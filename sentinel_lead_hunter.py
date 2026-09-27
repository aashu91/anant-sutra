#!/usr/bin/env python3
"""
sentinel_lead_hunter.py — Sovereign Lead Generation & Cold Pitch Engine for Swa-Kevala OS
Part of SutraOS & Antigravity Ecosystem.

Scrapes GitHub, tech forums & public web for local AI / data privacy inquiries,
stores qualified leads in SQLite leads.db, and auto-generates personalized cold pitches.
"""

import os
import re
import json
import sqlite3
import urllib.request
import urllib.parse

# ponytail: stdlib-only Lead Hunter engine using SQLite & urllib.request.
# Ceiling: Public API rate limits (GitHub 60 req/hr unauth). Upgrade path: add GITHUB_TOKEN header if env present.

LEADS_DB = "/data/data/com.termux/files/home/sutralang/leads.db"

def get_db():
    conn = sqlite3.connect(LEADS_DB, timeout=10.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    conn.execute("""

        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            title TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            email TEXT,
            author TEXT,
            pain_point TEXT,
            status TEXT DEFAULT 'new',
            draft_pitch TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn

def extract_email(text: str) -> str:
    """Extracts first valid email address from text using regex."""
    if not text:
        return ""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    matches = re.findall(pattern, text)
    return matches[0] if matches else ""

def generate_cold_pitch(title: str, author: str, pain_point: str) -> str:
    """Generates a high-converting, non-slop cold outreach pitch in salvationfinder voice."""
    short_title = (title[:60] + '...') if len(title) > 60 else title
    return (
        f"Hey {author or 'there'}, saw your post regarding '{short_title}'. "
        f"We faced the exact same issue and built Swa-Kevala OS — a zero-SaaS, <50MB RAM, "
        f"100% offline-first AI operating engine (zero cloud leaks, zero API costs). "
        f"Would love to give you an early access binary if you are still looking for a local solution!"
    )

def fetch_github_leads():
    """Scrapes public GitHub issues & discussions matching local AI & privacy queries."""
    query = "local ai privacy OR offline ai engine OR self hosted llm"
    url = f"https://api.github.com/search/issues?q={urllib.parse.quote(query)}+is:open&sort=created&order=desc&per_page=15"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Termux; SwaKevalaSentinel/1.0)",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # ponytail: optional unauth to auth upgrade if GITHUB_TOKEN present
    github_token = os.environ.get("GITHUB_TOKEN")
    if github_token:
        headers["Authorization"] = f"token {github_token}"
        
    req = urllib.request.Request(url, headers=headers)
    new_count = 0
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                items = data.get("items", [])
                conn = get_db()
                cur = conn.cursor()
                
                for item in items:
                    title = item.get("title", "")
                    issue_url = item.get("html_url", "")
                    body = item.get("body", "") or ""
                    author = item.get("user", {}).get("login", "Unknown")
                    email = extract_email(body)
                    pain_point = body[:150].replace("\n", " ").strip()
                    
                    pitch = generate_cold_pitch(title, author, pain_point)
                    
                    try:
                        cur.execute("""
                            INSERT INTO leads (source, title, url, email, author, pain_point, draft_pitch)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, ("github_issues", title, issue_url, email, author, pain_point, pitch))
                        new_count += 1
                    except sqlite3.IntegrityError:
                        pass # Duplicate URL already exists
                        
                conn.commit()
                conn.close()
    except Exception as e:
        print(f"[WARN] Lead Hunter GitHub search error: {e}")
        
    return new_count

def run_lead_hunter_cycle() -> dict:
    """Executes a full lead hunter scan and returns updated database stats."""
    new_leads = fetch_github_leads()
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM leads")
    total_leads = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM leads WHERE status='new'")
    new_status_leads = cur.fetchone()[0]
    
    conn.close()
    return {
        "added_this_run": new_leads,
        "total_leads": total_leads,
        "new_leads": new_status_leads
    }

def get_latest_leads(limit: int = 5):
    """Retrieves recent leads for Sentinel status reports."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT author, title, url, draft_pitch FROM leads ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return [{"author": r[0], "title": r[1], "url": r[2], "pitch": r[3]} for r in rows]

# ponytail: minimal runnable check for non-trivial logic verification
if __name__ == "__main__":
    print("Executing Lead Hunter self-check...")
    res = run_lead_hunter_cycle()
    print(f"[RESULT] Hunter cycle completed: {res}")
    latest = get_latest_leads(2)
    print(f"[LATEST LEADS] Scraped: {len(latest)} leads")
    for l in latest:
        print(f"  • Author: {l['author']} | Title: {l['title'][:40]} | URL: {l['url']}")
