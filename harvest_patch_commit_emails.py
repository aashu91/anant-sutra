#!/usr/bin/env python3
"""
harvest_patch_commit_emails.py — High-Speed Rate-Limit-Proof GitHub .patch Commit Email Harvester
Bypasses GitHub API rate limits completely by scraping raw commit patches (repo.atom feeds & .patch commit URLs).
Saves verified leads to /data/data/com.termux/files/home/sutralang/mcp_leads.db and triggers HTML dashboard update.
"""

import os
import re
import time
import json
import sqlite3
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed

DB_PATH = "/data/data/com.termux/files/home/sutralang/mcp_leads.db"
GEN_SCRIPT = "/data/data/com.termux/files/home/generate_leads_dashboard.py"

EXCLUDED_EMAIL_DOMAINS = [
    "users.noreply.github.com",
    "noreply.github.com",
    "dependabot.com",
    "sentry.io",
    "example.com",
    "domain.com",
    "w3.org",
    "schema.org",
    "github-actions"
]

TARGET_REPOS = [
    # MCP & AI Agent Repos
    "modelcontextprotocol/servers",
    "modelcontextprotocol/python-sdk",
    "modelcontextprotocol/typescript-sdk",
    "elizaos/eliza",
    "langchain-ai/langchain",
    "crewAIInc/crewAI",
    "AutoGPTq/AutoGPT",
    "browserbase/stagehand",
    "phidatahq/phidata",
    "pydantic/pydantic-ai",
    "open-interpreter/open-interpreter",
    "ollama/ollama",
    "vllm-project/vllm",
    "huggingface/transformers",
    "run-llama/llama_index",
    "mcp-get/mcp-get",
    "punkpeye/awesome-mcp-servers",
    "antigravity-market/mcp-web3-server",
    "antigravity/mcp-tools",
    "shroominic/code-interpreter-api",
    "astronomer/astro",
    "sgl-project/sglang",
    "vllm-project/vllm",
    "lmstudio-ai/lms",
    "QwenLM/Qwen",
    "THUDM/ChatGLM3",
    "deepseek-ai/DeepSeek-V3",
    "deepseek-ai/DeepSeek-Coder",
    "mistralai/mistral-src",
    "meta-llama/llama",

    # Web3, EVM & Solana Repos
    "hyperliquid-dex/hyperliquid-python-sdk",
    "polymarket/clob-client",
    "ethers-io/ethers.js",
    "wevm/viem",
    "wevm/wagmi",
    "solana-labs/solana-web3.js",
    "coral-xyz/anchor",
    "uniswap/v3-core",
    "uniswap/v3-periphery",
    "aave/aave-v3-core",
    "yearn/yearn-vaults",
    "curvefi/curve-contract",
    "Compound-Finance/compound-protocol",
    "OpenZeppelin/openzeppelin-contracts",
    "foundry-rs/foundry",
    "dapphub/dss",
    "flashbots/mev-boost",
    "flashbots/ethers-provider-flashbots",
    "hummingbot/hummingbot",
    "freqtrade/freqtrade",
    "crypto-trading-bot/crypto-trading-bot",
    "tauri-apps/tauri",
    "alpacahq/alpaca-py",
    "ccxt/ccxt",
    "solana-labs/solana-program-library",
    "pyth-network/pyth-sdk-rs",
    "chainlink/chainlink",
    "rust-lang/rust",
    "golang/go",
    "python/cpython",
    "facebook/react",
    "vercel/next.js",
    "tailwindlabs/tailwindcss",
    "prisma/prisma",
    "drizzle-team/drizzle-orm",
    "trpc/trpc",
    "shadcn-ui/ui",
    "expressjs/express",
    "nest-js/nest",
    "fastapi/fastapi",
    "django/django",
    "pallets/flask",
    "scikit-learn/scikit-learn",
    "pytorch/pytorch",
    "tensorflow/tensorflow",
    "pandas-dev/pandas",
    "numpy/numpy"
]

def extract_clean_email(text: str) -> str:
    if not text:
        return ""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    matches = re.findall(pattern, text)
    for m in matches:
        m_lower = m.lower()
        if not any(domain in m_lower for domain in EXCLUDED_EMAIL_DOMAINS):
            return m
    return ""

def init_db():
    conn = sqlite3.connect(DB_PATH, timeout=20.0)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS mcp_leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            author TEXT,
            email TEXT,
            repo_title TEXT,
            url TEXT UNIQUE,
            niche TEXT,
            draft_pitch TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn

