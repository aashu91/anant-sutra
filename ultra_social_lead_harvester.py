#!/usr/bin/env python3
"""
ultra_social_lead_harvester.py — Balanced 15-Worker Thread Social & Search Engine Dork Harvester
Includes User-Agent Rotation + Randomized Delays (0.3s - 0.7s) to prevent Search Engine / IP Rate Limiting.
"""

import os
import re
import json
import time
import html
import random
import sqlite3
import urllib.request
import urllib.parse
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

DB_PATH = "/data/data/com.termux/files/home/sutralang/mcp_leads.db"
GEN_SCRIPT = "/data/data/com.termux/files/home/generate_leads_dashboard.py"

SOCIAL_DOMAINS = [
    "site:x.com",
    "site:twitter.com",
    "site:instagram.com",
    "site:facebook.com",
    "site:linkedin.com/in",
    "site:github.com",
    "site:dev.to",
    "site:medium.com",
    "site:reddit.com/r",
    "site:news.ycombinator.com",
    "site:t.me",
    "site:telegram.me",
    "site:discord.gg",
    "site:discord.com",
    "site:lu.ma",
    "site:ethglobal.com",
    "site:devpost.com"
]

EMAIL_DOMAINS = [
    "@gmail.com",
    "@yahoo.com",
    "@outlook.com",
    "@hotmail.com",
    "@proton.me",
    "@protonmail.com",
    "@icloud.com"
]

TARGET_KEYWORDS = [
    "MCP server",
    "Model Context Protocol",
    "Web3 trader",
    "crypto bot",
    "vibe coding",
    "solidity developer",
    "EVM bot",
    "solana bot",
    "AI agent trading",
    "Robinhood EVM",
    "mev bot",
    "dex bot",
    "flashloan bot",
    "elizaos",
    "hyperliquid",
    "polymarket bot",
    "langchain mcp",
    "cursor mcp",
    "claude mcp",
    "autonolas",
    "virtuals protocol",
    "coinbase agentkit",
    "mcp tool",
    "mcp client",
    "pydantic-ai",
    "viem",
    "wagmi",
    "ethers.js",
    "foundry",
    "anchor framework",
    "cross chain swap",
    "arbitrage bot",
    "crypto developer",
    "smart contract developer"
]

EXCLUDED_EMAIL_DOMAINS = [
    "users.noreply.github.com",
    "noreply.github.com",
    "dependabot.com",
    "sentry.io",
    "example.com",
    "domain.com",
    "w3.org",
    "schema.org",
    "facebook.com",
    "instagram.com",
    "twitter.com"
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Android 14; Mobile; rv:124.0) Gecko/124.0 Firefox/124.0"
]

