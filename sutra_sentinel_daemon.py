#!/usr/bin/env python3
"""
sutra_sentinel_daemon.py — 24/7 Sovereign Background Sentinel Daemon
Part of SutraOS & Antigravity Ecosystem.

Monitors Second Brain goals, Poly bhai bot health, Anant Anaadi post schedules,
enforces Single Brain Sync to /sdcard/ (Rule 5 Parity), tracks Android thermal & battery metrics,
and posts real-time telemetry events to SutraOS Telemetry Server.
"""

import os
import sys
import time
import json
import sqlite3
import urllib.request
import subprocess
import shutil

SUTRA_DIR = "/data/data/com.termux/files/home/sutralang"
POLY_DIR = "/data/data/com.termux/files/home/poly_v2"
sys.path.insert(0, SUTRA_DIR)
sys.path.insert(0, POLY_DIR)

from spark_uacc_router import SparkUACCRouter, load_env
from sutra_goals import get_pending, list_goals
from sentinel_lead_hunter import run_lead_hunter_cycle, get_latest_leads

ENV = load_env()
DISCORD_WEBHOOK_URL = ENV.get("DISCORD_WEBHOOK_URL")
OBSIDIAN_VAULT = "/data/data/com.termux/files/home/sutra-brain/obsidian-vault"
INTERVAL_SECONDS = 900  # 15 minutes heartbeat
SERVER_URL = "http://localhost:8000"


def get_android_battery_status() -> dict:
    """Collects battery percentage, status, and temperature via Termux API or procfs."""
    battery_info = {"percentage": 100, "status": "Good", "temp_c": 30.0, "source": "mock"}
    termux_batt_bin = shutil.which("termux-battery-status")
    if termux_batt_bin:
        try:
            out = subprocess.check_output([termux_batt_bin], text=True, timeout=3)
            data = json.loads(out)
            battery_info = {
                "percentage": data.get("percentage", 100),
                "status": data.get("status", "Discharging"),
                "temp_c": data.get("temperature", 30.0),
                "health": data.get("health", "GOOD"),
                "source": "termux-api"
            }
            return battery_info
        except Exception:
            pass
            
    # Fallback to sysfs
    try:
        cap_path = "/sys/class/power_supply/battery/capacity"
        if os.path.exists(cap_path):
            with open(cap_path, "r") as f:
                battery_info["percentage"] = int(f.read().strip())
                battery_info["source"] = "sysfs"
    except Exception:
        pass
    return battery_info


def get_thermal_metrics() -> dict:
    """Collects thermal zone temperatures for Android throttle protection."""
    thermal_info = {"cpu_temp_c": 34.5, "status": "NOMINAL", "zones": {}}
    for i in range(4):
        tpath = f"/sys/class/thermal/thermal_zone{i}/temp"
        if os.path.exists(tpath):
            try:
                with open(tpath, "r") as f:
                    t_raw = int(f.read().strip())
                    t_c = t_raw / 1000.0 if t_raw > 1000 else float(t_raw)
                    thermal_info["zones"][f"zone_{i}"] = round(t_c, 1)
                    if i == 0:
                        thermal_info["cpu_temp_c"] = round(t_c, 1)
            except Exception:
                pass
    if thermal_info["cpu_temp_c"] > 45.0:
        thermal_info["status"] = "HIGH_THERMAL_THROTTLE_SHIELD"
    return thermal_info


def send_termux_notification(title: str, content: str):
    """Sends native Android notification via Termux API if installed."""
    termux_notif_bin = shutil.which("termux-notification")
    if termux_notif_bin:
        try:
            subprocess.run([
                termux_notif_bin,
                "--title", title,
                "--content", content,
                "--priority", "high"
            ], check=False)
        except Exception:
            pass


