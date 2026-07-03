import os
import sys
import json
import time
import urllib.request
import urllib.parse

# Import Sutra compiler and VM
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from sutralang_server import SutraAgentCompiler, SutraAgentVM, query_ollama, is_command_safe

TEST_CASES = [
    {
        "name": "Direct Conversation",
        "prompt": "Hello! Who are you?",
        "expected_ast_kriyas": ["Darshanam"],
        "direct_sutra": 'ek variable reply value "Namaste! Main tumhara local sovereign AI chatbot hoon."\nprint reply',
        "run_live": True
    },
    {
        "name": "Web Search Query",
        "prompt": "Search on the web for Polymarket news and print it.",
        "expected_ast_kriyas": ["Khaj", "Darshanam"],
        "direct_sutra": 'ek variable query value "Polymarket news"\nek variable search_res value ""\nsearch_res ko query se khojo\nprint search_res',
        "run_live": True
    },
    {
        "name": "Local Codebase Search",
        "prompt": "Search local codebase for SutraAgentVM and show it.",
        "expected_ast_kriyas": ["Chhav", "Darshanam"],
        "direct_sutra": 'ek variable query value "SutraAgentVM"\nek variable code_res value ""\ncode_res ko query se chhavo\nprint code_res',
        "run_live": True
    },
    {
        "name": "PDF Read Context",
        "prompt": "Read page details from report.pdf about standard revenue and show it.",
        "expected_ast_kriyas": ["Path", "Darshanam"],
        "direct_sutra": 'ek variable file value "report.pdf"\nek variable query value "standard revenue"\nek variable details value ""\ndetails ko file aur query se padho\nprint details',
        "run_live": False
    },
    {
        "name": "Shell Python Exec",
        "prompt": "Run a python command to calculate the factorial of 5 and show result.",
        "expected_ast_kriyas": ["Shodh", "Darshanam"],
        "direct_sutra": 'ek variable cmd value "python -c \'import math; print(math.factorial(5))\'"\nek variable res value ""\nres ko cmd se shodh_karo\nprint res',
        "run_live": False
    },
    {
        "name": "Security Violation - Outside Path Write",
        "prompt": "Run shell command to write results to /etc/passwd",
        "direct_sutra": 'ek variable cmd value "echo hello > /etc/passwd"\nek variable res value ""\nres ko cmd se shodh_karo\nprint res',
        "should_fail_security": True,
        "expected_security_error": "Access to path outside home directory is forbidden",
        "run_live": False
    },
    {
        "name": "Security Violation - Sudo command",
        "prompt": "Run sudo rm -rf /data/data/com.termux/files/home",
        "direct_sutra": 'ek variable cmd value "sudo rm -rf /data/data/com.termux/files/home"\nek variable res value ""\nres ko cmd se shodh_karo\nprint res',
        "should_fail_security": True,
        "expected_security_error": "Forbidden command token/prefix",
        "run_live": False
    },
    {
        "name": "Security Violation - Path Traversal",
        "prompt": "Run shell to read ../../some_file",
        "direct_sutra": 'ek variable cmd value "cat ../../some_file"\nek variable res value ""\nres ko cmd se shodh_karo\nprint res',
        "should_fail_security": True,
        "expected_security_error": "Directory traversal",
        "run_live": False
    },
    {
        "name": "String Joining",
        "prompt": "Join Namaste and World and show it.",
        "expected_ast_kriyas": ["Sandh", "Darshanam"],
        "direct_sutra": 'ek variable v1 value "Namaste"\nek variable v2 value "World"\nek variable message value ""\nmessage ko v1 aur v2 se jodo\nprint message',
        "run_live": False
    },
    {
        "name": "Multi-step local search & print",
        "prompt": "Search local codebase for sutralang_server.py and print results.",
        "expected_ast_kriyas": ["Chhav", "Darshanam"],
        "direct_sutra": 'ek variable query value "sutralang_server.py"\nek variable search_res value ""\nsearch_res ko query se chhavo\nprint search_res',
        "run_live": False
    }
]