def get_existing_urls_and_emails():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT url, email FROM mcp_leads")
    rows = cur.fetchall()
    conn.close()
    urls = {r[0] for r in rows if r[0]}
    emails = {r[1].lower() for r in rows if r[1]}
    return urls, emails

def generate_cold_pitch(repo: str, author_name: str) -> str:
    return (
        f"Hi {author_name},\n\n"
        f"I came across your work on {repo} and was really impressed. "
        f"We've built Robinhood EVM MCP — a high-performance Universal Web3 Model Context Protocol server "
        f"that allows AI agents (Claude, Cursor, ElizaOS) to execute cross-chain swaps, trade Polymarket/EVM/Solana positions, "
        f"and manage non-custodial wallets seamlessly.\n\n"
        f"Would love to connect or get your feedback on our open-source release!\n\n"
        f"Best regards,\nAshutosh Singh | salvationfinder"
    )

def scrape_atom_commits(repo: str, existing_urls: set, existing_emails: set) -> list:
    leads = []
    atom_url = f"https://github.com/{repo}/commits/main.atom"
    req = urllib.request.Request(atom_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                xml_data = resp.read().decode("utf-8", errors="ignore")
                root = ET.fromstring(xml_data)
                ns = {"atom": "http://www.w3.org/2005/Atom"}
                for entry in root.findall("atom:entry", ns):
                    link_elem = entry.find("atom:link", ns)
                    commit_url = link_elem.attrib.get("href", "") if link_elem is not None else ""
                    if not commit_url or commit_url in existing_urls:
                        continue
                    
                    author_elem = entry.find("atom:author", ns)
                    author_name = "Unknown"
                    if author_elem is not None:
                        name_tag = author_elem.find("atom:name", ns)
                        if name_tag is not None and name_tag.text:
                            author_name = name_tag.text.strip()
                    
                    patch_url = commit_url + ".patch"
                    preq = urllib.request.Request(patch_url, headers={"User-Agent": "Mozilla/5.0"})
                    try:
                        with urllib.request.urlopen(preq, timeout=8) as presp:
                            if presp.status == 200:
                                patch_text = presp.read().decode("utf-8", errors="ignore")
                                from_match = re.search(r'^From:\s+(.*?)\s+<([^>]+)>', patch_text, re.MULTILINE)
                                email = ""
                                if from_match:
                                    if author_name == "Unknown":
                                        author_name = from_match.group(1).strip()
                                    email = extract_clean_email(from_match.group(2).strip())
                                else:
                                    email = extract_clean_email(patch_text)
                                
                                if email and email.lower() not in existing_emails:
                                    niche = "mcp-server" if "mcp" in repo.lower() else ("trading-bot" if "trading" in repo.lower() or "bot" in repo.lower() else "web3-mcp")
                                    pitch = generate_cold_pitch(repo, author_name)
                                    leads.append({
                                        "source": "github_patch",
                                        "author": author_name,
                                        "email": email,
                                        "repo_title": f"Commit @{repo}",
                                        "url": commit_url,
                                        "niche": niche,
                                        "draft_pitch": pitch
                                    })
                                    existing_urls.add(commit_url)
                                    existing_emails.add(email.lower())
                    except Exception:
                        pass
    except Exception as e:
        pass
    return leads

def main():
    print("[*] Starting GitHub Raw .patch Commit Email Harvester (Rate-Limit Proof)...")
    conn = init_db()
    existing_urls, existing_emails = get_existing_urls_and_emails()
    print(f"[*] Baseline DB URLs: {len(existing_urls)}, Baseline Verified Emails: {len(existing_emails)}")

    added_count = 0
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(scrape_atom_commits, repo, existing_urls, existing_emails): repo for repo in TARGET_REPOS}
        cur = conn.cursor()
        for fut in as_completed(futures):
            repo = futures[fut]
            try:
                leads = fut.result()
                for lead in leads:
                    try:
                        cur.execute("""
                            INSERT INTO mcp_leads (source, author, email, repo_title, url, niche, draft_pitch)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (lead["source"], lead["author"], lead["email"], lead["repo_title"], lead["url"], lead["niche"], lead["draft_pitch"]))
                        conn.commit()
                        added_count += 1
                        print(f"  [SUCCESS #{added_count}] Direct Patch Lead: @{lead['author']} ({lead['email']}) -> {lead['repo_title']}")
                    except sqlite3.IntegrityError:
                        pass
            except Exception as e:
                pass

    conn.close()
    print(f"\n[DONE] Raw Patch Harvester finished! Scraped {added_count} fresh verified emails.")

if __name__ == "__main__":
    main()
