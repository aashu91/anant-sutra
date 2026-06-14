import http.server
import socketserver
import json
import subprocess
import os
import urllib.request
from sutralang_compiler import SutraCompiler
from sutralang_bytecode import compile_source_to_bytecode
from sutra_os import ExpanderScheduler, NyayaPageTable

PORT = 8000
DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")

# Global OS simulation instances
scheduler = ExpanderScheduler()
page_table = NyayaPageTable()

# Seed with some initial tasks
scheduler.add_task("VyakaranaVM")
scheduler.add_task("PostizPublisher")
scheduler.add_task("PolyBhaiTrading")

class SutraHubHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        if self.path == "/api/os/status":
            status_data = {
                "spectral_gap": scheduler.get_spectral_gap(),
                "load": scheduler.load,
                "cores": scheduler.cores,
                "history": scheduler.history,
                "allocations": page_table.allocations,
                "logs": page_table.logs
            }
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(status_data).encode('utf-8'))
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/run":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                mode = data.get("mode", "raw") # "raw" or "vibe"
                prompt = data.get("prompt", "")
                
                translated_code = ""
                ast_json = []
                bytecode_hex = ""
                stdout_output = ""
                error_msg = ""
                
                # Check mode
                if mode == "vibe":
                    # Call local Ollama LLM to translate (querying via sutralang_neuro compile_neuro_prompt)
                    import sutralang_neuro
                    try:
                        translated_code = sutralang_neuro.compile_neuro_prompt(prompt)
                    except Exception as e:
                        self.send_error_response(f"Translation failed: {e}")
                        return
                else:
                    translated_code = prompt

                # Compile AST using our compiler
                compiler = SutraCompiler()
                try:
                    ast_json = compiler.compile_program(translated_code)
                except Exception as e:
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "success": False,
                        "translated": translated_code,
                        "error": f"Syntax Compiler Error: {e}"
                    }).encode('utf-8'))
                    return
                
                # Compile to binary bytecode (.sutrab)
                try:
                    bytecode_bytes = compile_source_to_bytecode(translated_code)
                    bytecode_hex = bytecode_bytes.hex()
                    
                    # Write bytecode to temp file
                    bytecode_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_web.sutrab")
                    with open(bytecode_path, "wb") as f:
                        f.write(bytecode_bytes)
                except Exception as e:
                    self.send_error_response(f"Bytecode generation failed: {e}")
                    return

                # Execute natively via C++ VM executable ./sutra
                cpp_vm_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sutra")
                if not os.path.exists(cpp_vm_path):
                    # Compile sutralang.cpp if binary missing
                    cpp_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sutralang.cpp")
                    subprocess.run(["g++", "-O3", "-std=c++17", cpp_src, "-o", cpp_vm_path])
                
                try:
                    res = subprocess.run([cpp_vm_path, bytecode_path], capture_output=True, text=True, timeout=5)
                    stdout_output = res.stdout
                    if res.returncode != 0:
                        error_msg = res.stderr if res.stderr else "C++ VM execution failed."
                except subprocess.TimeoutExpired:
                    error_msg = "VM Execution Timeout (Possible infinite loop detected)."
                except Exception as e:
                    error_msg = f"C++ VM Spawn Error: {e}"

                response_data = {
                    "success": error_msg == "",
                    "translated": translated_code,
                    "ast": ast_json,
                    "bytecode": bytecode_hex,
                    "stdout": stdout_output,
                    "error": error_msg
                }

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
                
            except Exception as e:
                self.send_error_response(str(e))
                
        elif self.path == "/api/os/task/add":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                task_name = data.get("name", "UnnamedTask")
                core_assigned = scheduler.add_task(task_name)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "core": core_assigned}).encode('utf-8'))
            except Exception as e:
                self.send_error_response(str(e))
                
        elif self.path == "/api/os/tick":
            try:
                movements = scheduler.tick()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "movements": movements}).encode('utf-8'))
            except Exception as e:
                self.send_error_response(str(e))
                
        elif self.path == "/api/os/allocate":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                proc = data.get("process", "Anonymous")
                size = data.get("size", 0)
                limit = data.get("limit", 0)
                
                log_entry = page_table.allocate(proc, size, limit)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(log_entry).encode('utf-8'))
            except Exception as e:
                self.send_error_response(str(e))
        else:
            self.send_response(404)
            self.end_headers()

    def send_error_response(self, msg):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({
            "success": False,
            "error": msg
        }).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == "__main__":
    os.makedirs(DIRECTORY, exist_ok=True)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), SutraHubHandler) as httpd:
        print(f"\033[92m====================================================\033[0m")
        print(f"\033[92m  ANANT ANAADI R&D PORTAL SERVING ON PORT {PORT}      \033[0m")
        print(f"\033[92m  Open in browser: http://localhost:{PORT}          \033[0m")
        print(f"\033[92m====================================================\033[0m")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
