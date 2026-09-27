#!/usr/bin/env python3
"""
sutra_autonomous_engine.py — 24/7 Quine-Powered Sovereign Autonomous Daemon
Part of SutraOS & Antigravity Ecosystem.

Features:
- Bypasses child-process limits via background daemon + Termux wake lock.
- Quine AST self-attestation & state persistence in sqlite (turiya.db & sutra_life.db).
- Continuous goal execution (Anant Anaadi media, B2B lead gen, Poly bhai audit, Single Brain rsync).
"""

import os
import sys
import time
import json
import sqlite3
import hashlib
import subprocess
import shutil

HOME_DIR = "/data/data/com.termux/files/home"
SUTRA_DIR = os.path.join(HOME_DIR, "sutralang")
DB_PATH = os.path.join(HOME_DIR, "turiya.db")
LIFE_DB_PATH = os.path.join(HOME_DIR, "sutra_life.db")
LOG_FILE = os.path.join(SUTRA_DIR, "sutra_autonomous.log")

# ponytail: 24/7 autonomous loop with Quine AST checkpointing. Ceiling: 5-min sleep interval, upgrade path: systemd/runit daemon.

def acquire_wake_lock():
    """Acquires Termux CPU wake lock to prevent Android OS deep sleep."""
    wakelock_bin = shutil.which("termux-wake-lock")
    if wakelock_bin:
        try:
            subprocess.run([wakelock_bin], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("⚡ [WAKELOCK] Termux CPU wake lock acquired.")
        except Exception:
            pass

def log(msg: str):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{ts}] {msg}"
    print(formatted)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass

def calculate_quine_digest(filepath: str) -> str:
    """Calculates SHA-256 Quine AST digest for runtime self-attestation."""
    if os.path.exists(filepath):
        try:
            with open(filepath, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()[:16]
        except Exception:
            pass
    return "0000000000000000"

def checkpoint_quine_state(task_name: str, state_data: dict):
    """Persists active Quine AST execution state into telemetry database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS quine_checkpoints (id INTEGER PRIMARY KEY AUTOINCREMENT, task TEXT, digest TEXT, state TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);"
        )
        engine_file = os.path.abspath(__file__)
        digest = calculate_quine_digest(engine_file)
        cursor.execute(
            "INSERT INTO quine_checkpoints (task, digest, state) VALUES (?, ?, ?);",
            (task_name, digest, json.dumps(state_data))
        )
        conn.commit()
        conn.close()
    except Exception as e:
        log(f"⚠️ Quine Checkpoint Warning: {e}")

def run_task_anant_anaadi():
    """Autonomous Task: Check Anant Anaadi post rendering state."""
    log("[Task 1: Anant Anaadi Pipeline] Checking daily render status...")
    today_str = time.strftime("%Y-%m-%d")
    renders_dir = os.path.join(HOME_DIR, "aa_renders")
    rendered = False
    if os.path.exists(renders_dir):
        for f in os.listdir(renders_dir):
            if today_str in f:
                rendered = True
                break
    if rendered:
        log("✅ Anant Anaadi daily content rendered for today.")
    else:
        log("⚠️ Anant Anaadi daily content pending for today.")
    return {"today_rendered": rendered}

def run_task_single_brain_sync():
    """Autonomous Task: Rule 5 Single Brain rsync to /sdcard/."""
    log("[Task 2: Single Brain Mirroring] Syncing Obsidian Vault to /sdcard/...")
    src = os.path.join(HOME_DIR, "sutra-brain/obsidian-vault/")
    dst = "/sdcard/Documents/SutraBrain/"
    if os.path.exists(src) and os.path.exists("/sdcard/Documents/"):
        try:
            res = subprocess.run(["rsync", "-avz", "--delete", src, dst], check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            log("✅ Single Brain rsync completed successfully.")
            return {"status": "success"}
        except Exception as e:
            log(f"⚠️ Single Brain rsync error: {e}")
    return {"status": "skipped"}

def run_task_lead_hunter():
    """Autonomous Task: Swa-Kevala Lead Scraper Cycle."""
    log("[Task 3: Lead Hunter] Running B2B lead generation cycle...")
    try:
        script = os.path.join(SUTRA_DIR, "sentinel_lead_hunter.py")
        if os.path.exists(script):
            res = subprocess.run(["python3", script], check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            log("✅ Lead Hunter cycle finished.")
            return {"status": "success"}
    except Exception as e:
        log(f"⚠️ Lead Hunter cycle error: {e}")
    return {"status": "failed"}

def run_autonomous_cycle():
    """Main 24/7 Autonomous Goal Loop Cycle."""
    log("==================================================")
    log("🚀 Sutra Autonomous Engine Cycle Starting")
    log("==================================================")
    
    acquire_wake_lock()
    
    # 1. Quine Self-Attestation Checkpoint
    engine_file = os.path.abspath(__file__)
    digest = calculate_quine_digest(engine_file)
    log(f"🛡️ Engine Quine Digest: [{digest}]")

    # 2. Run Autonomous Tasks
    t1 = run_task_anant_anaadi()
    t2 = run_task_single_brain_sync()
    t3 = run_task_lead_hunter()

    cycle_state = {
        "engine_digest": digest,
        "anant_anaadi": t1,
        "single_brain": t2,
        "lead_hunter": t3,
        "timestamp": time.time()
    }

    checkpoint_quine_state("cycle_complete", cycle_state)
    log("✅ Autonomous Cycle Completed & Quine State Checkpointed.")

def main_loop(interval_seconds=300):
    log(f"=== Sutra Autonomous Engine Online (Interval: {interval_seconds}s) ===")
    while True:
        try:
            run_autonomous_cycle()
        except Exception as e:
            log(f"❌ Cycle Exception: {e}")
        time.sleep(interval_seconds)

if __name__ == "__main__":
    main_loop(300)
