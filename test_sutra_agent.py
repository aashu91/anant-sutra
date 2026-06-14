# Automated Rigorous Test Suite for SutraAgent and C++ VM
import os
import sys
import json
import subprocess
import shutil

RULES_DIR = "./rules_db"
CATALOG_PATH = os.path.join(RULES_DIR, "catalog.json")

def cleanup_db():
    if os.path.exists(RULES_DIR):
        shutil.rmtree(RULES_DIR)
    os.makedirs(RULES_DIR, exist_ok=True)
    with open(CATALOG_PATH, 'w', encoding='utf-8') as f:
        json.dump({}, f)

def run_sutra_cli(args):
    cpp_vm = "./sutra"
    cmd = [cpp_vm] + args
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res

def test_basic_compile_and_run():
    print("Testing basic compile and run (C++ VM)...")
    # Test creation and print
    res = run_sutra_cli(["--run-line", "ek variable score value 100; print score"])
    assert res.returncode == 0, f"Failed: {res.stderr}"
    assert "'score' with Maan = 100" in res.stdout
    assert "➔ [DARSHANAM] 100" in res.stdout
    print("✓ Basic compile and run passed.")

def test_math_operations():
    print("Testing math operations (C++ VM)...")
    # Yog
    res = run_sutra_cli(["--run-line", "ek variable a value 0; a ko 10 aur 20 ka yog rkho; print a"])
    assert res.returncode == 0
    assert "➔ [DARSHANAM] 30" in res.stdout

    # Antar
    res = run_sutra_cli(["--run-line", "ek variable a value 0; a ko 50 aur 20 ka antar rkho; print a"])
    assert res.returncode == 0
    assert "➔ [DARSHANAM] 30" in res.stdout

    # Gunan
    res = run_sutra_cli(["--run-line", "ek variable a value 0; a ko 5 aur 6 ka gunan rkho; print a"])
    assert res.returncode == 0
    assert "➔ [DARSHANAM] 30" in res.stdout

    # Bhagaphalam
    res = run_sutra_cli(["--run-line", "ek variable a value 0; a ko 60 aur 2 ka bhagaphalam rkho; print a"])
    assert res.returncode == 0
    assert "➔ [DARSHANAM] 30" in res.stdout
    print("✓ Math operations passed.")

def test_division_by_zero():
    print("Testing division by zero protection...")
    # Bhagaphalam division by zero
    res = run_sutra_cli(["--run-line", "ek variable a value 0; a ko 60 aur 0 ka bhagaphalam rkho; print a"])
    assert res.returncode != 0
    assert "Division by zero" in res.stderr

    # Inline division by zero
    res = run_sutra_cli(["--run-line", "ek variable a value 10; a ko 0 se bhag do; print a"])
    assert res.returncode != 0
    assert "Division by zero" in res.stderr
    print("✓ Division by zero protection passed.")

def test_conditionals():
    print("Testing conditionals (Sankalpa)...")
    # Equal to condition (true)
    res = run_sutra_cli(["--run-line", "ek variable x value 10; agar x 10 ke barabar ho; print \"match\"; sankalpa khatam"])
    assert res.returncode == 0
    assert "➔ [DARSHANAM] match" in res.stdout

    # Equal to condition (false)
    res = run_sutra_cli(["--run-line", "ek variable x value 10; agar x 20 ke barabar ho; print \"match\"; sankalpa khatam"])
    assert res.returncode == 0
    assert "➔ [DARSHANAM] match" not in res.stdout

    # Greater than condition
    res = run_sutra_cli(["--run-line", "ek variable x value 15; agar x 10 se bada ho; print \"greater\"; sankalpa khatam"])
    assert res.returncode == 0
    assert "➔ [DARSHANAM] greater" in res.stdout
    print("✓ Conditionals passed.")

def test_loops():
    print("Testing loops (Pravahanam)...")
    res = run_sutra_cli(["--run-line", "ek variable counter value 0; ek variable i value 0; loop chalao jab tak i 5 se chota; counter ko 2 se badhao; i ko 1 se badhao; loop khatam; print counter"])
    assert res.returncode == 0
    assert "➔ [DARSHANAM] 10" in res.stdout
    print("✓ Loops passed.")

def test_agent_registry():
    print("Testing SutraAgent self-learning registry...")
    cleanup_db()
    
    # Teach rule using sutra_agent API helper (indirectly via register_rule)
    from sutra_agent import register_rule, run_bytecode
    
    # Teach a greetings rule
    success = register_rule("greet_test", "Test Greeting Rule", "ek variable name value \"Aashu\"; print name")
    assert success
    
    # Check compiled sutrab exists
    bytecode_path = os.path.join(RULES_DIR, "greet_test.sutrab")
    assert os.path.exists(bytecode_path)
    
    # Check catalog entry
    with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    assert "greet_test" in catalog
    assert catalog["greet_test"]["description"] == "Test Greeting Rule"
    
    # Execute the rule via agent
    # Capturing stdout of run_bytecode
    import io
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout
    try:
        run_bytecode(bytecode_path)
    finally:
        sys.stdout = old_stdout
        
    output = new_stdout.getvalue()
    assert "➔ [DARSHANAM] Aashu" in output
    print("✓ SutraAgent self-learning registry passed.")

def main():
    print("==========================================")
    print("    SUTRAAGENT AUTOMATED TEST SUITE       ")
    print("==========================================")
    
    try:
        test_basic_compile_and_run()
        test_math_operations()
        test_division_by_zero()
        test_conditionals()
        test_loops()
        test_agent_registry()
        
        print("\nALL TESTS COMPLETED SUCCESSFULLY! ZERO GLITCHES DETECTED.")
    except AssertionError as e:
        print(f"\nTEST FAILURE: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUNEXPECTED EXCEPTION DURING TESTS: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
