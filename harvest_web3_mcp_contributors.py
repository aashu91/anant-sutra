#!/usr/bin/env python3
"""
harvest_web3_mcp_contributors.py — Multi-Threaded High-Volume GitHub Events & Contributor Email Harvester
Bypasses Search API limits by dynamic repo discovery and scraping public push events in parallel.
Saves leads into /data/data/com.termux/files/home/sutralang/mcp_leads.db and triggers HTML update.
"""

import os
import re
import json
import time
import sqlite3
import urllib.request
import urllib.parse
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

DB_PATH = "/data/data/com.termux/files/home/sutralang/mcp_leads.db"
GEN_SCRIPT = "/data/data/com.termux/files/home/generate_leads_dashboard.py"

TARGET_REPOS = [
    # Model Context Protocol & AI Agents
    "modelcontextprotocol/servers",
    "modelcontextprotocol/python-sdk",
    "modelcontextprotocol/typescript-sdk",
    "elizaos/eliza",
    "langchain-ai/langchain",
    "crewAIInc/crewAI",
    "AutoGPTq/AutoGPT",
    "browserbase/stagehand",
    "phidatahq/phidata",
    "golem-factory/golem",
    "shroominic/code-interpreter-api",
    "pydantic/pydantic-ai",
    "open-interpreter/open-interpreter",
    
    # EVM, Trading & Solana Repos
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
    "robinhood/robinhood-mcp",
    "salvationfinder/robinhood-evm-mcp",
    "hummingbot/hummingbot",
    "freqtrade/freqtrade",
    "crypto-trading-bot/crypto-trading-bot",
    "tauri-apps/tauri",
    "pipscoin/trading-bot",
    "alpacahq/alpaca-py",
    "ccxt/ccxt",
    "solana-labs/solana-program-library",
    "pyth-network/pyth-sdk-rs",
    "chainlink/chainlink",

    # More MCP & AI Agent Repos
    "anthropic-ai/anthropic-sdk-python",
    "openai/openai-python",
    "ollama/ollama",
    "vllm-project/vllm",
    "huggingface/transformers",
    "run-llama/llama_index",
    "astronomer/astro",
    "mcp-get/mcp-get",
    "punkpeye/awesome-mcp-servers",
    "antigravity-market/mcp-web3-server",
    "antigravity/mcp-tools"
]

SEARCH_TOPICS = [
    "mcp-server",
    "model-context-protocol",
    "web3-mcp",
    "trading-bot",
    "solana-bot",
    "mev-bot",
    "elizaos",
    "ai-agent",
    "crypto-trading",
    "hyperliquid",
    "polymarket-bot",
    "viem",
    "wagmi",
    "ethers",
    "vibe-coding",
    "solidity",
    "foundry",
    "anchor-framework",
    "cross-chain",
    "flashloan",
    "dex-arbitrage",
    "crypto-bot",
    "web3-agent",
    "claude-mcp",
    "cursor-mcp",
    "pydantic-ai",
    "autonolas",
    "virtuals-protocol",
    "coinbase-agentkit",
    "langchain",
    "llama-index",
    "crewai",
    "autogpt",
    "hummingbot",
    "freqtrade",
    "ccxt",
    "solana-program-library",
    "openzeppelin-contracts",
    "aave-v3",
    "uniswap-v3",
    "flashbots",
    "zero-knowledge",
    "circom",
    "snarkjs",
    "starknet",
    "cairo-lang",
    "sui-move",
    "aptos-core",
    "ton-blockchain",
    "tact-lang"
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
    "github-actions"
]

def get_gh_token() -> str:
    try:
        t = subprocess.check_output(["gh", "auth", "token"], stderr=subprocess.DEVNULL).decode().strip()
        if t:
            return t
    except Exception:
        pass
    return os.environ.get("GITHUB_TOKEN", "")

def get_headers():
    headers = {
        "User-Agent": "Mozilla/5.0 (Termux; SwaKevalaHarvester/2.0)",
        "Accept": "application/vnd.github.v3+json"
    }
    tok = get_gh_token()
    if tok:
        headers["Authorization"] = f"token {tok}"
    return headers

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

def generate_cold_pitch(repo_title: str, author: str) -> str:
    author_name = author if author and author != "Unknown" else "there"
    return (
        f"Hey {author_name}, saw your work on '{repo_title}'. "
        f"If you are automating trades or building AI execution agents, check out our Universal Web3 MCP Server — "
        f"featuring Robinhood EVM MCP tools, zero-latency cross-chain DEX swaps, and multi-wallet trade execution directly via Model Context Protocol. "
        f"Would love to send over early API/SDK access!"
    )

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
        urls = set(r[0] for r in rows if r[0])
        emails = set(r[1].lower() for r in rows if r[1])
        conn.close()
        return urls, emails
    except Exception:
        return set(), set()

def fetch_user_email_from_events(username: str, headers: dict) -> str:
    url = f"https://api.github.com/users/{username}/events/public"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            if resp.status == 200:
                events = json.loads(resp.read().decode("utf-8"))
                for ev in events:
                    if ev.get("type") == "PushEvent":
                        commits = ev.get("payload", {}).get("commits", [])
                        for commit in commits:
                            email = extract_clean_email(commit.get("author", {}).get("email", ""))
                            if email:
                                return email
    except Exception:
        pass
    return ""

def fetch_user_profile_email(username: str, headers: dict) -> str:
    try:
        ureq = urllib.request.Request(f"https://api.github.com/users/{username}", headers=headers)
        with urllib.request.urlopen(ureq, timeout=8) as uresp:
            uinfo = json.loads(uresp.read().decode("utf-8"))
            return extract_clean_email(uinfo.get("email") or uinfo.get("bio", ""))
    except Exception:
        return ""