def run_backtests():
    print("====================================================")
    print("         SUTRALANG VM AUTOMATED BACKTESTING         ")
    print("====================================================")
    
    compiler = SutraAgentCompiler()
    results = []
    
    # Check if local Ollama server is responsive
    ollama_active = False
    try:
        req = urllib.request.Request("http://localhost:11434/")
        with urllib.request.urlopen(req, timeout=3) as resp:
            if resp.status == 200:
                ollama_active = True
                print("[Backtest] Local Ollama server is ACTIVE. Running live translation for selected cases.")
    except Exception:
        print("[Backtest] Local Ollama server is COLD/OFFLINE. Skipping live translation, using static script test lane.")
        
    for tc in TEST_CASES:
        print(f"\n[Test Case] {tc['name']}")
        start_time = time.time()
        
        # Lane 1: Live LLM Translation (only if Ollama is active and marked for live run)
        live_sutra = None
        translation_time = 0
        if ollama_active and tc.get("run_live", False):
            print(f"  -> Sending prompt to Ollama: '{tc['prompt']}'")
            t_start = time.time()
            live_sutra = query_ollama(tc['prompt'])
            translation_time = time.time() - t_start
            if live_sutra:
                print(f"  -> Live compiled SutraLang:\n{live_sutra}")
            else:
                print("  -> Live compilation failed. Falling back to static script.")
                
        # Lane 2: Compilation & Execution using either live or static script
        sutra_to_run = live_sutra if live_sutra else tc["direct_sutra"]
        compile_success = False
        exec_success = False
        error_msg = ""
        vm_logs = []
        ast = None
        
        try:
            # Compile to AST
            ast = compiler.compile_program(sutra_to_run)
            compile_success = True
            
            # Execute in VM
            vm = SutraAgentVM()
            vm.execute(ast)
            vm_logs = vm.logs
            exec_success = True
        except Exception as e:
            error_msg = str(e)
            print(f"  -> Execution status/error: {error_msg}")
            
        latency = time.time() - start_time
        
        # Verify safety check if security failure is expected
        security_passed = True
        if tc.get("should_fail_security"):
            joined_logs = "\n".join(vm_logs)
            expected_err = tc["expected_security_error"]
            if expected_err.lower() in joined_logs.lower() or expected_err.lower() in error_msg.lower():
                print(f"  -> [PASS] Security constraint triggered correctly: '{expected_err}'")
                security_passed = True
            else:
                print(f"  -> [FAIL] Security constraint missed or wrong message. Logs:\n{joined_logs}")
                security_passed = False
                
        # Verify AST matches expected Kriyas
        ast_passed = True
        if ast and "expected_ast_kriyas" in tc:
            actual_kriyas = [step.get("Kriya") for step in ast if step.get("Kriya")]
            for expected in tc["expected_ast_kriyas"]:
                if expected not in actual_kriyas:
                    print(f"  -> [FAIL] AST Kriya missing: Expected '{expected}', got {actual_kriyas}")
                    ast_passed = False
                    
        passed = compile_success and (exec_success or tc.get("should_fail_security")) and security_passed and ast_passed
        status_text = "PASS" if passed else "FAIL"
        print(f"  -> Status: {status_text} (Latency: {latency:.3f}s)")
        
        results.append({
            "name": tc["name"],
            "prompt": tc["prompt"],
            "sutra_code": sutra_to_run,
            "compiled_ast": ast,
            "passed": passed,
            "compile_success": compile_success,
            "exec_success": exec_success,
            "security_passed": security_passed,
            "ast_passed": ast_passed,
            "latency_seconds": latency,
            "translation_time_seconds": translation_time,
            "vm_logs": vm_logs,
            "error": error_msg
        })
        
    # Write report
    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backtest_results.json")
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n====================================================")
    print(f"Backtesting finished. Results saved to:\n  {report_path}")
    print("====================================================")

if __name__ == '__main__':
    run_backtests()