def init_db():
    conn = sqlite3.connect(DB_PATH, timeout=15.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS mcp_leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            author TEXT NOT NULL,
            email TEXT,
            repo_title TEXT,
            url TEXT UNIQUE NOT NULL,
            niche TEXT NOT NULL,
            draft_pitch TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    return conn

def get_existing_urls_and_emails():
    if not os.path.exists(DB_PATH):
        return set(), set()
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        cur = conn.cursor()
        cur.execute("SELECT url, email FROM mcp_leads")
        rows = cur.fetchall()
        conn.close()
        urls = set(r[0] for r in rows if r[0])
        emails = set(r[1].lower() for r in rows if r[1])
        return urls, emails
    except Exception:
        return set(), set()

def extract_emails(text: str):
    if not text:
        return []
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    matches = re.findall(pattern, text)
    valid_emails = []
    for m in matches:
        m_lower = m.lower()
        if not any(ex in m_lower for ex in EXCLUDED_EMAIL_DOMAINS):
            valid_emails.append(m)
    return list(set(valid_emails))

def generate_pitch(platform: str, keyword: str, author: str, title: str) -> str:
    author_name = author if author and author != "Developer" else "there"
    return (
        f"Hey {author_name}, saw your {platform} profile/post regarding '{title[:40]}'. "
        f"We've built the Universal Web3 MCP Server — featuring Robinhood EVM MCP tools, "
        f"zero-latency cross-chain DEX swaps, and automated trade execution directly via Model Context Protocol. "
        f"Would love to send over early API/SDK access!"
    )

def fetch_duckduckgo_dork(site_domain: str, keyword: str, email_provider: str):
    # Small random delay to avoid IP rate limiting / blocks
    time.sleep(random.uniform(0.3, 0.7))

    query = f'{site_domain} "{keyword}" "{email_provider}"'
    encoded_q = urllib.parse.quote(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded_q}"

    req = urllib.request.Request(url, headers={
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9"
    })

    found_leads = []
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            if resp.status == 200:
                body = resp.read().decode("utf-8", errors="ignore")
                matches = re.findall(r'<a class="result__url" href="([^"]+)".*?<a class="result__snippet[^>]*>(.*?)</a>', body, re.DOTALL)
                for target_url, snippet_raw in matches:
                    clean_snippet = re.sub(r'<[^>]+>', '', snippet_raw)
                    clean_snippet = html.unescape(clean_snippet).strip()
                    
                    emails = extract_emails(clean_snippet)
                    if emails:
                        for email in emails:
                            platform = "x_social" if "x.com" in target_url or "twitter.com" in target_url else (
                                "instagram" if "instagram.com" in target_url else (
                                "facebook" if "facebook.com" in target_url else (
                                "linkedin_public" if "linkedin.com" in target_url else (
                                "reddit" if "reddit.com" in target_url else (
                                "hackernews" if "news.ycombinator.com" in target_url else (
                                "telegram" if "t.me" in target_url or "telegram.me" in target_url else (
                                "discord" if "discord.gg" in target_url or "discord.com" in target_url else (
                                "events" if "lu.ma" in target_url or "ethglobal.com" in target_url or "devpost.com" in target_url else (
                                "devto" if "dev.to" in target_url else "web_social"
                            )))))))))

                            author = "Trader/Dev"
                            if "x.com/" in target_url or "twitter.com/" in target_url:
                                parts = target_url.split("/")
                                if len(parts) > 3:
                                    author = "@" + parts[3].split("?")[0]
                            elif "instagram.com/" in target_url:
                                parts = target_url.split("/")
                                if len(parts) > 3:
                                    author = "@" + parts[3].split("?")[0]
                            elif "t.me/" in target_url:
                                parts = target_url.split("/")
                                if len(parts) > 3:
                                    author = "t.me/" + parts[3].split("?")[0]
                            elif "dev.to/" in target_url:
                                parts = target_url.split("/")
                                if len(parts) > 3:
                                    author = "@" + parts[3].split("?")[0]

                            title = f"{platform.upper()} Profile ({keyword}): {clean_snippet[:60]}"
                            pitch = generate_pitch(platform, keyword, author, title)

                            found_leads.append({
                                "source": platform,
                                "author": author,
                                "email": email,
                                "repo_title": title,
                                "url": target_url.split("?")[0],
                                "niche": keyword.replace(" ", "-").lower(),
                                "draft_pitch": pitch
                            })
    except Exception:
        pass

    return found_leads

def run_harvest_turbo():
    print("🚀 [BALANCED 15 WORKERS + RANDOM DELAYS] Starting Harvester...")
    conn = init_db()
    existing_urls, existing_emails = get_existing_urls_and_emails()
    print(f"[*] Baseline DB URLs: {len(existing_urls)}, Baseline Emails: {len(existing_emails)}")

    total_added = 0
    tasks = []

    # 15 Balanced Worker Threads + Random Delays for Rate-Limit Safety
    with ThreadPoolExecutor(max_workers=15) as executor:
        for domain in SOCIAL_DOMAINS:
            for kw in TARGET_KEYWORDS:
                for ep in EMAIL_DOMAINS:
                    tasks.append(executor.submit(fetch_duckduckgo_dork, domain, kw, ep))

        cur = conn.cursor()
        for future in as_completed(tasks):
            try:
                leads = future.result()
                if leads:
                    for lead in leads:
                        if lead["url"] not in existing_urls and lead["email"].lower() not in existing_emails:
                            try:
                                cur.execute("""
                                    INSERT INTO mcp_leads (source, author, email, repo_title, url, niche, draft_pitch)
                                    VALUES (?, ?, ?, ?, ?, ?, ?)
                                """, (lead["source"], lead["author"], lead["email"], lead["repo_title"], lead["url"], lead["niche"], lead["draft_pitch"]))
                                conn.commit()
                                existing_urls.add(lead["url"])
                                existing_emails.add(lead["email"].lower())
                                total_added += 1
                                print(f"  ⚡ [BALANCED LEAD #{total_added}] [{lead['source'].upper()}] {lead['author']} ({lead['email']}) -> {lead['niche']}")

                                if total_added % 5 == 0:
                                    subprocess.run(["python3", GEN_SCRIPT], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            except sqlite3.IntegrityError:
                                pass
            except Exception:
                pass

    conn.close()
    print(f"\n✅ [COMPLETED BATCH] Total New Social Media Emails Harvested: {total_added}")
    subprocess.run(["python3", GEN_SCRIPT])

if __name__ == "__main__":
    run_harvest_turbo()
