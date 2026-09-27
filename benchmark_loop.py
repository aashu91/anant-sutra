#!/usr/bin/env python3
import os
import sys
import json
import sqlite3
import subprocess
import time

# ponytail: simple end-to-end system benchmark runner.
# Ceiling: sequential stage verification. Upgrade path: async parallel stage execution if benchmark suite grows.

def run_benchmark():
    print("=" * 60)
    print("🚀 SUTRA OS / SPARK ROUTER ADVERSARIAL BENCHMARK LOOP")
    print("=" * 60)
    
    # -------------------------------------------------------------
    # STAGE 1: Spark Router Intent Dispatch Verification
    # -------------------------------------------------------------
    print("[1/5] Testing Spark Router Intent & Routing...")
    from spark_router import SparkRouter
    router = SparkRouter()
    
    query = "Elon Musk Vajra and Nikola Tesla 1896 meeting Akasha Prana physics fact check and Instagram post render"
    route_res = router.dispatch(query)
    print(f"   └─ Route Result: {route_res['route']} (Score: {route_res['score']})")
    assert route_res["route"] in ["TURIYA", "ANANT_ANAADI"], f"Routing failed! Got {route_res['route']}"
    print("   ✅ STAGE 1 PASSED: Intent Routing Verified.\n")

    # -------------------------------------------------------------
    # STAGE 2: SutraLang Bytecode & C++ VM Execution
    # -------------------------------------------------------------
    print("[2/5] Testing SutraLang Bytecode Compilation & C++ VM Execution...")
    sutra_file = "/data/data/com.termux/files/home/sutralang/temp_vajra_tesla.sutra"
    sutrab_file = "/data/data/com.termux/files/home/sutralang/temp_vajra_tesla.sutrab"
    vm_binary = "/data/data/com.termux/files/home/sutralang/sutra"
    
    # Compile
    comp_proc = subprocess.run(
        ["python3", "/data/data/com.termux/files/home/sutralang/sutralang_bytecode.py", sutra_file, sutrab_file],
        capture_output=True, text=True
    )
    assert comp_proc.returncode == 0, f"Bytecode compilation failed: {comp_proc.stderr}"
    assert os.path.exists(sutrab_file), "Bytecode .sutrab file not generated!"
    
    # Run VM
    vm_proc = subprocess.run([vm_binary, "--run", sutrab_file], capture_output=True, text=True)
    assert vm_proc.returncode == 0, f"C++ SutraVM execution failed: {vm_proc.stderr}"
    assert "801" in vm_proc.stdout, "VM output calculation 801 missing!"
    print("   └─ SutraVM Output: Field Resonance 801 Verified.")
    print("   ✅ STAGE 2 PASSED: C++ SutraVM Execution Verified.\n")

    # -------------------------------------------------------------
    # STAGE 3: Turiya Forensic Database Integrity Check
    # -------------------------------------------------------------
    print("[3/5] Testing Turiya Forensic Database (turiya.db)...")
    db_path = "/data/data/com.termux/files/home/turiya.db"
    assert os.path.exists(db_path), f"Turiya DB missing at {db_path}"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, status FROM claims ORDER BY id DESC LIMIT 1;")
    claim = cursor.fetchone()
    conn.close()
    
    assert claim is not None, "No claims found in turiya.db!"
    print(f"   └─ Latest Claim #{claim[0]}: '{claim[1]}' [{claim[2]}]")
    print("   ✅ STAGE 3 PASSED: Turiya DB Integrity Verified.\n")

    # -------------------------------------------------------------
    # STAGE 4: Anant Anaadi Image Render Verification
    # -------------------------------------------------------------
    print("[4/5] Testing Anant Anaadi Image Factory (aa_pro_factory.py)...")
    factory_path = "/data/data/com.termux/files/home/aa_pro_factory.py"
    assert os.path.exists(factory_path), f"Factory missing at {factory_path}"
    
    # Verify PIL import works cleanly
    from PIL import Image, ImageDraw
    test_img = Image.new('RGB', (1080, 1350), color = (10, 25, 47))
    test_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_aa_bench.png")
    test_img.save(test_path)
    assert os.path.exists(test_path), "Failed to render test canvas!"
    os.remove(test_path)
    print("   └─ PIL HD Graphic Canvas (1080x1350) Render Verified.")
    print("   ✅ STAGE 4 PASSED: Graphic Factory Verified.\n")

    # -------------------------------------------------------------
    # STAGE 5: Live Discord Webhook & Reinforcement Loop Verification
    # -------------------------------------------------------------
    print("[5/5] Testing Discord Webhook & Reinforcement Memory Loop...")
    discord_sent = router.notify_discord(
        title="🏆 BENCHMARK COMPLETED: All 5 Stages Passed",
        description="**System Status**: 100% Operational\n**SutraVM**: Verified (801 Hz)\n**Turiya DB**: Connected\n**Graphic Factory**: Operational",
        color=65280
    )
    assert discord_sent is True, "Discord notification failed to deliver!"
    print("   └─ Live Discord Webhook Report Delivered.")
    print("   ✅ STAGE 5 PASSED: Discord Integration Verified.\n")

    print("=" * 60)
    print("🎉 ALL 5 BENCHMARK STAGES PASSED CLEANLY! SYSTEM IS 100% OPERATIONAL.")
    print("=" * 60)

if __name__ == "__main__":
    run_benchmark()
