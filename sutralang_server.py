# sutralang_server.py — Local HTTP Web Gateway & REPL Portal for SutraAgent
# Copyright (c) 2026 Ashutosh Singh (salvationfinder / Anant Anaadi Group)
# Distributed under the MIT License. See LICENSE for details.
import http.server
import socketserver
import json
import subprocess
import os
import sys

# Ensure script directory is in path before importing local modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sutra_chain
from sutra_os import ExpanderScheduler, NyayaPageTable

# ponytail: Cleaned up redundant imports (urllib, re, PdfReader, SutraCompiler, SutraVM, and core tool helper functions)
# since server delegates AST compilation and VM execution to sutra_agent_core directly.
from sutra_agent_core import (
    SutraAgentCompiler, SutraAgentVM as SutraAgentCoreVM,
    query_ollama
)

PORT = 8000
DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")

# Global OS simulation instances
scheduler = ExpanderScheduler()
page_table = NyayaPageTable()

# Seed with some initial tasks
scheduler.add_task("VyakaranaVM")
scheduler.add_task("PostizPublisher")
scheduler.add_task("PolyBhaiTrading")


# Custom SutraAgentVM subclass for Server to capture logs for API response
class SutraAgentVM(SutraAgentCoreVM):
    def __init__(self):
        super().__init__()
        self.logs = []
        self.trace = []

    def log(self, text):
        super().log(text)
        self.logs.append(text)

    def execute(self, ast_program):
        import copy
        for step in ast_program:
            kriya = step.get("Kriya")
            if not kriya:
                continue
            
            log_start_idx = len(self.logs)
            
            method_name = f"kriya_{kriya.lower()}"
            if hasattr(self, method_name):
                getattr(self, method_name)(step)
            else:
                super().execute([step])
                
            step_logs = self.logs[log_start_idx:]
            self.trace.append({
                "instruction": step,
                "registry": copy.deepcopy(self.karta_registry),
                "logs": step_logs
            })

    def kriya_darshanam(self, step):
        karma = step.get("Karma")
        # Resolve reference or literal
        if karma in self.karta_registry:
            val = str(self.karta_registry[karma])
        else:
            val = str(karma)
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
        self.log(f"➔ [DARSHANAM OUTPUT] {val}")




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
        elif self.path == "/api/chain/status":
            st = sutra_chain.load_state()
            peers = sutra_chain.load_peers()
            data = {
                "chain_length": st.get("chain_length", 0),
                "last_block_hash": st.get("last_block_hash", ""),
                "peers": peers,
                "satya_points": st.get("satya_points", {})
            }
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode('utf-8'))
        elif self.path == "/api/chain/blocks":
            blocks = sutra_chain.get_chain_json()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(blocks).encode('utf-8'))
        elif self.path.startswith("/api/chain/block/"):
            try:
                parts = self.path.split("/")
                idx = int(parts[-1])
                _, sutrab_path = sutra_chain.get_block_paths(idx)
                if os.path.exists(sutrab_path):
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/octet-stream')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    with open(sutrab_path, 'rb') as f:
                        self.wfile.write(f.read())
                else:
                    self.send_error(404, "Block not found")
            except Exception as e:
                self.send_error(500, str(e))
        elif self.path.startswith("/api/chain/block_src/"):
            try:
                parts = self.path.split("/")
                idx = int(parts[-1])
                sutra_path, _ = sutra_chain.get_block_paths(idx)
                if os.path.exists(sutra_path):
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/plain')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    with open(sutra_path, 'r', encoding='utf-8') as f:
                        self.wfile.write(f.read().encode('utf-8'))
                else:
                    self.send_error(404, "Block source not found")
            except Exception as e:
                self.send_error(500, str(e))
        elif self.path == "/api/turiya/posts":
            turiya_json = "/data/data/com.termux/files/home/sutralang/turiya_content.json"
            if os.path.exists(turiya_json):
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                with open(turiya_json, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "Turiya content not found")
        elif self.path.startswith("/api/turiya/slide/"):
            try:
                # Format: /api/turiya/slide/YYYY-MM-DD/post_idx/slide_num
                parts = self.path.split("/")
                date_str = parts[4]
                post_idx = parts[5]
                slide_num = parts[6]
                
                # Check for extension and strip it if present
                if slide_num.endswith(".png"):
                    slide_num = slide_num[:-4]
                
                slide_path = f"/sdcard/Download/TURIYA_FACTORY/{date_str}_post_{post_idx}/slide_{slide_num}.png"
                if os.path.exists(slide_path):
                    self.send_response(200)
                    self.send_header('Content-Type', 'image/png')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    with open(slide_path, 'rb') as f:
                        self.wfile.write(f.read())
                else:
                    self.send_error(404, f"Slide file not found at {slide_path}")
            except Exception as e:
                self.send_error(500, str(e))
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/chain/mine":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                x = int(data.get("x", 0))
                y = int(data.get("y", 0))
                z = int(data.get("z", 0))
                status = data.get("status", "unverified")
                claim = data.get("claim", "")
                proof = data.get("proof", "")
                contributor = data.get("contributor", "operator")
                
                success, block_hash = sutra_chain.mine_block(x, y, z, status, claim, proof, contributor)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": success,
                    "hash": block_hash
                }).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))
        elif self.path == "/api/turiya/render":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                date_str = data.get("date", "2026-07-22")
                
                import subprocess
                res = subprocess.run(
                    [sys.executable, "/sdcard/Download/turiya_factory.py", date_str],
                    capture_output=True, text=True
                )
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": res.returncode == 0,
                    "stdout": res.stdout,
                    "stderr": res.stderr
                }).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))
        elif self.path == "/api/chain/sync":
            try:
                synced = sutra_chain.sync_with_peers()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": True,
                    "synced_blocks": synced
                }).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))
        elif self.path == "/api/chat":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                prompt = data.get("prompt", "")
                
                print(f"[API Chat] Query: '{prompt}'")
                sutra_code = query_ollama(prompt)
                if not sutra_code:
                    self.send_error_response("Could not compile query via Ollama. Make sure Ollama server is running.")
                    return
                
                # Strip markdown code blocks if the model wrapped output
                sutra_lines = []
                for line in sutra_code.split("\n"):
                    line_strip = line.strip()
                    if line_strip.startswith("```") or line_strip.endswith("```"):
                        continue
                    if line_strip:
                        sutra_lines.append(line_strip)
                sutra_clean_code = "\n".join(sutra_lines)

                compiler = SutraAgentCompiler()
                vm = SutraAgentVM()
                
                ast_json = []
                success = False
                error_msg = ""
                
                try:
                    ast_json = compiler.compile_program(sutra_clean_code)
                    vm.execute(ast_json)
                    success = True
                except Exception as e:
                    error_msg = str(e)
                    print(f"[API Chat] Execution Error: {error_msg}")

                # Extract Darshanam outputs for the final user response
                darshanam_outputs = []
                for log_line in vm.logs:
                    if "➔ [DARSHANAM OUTPUT]" in log_line:
                        darshanam_outputs.append(log_line.replace("➔ [DARSHANAM OUTPUT]", "").strip())
                
                final_response = "\n".join(darshanam_outputs) if darshanam_outputs else "Execution completed, but no outputs were printed."
                
                response_data = {
                    "success": success,
                    "sutra_code": sutra_clean_code,
                    "ast": ast_json,
                    "vm_logs": vm.logs,
                    "trace": vm.trace,
                    "response": final_response,
                    "error": error_msg
                }
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
                
            except Exception as e:
                self.send_error_response(str(e))

        elif self.path == "/api/run":
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
                
                if mode == "vibe":
                    cpp_vm_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sutra")
                    try:
                        res = subprocess.run([cpp_vm_path, "--translate-line", prompt], capture_output=True, text=True, timeout=5)
                        if res.returncode != 0:
                            raise Exception(res.stderr.strip())
                        translated_code = res.stdout.strip()
                    except Exception as e:
                        self.send_error_response(f"Translation failed: {e}")
                        return
                else:
                    translated_code = prompt

                # Compile AST
                compiler = SutraAgentCompiler()
                vm = SutraAgentVM()
                try:
                    ast_json = compiler.compile_program(translated_code)
                    vm.execute(ast_json)
                    stdout_output = "\n".join(vm.logs)
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
                
                # Compile to binary bytecode (.sutrab) using C++ compiler if available
                cpp_vm_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sutra")
                if os.path.exists(cpp_vm_path):
                    bytecode_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_web.sutrab")
                    try:
                        res_compile = subprocess.run([cpp_vm_path, "--compile-line", translated_code, bytecode_path], capture_output=True, text=True, timeout=5)
                        if res_compile.returncode == 0:
                            with open(bytecode_path, "rb") as f:
                                bytecode_bytes = f.read()
                            bytecode_hex = bytecode_bytes.hex()
                    except Exception:
                        pass

                response_data = {
                    "success": error_msg == "",
                    "translated": translated_code,
                    "ast": ast_json,
                    "bytecode": bytecode_hex,
                    "stdout": stdout_output,
                    "trace": vm.trace,
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
        print(f"\033[92m  SUTRAAGENT CHATBOT PORTAL SERVING ON PORT {PORT}    \033[0m")
        print(f"\033[92m  Open in browser: http://localhost:{PORT}          \033[0m")
        print(f"\033[92m====================================================\033[0m")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