def discover_dynamic_repos(headers: dict) -> List[str]:
    repos = set(TARGET_REPOS)
    def fetch_topic_repos(topic: str):
        found = []
        for page in range(1, 6):
            try:
                url = f"https://api.github.com/search/repositories?q={topic}+sort:updated&per_page=30&page={page}"
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=8) as resp:
                    if resp.status == 200:
                        data = json.loads(resp.read().decode("utf-8"))
                        items = data.get("items", [])
                        if not items:
                            break
                        for item in items:
                            full_name = item.get("full_name")
                            if full_name:
                                found.append(full_name)
                    else:
                        break
            except Exception:
                break
            time.sleep(0.2)
        return found

    with ThreadPoolExecutor(max_workers=10) as texec:
        futures = [texec.submit(fetch_topic_repos, top) for top in SEARCH_TOPICS]
        for fut in as_completed(futures):
            try:
                repos.update(fut.result())
            except Exception:
                pass
    return list(repos)

def fetch_repo_commit_emails(repo: str, headers: dict, existing_urls: set, existing_emails: set) -> List[dict]:
    leads = []
    for page in range(1, 3):
        url = f"https://api.github.com/repos/{repo}/commits?per_page=100&page={page}"
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    commits = json.loads(resp.read().decode("utf-8"))
                    if isinstance(commits, list) and len(commits) > 0:
                        for c in commits:
                            commit_obj = c.get("commit", {})
                            author_obj = commit_obj.get("author", {})
                            author_name = author_obj.get("name") or c.get("author", {}).get("login") or "Unknown"
                            email = extract_clean_email(author_obj.get("email", ""))
                            commit_url = c.get("html_url", "")
                            
                            if email and email.lower() not in existing_emails and commit_url not in existing_urls:
                                niche = "mcp-server" if "mcp" in repo.lower() else ("trading-bot" if "trading" in repo.lower() or "bot" in repo.lower() else "web3-mcp")
                                pitch = generate_cold_pitch(repo, author_name)
                                leads.append({
                                    "source": "github_commit",
                                    "author": author_name,
                                    "email": email,
                                    "repo_title": f"Commit @{repo}",
                                    "url": commit_url,
                                    "niche": niche,
                                    "draft_pitch": pitch
                                })
                                existing_urls.add(commit_url)
                                existing_emails.add(email.lower())
                    else:
                        break
        except Exception:
            break
    return leads

def process_contributor(login: str, repo: str, headers: dict, existing_urls: set, existing_emails: set):
    if not login or login == "Unknown":
        return None
    user_url = f"https://github.com/{login}"
    if user_url in existing_urls:
        return None

    email = fetch_user_email_from_events(login, headers)
    if not email:
        email = fetch_user_profile_email(login, headers)

    if email and email.lower() not in existing_emails:
        niche = "mcp-server" if "mcp" in repo.lower() else ("trading-bot" if "trading" in repo.lower() or "bot" in repo.lower() else "web3-mcp")
        pitch = generate_cold_pitch(repo, login)
        return {
            "source": "github_contributor",
            "author": login,
            "email": email,
            "repo_title": f"Contributor @{repo}",
            "url": user_url,
            "niche": niche,
            "draft_pitch": pitch
        }
    return None

def harvest():
    print("[*] Starting Web3/MCP Multi-Threaded Contributor & Events Email Harvester...")
    headers = get_headers()
    conn = init_db()
    existing_urls, existing_emails = get_existing_urls_and_emails()

    start_leads = len(existing_urls)
    print(f"[*] Baseline DB URLs: {start_leads}, Baseline Emails: {len(existing_emails)}")

    all_repos = discover_dynamic_repos(headers)
    print(f"[*] Total Target Repositories Discovered: {len(all_repos)}")

    added_count = 0

    def process_repo(repo: str):
        leads = fetch_repo_commit_emails(repo, headers, existing_urls, existing_emails)
        
        contrib_url = f"https://api.github.com/repos/{repo}/contributors?per_page=100"
        req = urllib.request.Request(contrib_url, headers=headers)
        contributors = []
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    contributors = json.loads(resp.read().decode("utf-8"))
        except Exception:
            pass

        with ThreadPoolExecutor(max_workers=8) as texec:
            futures = [texec.submit(process_contributor, c.get("login"), repo, headers, existing_urls, existing_emails)
                       for c in contributors if isinstance(c, dict)]
            for fut in as_completed(futures):
                try:
                    res = fut.result()
                    if res:
                        leads.append(res)
                except Exception:
                    pass
        return leads

    with ThreadPoolExecutor(max_workers=5) as repo_exec:
        repo_futures = [repo_exec.submit(process_repo, r) for r in all_repos]
        cur = conn.cursor()
        for fut in as_completed(repo_futures):
            try:
                leads = fut.result()
                for lead in leads:
                    try:
                        cur.execute("""
                            INSERT INTO mcp_leads (source, author, email, repo_title, url, niche, draft_pitch)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (lead["source"], lead["author"], lead["email"], lead["repo_title"], lead["url"], lead["niche"], lead["draft_pitch"]))
                        conn.commit()
                        existing_urls.add(lead["url"])
                        existing_emails.add(lead["email"].lower())
                        added_count += 1
                        print(f"  [SUCCESS #{added_count}] Scraped Lead: @{lead['author']} ({lead['email']}) -> {lead['repo_title']}")

                        if added_count % 10 == 0:
                            subprocess.run(["python3", GEN_SCRIPT], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    except sqlite3.IntegrityError:
                        pass
            except Exception:
                pass

    conn.close()
    print(f"\n[DONE] Harvester run finished! Total New Emails Scraped: {added_count}")
    subprocess.run(["python3", GEN_SCRIPT])

if __name__ == "__main__":
    harvest()

