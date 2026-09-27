#!/usr/bin/env python3
"""
continuous_lead_orchestrator.py — Master Orchestrator for High-Volume Web3 & MCP Lead Harvesting
Runs multi-threaded lead scraping engines in a continuous loop across:
- GitHub API, Repos, Push Events, Commit Logs & Users
- Dev.to Articles & Profiles
- HackerNews Forums & Comments
- X (Twitter) Bios & Posts
- LinkedIn Public Profiles
- Reddit Developer Threads
- Instagram & Facebook Profiles
- Telegram & Discord Public Communities

Saves leads into SQLite DB (/data/data/com.termux/files/home/sutralang/mcp_leads.db),
maintains 100% deduplication, and triggers pre-rendered HTML dashboard updates.
Loops until 10,000 verified emails are reached.
"""

import os
import sys
import time
import sqlite3
import datetime
import subprocess

DB_PATH = "/data/data/com.termux/files/home/sutralang/mcp_leads.db"
GEN_SCRIPT = "/data/data/com.termux/files/home/generate_leads_dashboard.py"
CONTRIB_SCRIPT = "/data/data/com.termux/files/home/sutralang/harvest_web3_mcp_contributors.py"
SOCIAL_SCRIPT = "/data/data/com.termux/files/home/sutralang/ultra_social_lead_harvester.py"
SCRAPER_SCRIPT = "/data/data/com.termux/files/home/sutralang/mcp_trading_lead_scraper.py"

TARGET_VERIFIED_EMAILS = 10000

def get_lead_stats():
    if not os.path.exists(DB_PATH):
        return {"total_leads": 0, "verified_emails": 0, "by_source": {}}
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*), COUNT(DISTINCT email) FROM mcp_leads WHERE email IS NOT NULL AND email != ''")
        row = cur.fetchone()
        total_leads, verified_emails = row[0], row[1]

        cur.execute("SELECT source, COUNT(DISTINCT email) FROM mcp_leads WHERE email IS NOT NULL AND email != '' GROUP BY source")
        by_source = dict(cur.fetchall())
        conn.close()
        return {
            "total_leads": total_leads,
            "verified_emails": verified_emails,
            "by_source": by_source
        }
    except Exception as e:
        print(f"[ERR] Failed to read DB stats: {e}")
        return {"total_leads": 0, "verified_emails": 0, "by_source": {}}

def trigger_dashboard_update():
    try:
        res = subprocess.run(["python3", GEN_SCRIPT], capture_output=True, text=True, timeout=30)
        if res.returncode == 0:
            print("  📊 [DASHBOARD UPDATED] Pre-rendered HTML dashboard regenerated successfully.")
        else:
            print(f"  [WARN] Dashboard generation error: {res.stderr}")
    except Exception as e:
        print(f"  [WARN] Could not trigger dashboard update: {e}")

def run_script_safe(script_cmd, name):
    print(f"\n==================================================================")
    print(f"⚡ Launching Engine: {name}")
    print(f"   Command: {' '.join(script_cmd)}")
    print(f"==================================================================")
    try:
        env = dict(os.environ)
        env["PYTHONUNBUFFERED"] = "1"
        proc = subprocess.Popen(script_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, env=env)
        for line in iter(proc.stdout.readline, ''):
            if line:
                print(f"[{name}] {line.strip()}", flush=True)
        proc.wait()
        print(f"[+] Engine {name} completed batch with returncode: {proc.returncode}", flush=True)
    except Exception as e:
        print(f"[ERR] Error executing engine {name}: {e}", flush=True)

def main():
    print("==================================================================", flush=True)
    print("🚀 SWA-KEVALA OS MASTER LEAD HARVESTING ORCHESTRATOR STARTED", flush=True)
    print(f"   Target Verified Emails: {TARGET_VERIFIED_EMAILS:,}", flush=True)
    print(f"   DB Path: {DB_PATH}", flush=True)
    print("==================================================================", flush=True)

    cycle = 1
    while True:
        stats = get_lead_stats()
        current_emails = stats["verified_emails"]
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"\n[{now_str}] 📈 CYCLE #{cycle} START | Current Verified Emails: {current_emails:,} / {TARGET_VERIFIED_EMAILS:,} ({current_emails/TARGET_VERIFIED_EMAILS*100:.1f}%)", flush=True)

        if current_emails >= TARGET_VERIFIED_EMAILS:
            print(f"\n🎉 [MILESTONE REACHED] Successfully collected {current_emails:,} verified emails! Stopping orchestrator.", flush=True)
            trigger_dashboard_update()
            break

        # Step 1: Run GitHub Contributor & Events Harvester
        start_emails = current_emails
        run_script_safe(["python3", "-u", CONTRIB_SCRIPT], "GH_EVENTS_CONTRIB")
        
        mid_stats = get_lead_stats()
        print(f"  --> Gained {mid_stats['verified_emails'] - start_emails} verified emails from GitHub Contributor & Events Harvester.", flush=True)

        if mid_stats["verified_emails"] >= TARGET_VERIFIED_EMAILS:
            print(f"\n🎉 [MILESTONE REACHED] Reached target! Total: {mid_stats['verified_emails']:,}", flush=True)
            trigger_dashboard_update()
            break

        # Step 2: Run Ultra Social Dork Harvester (X, IG, FB, LinkedIn, Reddit, Dev.to, HN, Telegram, Discord, Events)
        start_emails = mid_stats["verified_emails"]
        run_script_safe(["python3", "-u", SOCIAL_SCRIPT], "ULTRA_SOCIAL_DORKS")
        
        mid2_stats = get_lead_stats()
        print(f"  --> Gained {mid2_stats['verified_emails'] - start_emails} verified emails from Ultra Social Harvester.", flush=True)

        if mid2_stats["verified_emails"] >= TARGET_VERIFIED_EMAILS:
            print(f"\n🎉 [MILESTONE REACHED] Reached target! Total: {mid2_stats['verified_emails']:,}", flush=True)
            trigger_dashboard_update()
            break

        # Step 3: Run Multi-Source Trading & MCP Scraper Engine
        start_emails = mid2_stats["verified_emails"]
        run_script_safe(["python3", "-u", SCRAPER_SCRIPT, "--pages", "5"], "MCP_TRADING_SCRAPER")

        end_stats = get_lead_stats()
        gained_cycle = end_stats["verified_emails"] - current_emails
        print(f"\n✅ CYCLE #{cycle} SUMMARY: Gained {gained_cycle} new verified emails. Total: {end_stats['verified_emails']:,} / {TARGET_VERIFIED_EMAILS:,}", flush=True)

        trigger_dashboard_update()

        cycle += 1
        print("Waiting 10 seconds before starting next scaling iteration...")
        time.sleep(10)

if __name__ == "__main__":
    main()