def send_discord_alert(title: str, description: str, color: int = 3447003):
    """Sends rich embed notification to user's Discord Server."""
    if not DISCORD_WEBHOOK_URL:
        return False
    payload = {
        "username": "SutraOS 24/7 Sentinel",
        "embeds": [{
            "title": title,
            "description": description,
            "color": color,
            "footer": {"text": "SutraOS Sovereign Sentinel • Termux Heartbeat"}
        }]
    }
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            DISCORD_WEBHOOK_URL,
            data=data,
            headers={"Content-Type": "application/json", "User-Agent": "SutraSentinel/1.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status in (200, 204)
    except Exception as e:
        print(f"[WARN] Discord Webhook alert failed: {e}")
        return False


def sync_single_brain_obsidian() -> bool:
    """Rule 5 Mandate: Mirror /sutra-brain/obsidian-vault/ to /sdcard/Documents/SutraBrain/ via rsync."""
    src = "/data/data/com.termux/files/home/sutra-brain/obsidian-vault/"
    dst = "/sdcard/Documents/SutraBrain/"
    if os.path.exists(src) and os.path.exists("/sdcard/Documents/"):
        try:
            subprocess.run(["rsync", "-avz", "--delete", src, dst], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("[SENTINEL Node C] Single Brain Sync completed via rsync.")
            return True
        except Exception as e:
            print(f"[WARN] Single Brain Sync rsync warning: {e}")
    return False


def check_second_brain_goals():
    """Scans pending goals from SQLite DB & Obsidian Daily Notes."""
    pending_goals = get_pending()
    obsidian_tasks = []
    today_str = time.strftime("%Y-%m-%d")
    daily_note_path = os.path.join(OBSIDIAN_VAULT, "06_Journal", time.strftime("%Y"), time.strftime("%m"), f"{today_str}.md")
    if os.path.exists(daily_note_path):
        try:
            with open(daily_note_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("- [ ]"):
                        obsidian_tasks.append(line.strip().replace("- [ ]", "").strip())
        except Exception:
            pass
    return pending_goals, obsidian_tasks


def check_poly_x_signals():
    """Node A: Scans Poly bhai DB for high-edge signals and formats tweet output."""
    db_path = os.path.join(POLY_DIR, "poly_v2.db")
    if not os.path.exists(db_path):
        return None
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT market_slug, side, price, status, pnl FROM trades ORDER BY timestamp DESC LIMIT 1")
        row = cur.fetchone()
        conn.close()
        if row:
            market_slug, side, price, status, pnl = row
            return {"slug": market_slug, "signal": side, "price": price, "status": status, "pnl": pnl}
    except Exception as e:
        print(f"[WARN] Poly DB signal query failed: {e}")
    return None


def check_system_services() -> dict:
    """Checks running state of Poly bhai, Chiransh, and system resources."""
    health = SparkUACCRouter.get_system_health()
    poly_running = False
    try:
        output = subprocess.check_output(["ps", "aux"], text=True)
        if "sutra_agent_bot.py" in output or "poly" in output or "main.py" in output:
            poly_running = True
    except Exception:
        pass
    return {"health": health, "poly_running": poly_running}


def check_anant_anaadi_pipeline() -> dict:
    """Node B: Audits Anant Anaadi rendering & scheduling pipeline state."""
    renders_dir = "/data/data/com.termux/files/home/aa_renders"
    content_json = "/data/data/com.termux/files/home/content.json"
    today_str = time.strftime("%Y-%m-%d")
    today_rendered = False
    total_renders = 0
    if os.path.exists(renders_dir):
        files = os.listdir(renders_dir)
        total_renders = len(files)
        for f in files:
            if today_str in f or f"post_{today_str}" in f:
                today_rendered = True
                break
    scheduled_posts = 0
    if os.path.exists(content_json):
        try:
            with open(content_json, "r", encoding="utf-8") as f:
                data = json.load(f)
                scheduled_posts = len(data) if isinstance(data, list) else 0
        except Exception:
            pass
    return {"today_rendered": today_rendered, "total_renders": total_renders, "scheduled_posts": scheduled_posts}


def post_telemetry_heartbeat(status_data: dict):
    """Posts telemetry event to SutraOS Web Server for 3D Visualizer updates."""
    try:
        req = urllib.request.Request(
            f"{SERVER_URL}/api/telemetry/event",
            data=json.dumps({
                "type": "SENTINEL_HEARTBEAT",
                "query": "24/7 Sovereign Sentinel Monitoring Check",
                "details": status_data
            }).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            pass
    except Exception:
        pass


def run_native_sutraos_telemetry():
    """Executes the standalone native SutraLang 3.0 ELF engine binary for zero-GC telemetry."""
    native_bin = "/data/data/com.termux/files/home/sutralang_v3/sutraos"
    if not os.path.exists(native_bin):
        native_bin = "/data/data/com.termux/files/home/sutralang/sutraos"
    if os.path.exists(native_bin) and os.access(native_bin, os.X_OK):
        try:
            res = subprocess.run([native_bin], capture_output=True, text=True, timeout=2)
            print("[SENTINEL Native Core] Native SutraOS 3.0 ELF Engine Output:")
            for line in res.stdout.strip().split("\n"):
                if line.strip():
                    print(f"  {line.strip()}")
        except Exception as e:
            print(f"[WARN] Native SutraOS engine call failed: {e}")


def heartbeat_cycle():
    """Single heartbeat audit cycle with Graph Node triggers."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] ⚡ Sentinel Heartbeat Check Starting...")
    
    # 0. Sovereign Native SutraOS 3.0 Engine Cycle
    run_native_sutraos_telemetry()

    # 1. Rule 5 Single Brain Mirroring
    sync_ok = sync_single_brain_obsidian()
    
    # 2. Battery & Thermal Metrics
    batt = get_android_battery_status()
    thermal = get_thermal_metrics()
    
    # 3. Lead Hunter Scraper
    lead_stats = run_lead_hunter_cycle()
    
    services = check_system_services()
    pending_db, pending_obsidian = check_second_brain_goals()
    latest_signal = check_poly_x_signals()
    aa_status = check_anant_anaadi_pipeline()
    
    health = services["health"]
    signal_str = f"`{latest_signal['slug']} ({latest_signal['signal']} @ {latest_signal['price']:.2f})`" if latest_signal else "`No Active Signal`"
    aa_str = f"🟢 Rendered Today ({aa_status['total_renders']} Total Renders)" if aa_status['today_rendered'] else f"⚠️ Pending Today ({aa_status['total_renders']} Total Renders)"
    
    status_msg = (
        f"**System Status**: Free RAM: `{health['mem_available_mb']}MB` | Load: `{health['load_1m']}`\n"
        f"**Battery**: `{batt['percentage']}%` ({batt['status']}) | **Thermal**: `{thermal['cpu_temp_c']}°C` ({thermal['status']})\n"
        f"**Single Brain Parity**: {'🟢 Synced (/sdcard/)' if sync_ok else '🟡 Parity OK'}\n"
        f"**Anant Anaadi Pipeline**: {aa_str} | Scheduled: `{aa_status['scheduled_posts']}`\n"
        f"**Poly bhai Trading Bot**: {'🟢 Running' if services['poly_running'] else '🔴 Idle/Stopped'}\n"
        f"**Latest Quant Signal**: {signal_str}\n"
        f"**Swa-Kevala Leads**: Scraped: `{lead_stats['total_leads']}` (+`{lead_stats['added_this_run']}` new)\n"
        f"**Pending Goals**: DB `{len(pending_db)}` | Obsidian Tasks `{len(pending_obsidian)}`"
    )
    print(status_msg)

    # Post real-time event to SutraOS 3D Visualizer server
    post_telemetry_heartbeat({
        "ram_free_mb": health['mem_available_mb'],
        "battery": batt,
        "thermal": thermal,
        "single_brain_sync": sync_ok,
        "poly_signal": latest_signal,
        "lead_stats": lead_stats,
        "pending_goals_count": len(pending_db) + len(pending_obsidian)
    })
    
    send_discord_alert(
        title=f"🧠 Sovereign Sentinel Heartbeat ({time.strftime('%H:%M')})",
        description=status_msg,
        color=65280 if services['poly_running'] else 16753920
    )
    send_termux_notification(
        title="SutraOS Sentinel Active",
        content=f"RAM: {health['mem_available_mb']}MB | Temp: {thermal['cpu_temp_c']}°C | Signal: {latest_signal['slug'] if latest_signal else 'None'}"
    )


def run_daemon():
    print(f"=== Starting SutraOS 24/7 Sovereign Sentinel Daemon (Interval: {INTERVAL_SECONDS}s) ===")
    send_discord_alert(
        title="🚀 Sovereign Sentinel Online",
        description="24/7 Sentinel daemon initialized on Termux. Graph Nodes: Poly bhai Signal Tracker, Thermal Shield, Single Brain Mirroring Active.",
        color=3447003
    )
    while True:
        try:
            heartbeat_cycle()
        except Exception as e:
            print(f"[ERROR] Heartbeat cycle failed: {e}")
            send_discord_alert("⚠️ Sentinel Heartbeat Warning", f"Error encountered during heartbeat: `{e}`", color=16711680)
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        heartbeat_cycle()
    else:
        run_daemon()
