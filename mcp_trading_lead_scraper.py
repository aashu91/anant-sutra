#!/usr/bin/env python3
"""
mcp_trading_lead_scraper.py — Continuous High-Capacity Lead Generation Engine
Targets Web3 MCP servers, crypto trading bots, AI vibe coding, MCP protocols,
GitHub repos/commits/issues/users, Dev.to, HackerNews, Reddit, X (Twitter), LinkedIn, Telegram, and Discord.

Saves verified leads to SQLite DB: /data/data/com.termux/files/home/sutralang/mcp_leads.db
Fields: id, source, author, email, repo_title, url, niche, draft_pitch, created_at
"""

import os
import re
import json
import time
import argparse
import sqlite3
import urllib.request
import urllib.parse
import subprocess
from typing import Dict, List, Optional, Tuple, Set

import requests
from bs4 import BeautifulSoup

# Database path
DB_PATH = "/data/data/com.termux/files/home/sutralang/mcp_leads.db"

# Target topics for repository & forum searches (26 High-Conversion Web3/MCP/AI Niches)
TARGET_TOPICS = [
    "mcp-server",
    "web3-mcp",
    "trading-bot",
    "vibe-coding",
    "solidity-mcp",
    "crypto-trader",
    "mcp-protocol",
    "robinhood-mcp",
    "model-context-protocol",
    "ai-agent",
    "solana-bot",
    "mev-bot",
    "dex-bot",
    "elizaos",
    "hyperliquid-mcp",
    "polymarket-bot",
    "langchain-mcp",
    "claude-mcp",
    "cursor-mcp",
    "web3-agent",
    "crypto-agent",
    "uniswap-bot",
    "flashloan-bot",
    "ethers-js",
    "viem",
    "solana-web3",
    "pydantic-ai",
    "coinbase-agentkit",
    "autonolas",
    "virtuals-protocol",
    "foundry-rs",
    "anchor-framework",
    "arbitrage-bot",
    "biconomy-sdk",
    "safe-global"
]

# Social media specific search keywords (X, LinkedIn, Telegram, Discord, Reddit)
SOCIAL_KEYWORDS = [
    "#MCP",
    "Model Context Protocol",
    "Vibe Coding",
    "Web3 Trader",
    "Crypto Bot",
    "Solana Bot",
    "AI Agent Trader",
    "Robinhood EVM",
    "DEX Bot"
]

# Email exclusion filters for automated bots/system accounts/placeholders
EXCLUDED_EMAIL_DOMAINS = [
    "users.noreply.github.com",
    "noreply.github.com",
    "dependabot.com",
    "sentry.io",
    "sentry-io",
    "example.com",
    "example.org",
    "domain.com",
    "invalid.com",
    "test.com",
    "email.com",
    "w3.org",
    "schema.org",
    "github-actions",
    "renovatebot",
    "greenkeeper",
    "gitter.im",
    "npm",
    "snyk.io",
    "localhost"
]

def get_github_token() -> str:
    """Retrieve GitHub token from env or gh CLI."""
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        return token.strip()
    try:
        token = subprocess.check_output(["gh", "auth", "token"], stderr=subprocess.DEVNULL).decode().strip()
        if token:
            return token
    except Exception:
        pass
    return ""

def init_db(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Initialize SQLite database and table structure."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=15.0)
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

def get_existing_urls(db_path: str = DB_PATH) -> Set[str]:
    """Retrieve set of existing lead URLs in DB for fast duplicate prevention."""
    if not os.path.exists(db_path):
        return set()
    try:
        conn = sqlite3.connect(db_path, timeout=10.0)
        cur = conn.cursor()
        cur.execute("SELECT url FROM mcp_leads")
        urls = set(row[0] for row in cur.fetchall())
        conn.close()
        return urls
    except Exception:
        return set()

def extract_clean_email(text: str) -> str:
    """Extract valid developer email, filtering out bot/noreply addresses."""
    if not text:
        return ""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    matches = re.findall(pattern, text)
    for m in matches:
        m_lower = m.lower()
        if not any(domain in m_lower for domain in EXCLUDED_EMAIL_DOMAINS):
            return m
    return ""

def extract_github_profile_link(text: str) -> str:
    """Extract GitHub profile link if present in bio/snippet."""
    if not text:
        return ""
    m = re.search(r'https?://github\.com/([a-zA-Z0-9_-]+)', text)
    if m:
        username = m.group(1)
        if username.lower() not in ['features', 'pricing', 'about', 'blog', 'search', 'topics', 'trending', 'orgs', 'marketplace']:
            return f"https://github.com/{username}"
    return ""

def generate_cold_pitch(niche: str, repo_title: str, author: str, source: str) -> str:
    """Generate customized outreach pitch for Universal Web3 MCP Server across GitHub & Social channels."""
    short_title = repo_title[:50] + "..." if len(repo_title) > 50 else repo_title
    author_name = author if author and author != "Unknown" else "there"

    if source == "x_social":
        return (
            f"Hey {author_name}, saw your X post/bio regarding '{short_title}'. "
            f"If you are vibe-coding or building AI trading tools, check out our Universal Web3 MCP Server — "
            f"featuring Robinhood EVM MCP, zero-latency DEX swaps, and multi-wallet trade execution directly via Model Context Protocol. "
            f"Would love to send over early API/SDK access!"
        )
    elif source == "linkedin_public":
        return (
            f"Hi {author_name}, came across your profile regarding '{short_title}'. "
            f"We've built the Universal Web3 MCP Server — standardizing Robinhood EVM transactions, "
            f"smart contract calls, and cross-chain swaps into native MCP tools for AI agents. "
            f"Let's connect or explore integration opportunities!"
        )
    elif source in ["discord_public", "telegram_public", "reddit_public"]:
        return (
            f"Hey {author_name}, saw your dev post/community regarding '{short_title}'. "
            f"We built the Universal Web3 MCP Server to give crypto trading bots and AI vibe coders "
            f"direct trade execution capabilities via MCP standard tools. Check out our early release!"
        )
    elif niche in ["trading-bot", "crypto-trader", "robinhood-mcp", "Crypto Bot", "Web3 Trader", "solana-bot", "mev-bot", "dex-bot", "hyperliquid-mcp", "polymarket-bot"]:
        return (
            f"Hey {author_name}, saw your project '{short_title}'. "
            f"If you are automating trades or building AI execution agents, we launched the Universal Web3 MCP Server — "
            f"featuring Robinhood EVM MCP tools, zero-latency cross-chain DEX swaps, and multi-wallet trade execution directly via Model Context Protocol. "
            f"Would love to get your feedback or send over early API/SDK access!"
        )
    elif niche in ["web3-mcp", "solidity-mcp", "solana-web3", "ethers-js", "viem"]:
        return (
            f"Hey {author_name}, checked out '{short_title}' in Web3/MCP. "
            f"We've built the Universal Web3 MCP Server — standardizing Robinhood EVM transactions, smart contract calls, "
            f"and cross-chain swaps as native MCP tools for Cursor, Claude Code, and vibe-coding agents. "
            f"Would be great to connect or explore integration possibilities!"
        )
    else:  # vibe-coding, mcp-server, mcp-protocol, model-context-protocol, #MCP, etc.
        return (
            f"Hey {author_name}, came across '{short_title}' while exploring MCP ecosystem projects. "
            f"We built the Universal Web3 MCP Server to give AI vibe coders direct trade execution capabilities — "
            f"including Robinhood EVM MCP, cross-chain swaps, and instant on-chain interactions via simple MCP tools. "
            f"Let me know if you'd like to test the early access release!"
        )

class GitHubLeadScraper:
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Universal-Web3-MCP-LeadScraper/1.0"
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    def _api_get(self, url: str) -> Optional[dict]:
        """Make rate-limit-aware HTTP GET request to GitHub API."""
        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                rem = resp.headers.get("X-RateLimit-Remaining")
                if rem and int(rem) < 3:
                    reset_time = int(resp.headers.get("X-RateLimit-Reset", time.time() + 60))
                    sleep_duration = max(1, reset_time - int(time.time()) + 2)
                    print(f"[RATE-LIMIT] GitHub API limit near threshold. Sleeping {sleep_duration}s...")
                    time.sleep(sleep_duration)
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 403 and "rate limit" in str(e.reason).lower():
                print("[RATE-LIMIT] 403 Rate limited. Backing off 30s...")
                time.sleep(30)
            elif e.code == 422:
                # 422 Unprocessable Entity happens when search page exceeds GitHub's 1000 result cap
                pass
            elif e.code != 404:
                print(f"[WARN] HTTP {e.code} for {url}")
        except Exception as e:
            print(f"[WARN] Request error for {url}: {e}")
        return None

    def fetch_user_email(self, username: str) -> str:
        """Fetch email from public user profile if available."""
        if not username or username == "Unknown":
            return ""
        data = self._api_get(f"https://api.github.com/users/{username}")
        if data:
            email = extract_clean_email(data.get("email") or "")
            if email:
                return email
            bio = data.get("bio") or ""
            return extract_clean_email(bio)
        return ""

    def fetch_repo_commits_email(self, owner: str, repo: str) -> str:
        """Fetch author email from recent repository commits."""
        url = f"https://api.github.com/repos/{owner}/{repo}/commits?per_page=5"
        commits = self._api_get(url)
        if isinstance(commits, list):
            for c in commits:
                commit_obj = c.get("commit", {})
                author_email = extract_clean_email(commit_obj.get("author", {}).get("email", ""))
                if author_email:
                    return author_email
                committer_email = extract_clean_email(commit_obj.get("committer", {}).get("email", ""))
                if committer_email:
                    return committer_email
        return ""

    def _get_query_variations(self, topic: str, max_pages: int) -> List[Tuple[str, int]]:
        """Build search query variations (sliced by language & date) to bypass GitHub 1000 result search cap."""
        if max_pages <= 10:
            return [(topic, max_pages)]
        
        # When deep scanning (--pages 100), iterate through languages and date ranges
        pages_per_subquery = min(10, max_pages)
        queries = [(topic, pages_per_subquery)]
        
        languages = ["python", "typescript", "javascript", "go", "rust", "solidity", "cpp"]
        for lang in languages:
            queries.append((f"{topic} language:{lang}", pages_per_subquery))
            
        date_slices = [">2026-01-01", "2025-07-01..2025-12-31", "2025-01-01..2025-06-30", "2024-01-01..2024-12-31"]
        for ds in date_slices:
            queries.append((f"{topic} created:{ds}", pages_per_subquery))
            
        return queries

    def search_repositories(self, topic: str, max_pages: int = 2, existing_urls: Set[str] = None) -> List[dict]:
        """Search GitHub public repositories for a topic."""
        existing_urls = existing_urls or set()
        leads = []
        subqueries = self._get_query_variations(topic, max_pages)
        
        for q_str, p_limit in subqueries:
            for page in range(1, p_limit + 1):
                encoded_query = urllib.parse.quote(q_str)
                url = f"https://api.github.com/search/repositories?q={encoded_query}&sort=updated&order=desc&per_page=50&page={page}"
                data = self._api_get(url)
                time.sleep(1.0)
                if not data or "items" not in data:
                    break
                items = data.get("items", [])
                if not items:
                    break
                for item in items:
                    repo_title = item.get("full_name", "")
                    item_url = item.get("html_url", "")
                    if item_url in existing_urls:
                        continue
                        
                    owner_login = item.get("owner", {}).get("login", "Unknown")
                    desc = item.get("description") or ""

                    # Extract email
                    email = extract_clean_email(desc)
                    if not email and "/" in repo_title:
                        owner, repo_name = repo_title.split("/", 1)
                        email = self.fetch_repo_commits_email(owner, repo_name)
                    if not email:
                        email = self.fetch_user_email(owner_login)

                    pitch = generate_cold_pitch(topic, repo_title, owner_login, "github_repo")
                    leads.append({
                        "source": "github_repo",
                        "author": owner_login,
                        "email": email,
                        "repo_title": repo_title,
                        "url": item_url,
                        "niche": topic,
                        "draft_pitch": pitch
                    })
                    existing_urls.add(item_url)
        return leads

    def search_commits(self, topic: str, max_pages: int = 2, existing_urls: Set[str] = None) -> List[dict]:
        """Search GitHub commits matching target keywords."""
        existing_urls = existing_urls or set()
        leads = []
        subqueries = self._get_query_variations(topic, max_pages)
        
        for q_str, p_limit in subqueries:
            for page in range(1, p_limit + 1):
                encoded_query = urllib.parse.quote(q_str)
                url = f"https://api.github.com/search/commits?q={encoded_query}&sort=committer-date&order=desc&per_page=50&page={page}"
                data = self._api_get(url)
                time.sleep(1.0)
                if not data or "items" not in data:
                    break
                items = data.get("items", [])
                if not items:
                    break
                for item in items:
                    commit_url = item.get("html_url", "")
                    if commit_url in existing_urls:
                        continue
                        
                    commit_info = item.get("commit", {})
                    author_info = commit_info.get("author", {})
                    author_name = author_info.get("name") or item.get("author", {}).get("login") or "Unknown"
                    raw_email = author_info.get("email", "")
                    email = extract_clean_email(raw_email)
                    repo_title = item.get("repository", {}).get("full_name", "Unknown Repo")

                    pitch = generate_cold_pitch(topic, repo_title, author_name, "github_commit")
                    leads.append({
                        "source": "github_commit",
                        "author": author_name,
                        "email": email,
                        "repo_title": repo_title,
                        "url": commit_url,
                        "niche": topic,
                        "draft_pitch": pitch
                    })
                    existing_urls.add(commit_url)
        return leads

    def search_issues_prs(self, topic: str, max_pages: int = 2, existing_urls: Set[str] = None) -> List[dict]:
        """Search GitHub issues & PRs matching keywords."""
        existing_urls = existing_urls or set()
        leads = []
        subqueries = self._get_query_variations(topic, max_pages)
        
        for q_str, p_limit in subqueries:
            for page in range(1, p_limit + 1):
                encoded_query = urllib.parse.quote(q_str)
                url = f"https://api.github.com/search/issues?q={encoded_query}&sort=updated&order=desc&per_page=50&page={page}"
                data = self._api_get(url)
                time.sleep(1.0)
                if not data or "items" not in data:
                    break
                items = data.get("items", [])
                if not items:
                    break
                for item in items:
                    issue_url = item.get("html_url", "")
                    if issue_url in existing_urls:
                        continue
                        
                    title = item.get("title", "")
                    author = item.get("user", {}).get("login", "Unknown")
                    body = item.get("body") or ""
                    is_pr = "pull_request" in item

                    email = extract_clean_email(body)
                    if not email:
                        email = self.fetch_user_email(author)

                    source_type = "github_pr" if is_pr else "github_issue"
                    pitch = generate_cold_pitch(topic, title, author, source_type)
                    leads.append({
                        "source": source_type,
                        "author": author,
                        "email": email,
                        "repo_title": title,
                        "url": issue_url,
                        "niche": topic,
                        "draft_pitch": pitch
                    })
                    existing_urls.add(issue_url)
        return leads

    def search_users(self, topic: str, max_pages: int = 2, existing_urls: Set[str] = None) -> List[dict]:
        """Search GitHub users directly by topic in bio/readme."""
        existing_urls = existing_urls or set()
        leads = []
        p_limit = min(max_pages, 10)
        
        for page in range(1, p_limit + 1):
            encoded_query = urllib.parse.quote(f"{topic} in:bio,readme")
            url = f"https://api.github.com/search/users?q={encoded_query}&per_page=50&page={page}"
            data = self._api_get(url)
            time.sleep(1.0)
            if not data or "items" not in data:
                break
            items = data.get("items", [])
            if not items:
                break
            for item in items:
                user_login = item.get("login")
                user_url = item.get("html_url", f"https://github.com/{user_login}")
                if user_url in existing_urls:
                    continue
                    
                user_info = self._api_get(f"https://api.github.com/users/{user_login}")
                if not user_info:
                    continue
                    
                bio = user_info.get("bio") or ""
                blog = user_info.get("blog") or ""
                email = extract_clean_email(user_info.get("email") or bio)
                twitter_user = user_info.get("twitter_username")
                
                title = f"GitHub Developer @{user_login}: {bio[:70]}"
                if twitter_user:
                    title += f" [Twitter: @{twitter_user}]"
                    
                pitch = generate_cold_pitch(topic, title, user_login, "github_user")
                leads.append({
                    "source": "github_user",
                    "author": user_login,
                    "email": email,
                    "repo_title": title,
                    "url": user_url,
                    "niche": topic,
                    "draft_pitch": pitch
                })
                existing_urls.add(user_url)
        return leads

class SocialMediaLeadScraper:
    """Scraper targeting X (Twitter), LinkedIn public profiles, Reddit, Dev.to, and Telegram/Discord dev communities."""
    def __init__(self, gh_token: str = ""):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        })
        self.gh_token = gh_token
        self.gh_headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Universal-Web3-MCP-LeadScraper/1.0"
        }
        if self.gh_token:
            self.gh_headers["Authorization"] = f"token {self.gh_token}"

    def _gh_api_get(self, url: str) -> Optional[dict]:
        req = urllib.request.Request(url, headers=self.gh_headers)
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception:
            return None

    def search_x_social(self, keyword: str) -> List[dict]:
        """Search X (Twitter) bios & posts for target keyword via web search and GitHub dev profiles."""
        leads = []
        query = f"site:x.com {keyword}"
        try:
            url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            resp = self.session.get(url, timeout=12)
            soup = BeautifulSoup(resp.text, 'html.parser')
            for r in soup.find_all('div', class_='result'):
                a = r.find('a', class_='result__url')
                snip = r.find('a', class_='result__snippet')
                if not a:
                    continue
                raw_href = a.get('href', '')
                m = re.search(r'uddg=([^&]+)', raw_href)
                clean_url = urllib.parse.unquote(m.group(1)) if m else raw_href

                if 'x.com/' in clean_url or 'twitter.com/' in clean_url:
                    snip_text = snip.get_text(strip=True) if snip else ''
                    handle_m = re.search(r'(?:x|twitter)\.com/([^/]+)', clean_url)
                    handle = handle_m.group(1) if handle_m else 'Unknown'
                    ignored = ['hashtag', 'search', 'home', 'explore', 'i', 'intent', 'privacy', 'tos', 'tools', 'settings', 'developer', 'docs', 'about']
                    if handle.lower() in ignored:
                        continue
                    email = extract_clean_email(snip_text)
                    gh_link = extract_github_profile_link(snip_text)
                    title = f"X Post/Bio by @{handle}"
                    if gh_link:
                        title += f" [GitHub: {gh_link}]"
                    title += f": {snip_text[:70]}"

                    pitch = generate_cold_pitch(keyword, title, f"@{handle}", "x_social")
                    leads.append({
                        "source": "x_social",
                        "author": f"@{handle}",
                        "email": email,
                        "repo_title": title,
                        "url": clean_url,
                        "niche": keyword,
                        "draft_pitch": pitch
                    })
        except Exception as e:
            print(f"    [WARN] X Search error for '{keyword}': {e}")

        # GitHub API User Search for twitter_username
        if self.gh_token:
            try:
                enc_kw = urllib.parse.quote(keyword)
                u_data = self._gh_api_get(f"https://api.github.com/search/users?q={enc_kw}&per_page=15")
                if u_data and "items" in u_data:
                    for item in u_data["items"]:
                        u_login = item.get("login")
                        u_info = self._gh_api_get(f"https://api.github.com/users/{u_login}")
                        if not u_info:
                            continue
                        tw = u_info.get("twitter_username")
                        bio = u_info.get("bio") or ""
                        email = extract_clean_email(u_info.get("email") or bio)
                        if tw:
                            x_url = f"https://x.com/{tw}"
                            title = f"X Profile @{tw} ({u_login}) - {bio[:70]}"
                            pitch = generate_cold_pitch(keyword, title, f"@{tw}", "x_social")
                            leads.append({
                                "source": "x_social",
                                "author": f"@{tw}",
                                "email": email,
                                "repo_title": title,
                                "url": x_url,
                                "niche": keyword,
                                "draft_pitch": pitch
                            })
            except Exception as e:
                print(f"    [WARN] GH User X search error for '{keyword}': {e}")

        return leads

    def search_linkedin_public(self, keyword: str) -> List[dict]:
        """Search public LinkedIn profiles for target keyword via web search and GitHub profiles."""
        leads = []
        query = f"site:linkedin.com/in {keyword}"
        try:
            url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            resp = self.session.get(url, timeout=12)
            soup = BeautifulSoup(resp.text, 'html.parser')
            for r in soup.find_all('div', class_='result'):
                a = r.find('a', class_='result__url')
                snip = r.find('a', class_='result__snippet')
                if not a:
                    continue
                raw_href = a.get('href', '')
                m = re.search(r'uddg=([^&]+)', raw_href)
                clean_url = urllib.parse.unquote(m.group(1)) if m else raw_href

                if 'linkedin.com/in/' in clean_url:
                    snip_text = snip.get_text(strip=True) if snip else ''
                    li_handle_m = re.search(r'linkedin\.com/in/([a-zA-Z0-9_-]+)', clean_url)
                    handle = li_handle_m.group(1) if li_handle_m else 'Unknown'
                    email = extract_clean_email(snip_text)
                    gh_link = extract_github_profile_link(snip_text)
                    title = f"LinkedIn Profile: {handle}"
                    if gh_link:
                        title += f" [GitHub: {gh_link}]"
                    title += f" - {snip_text[:70]}"

                    pitch = generate_cold_pitch(keyword, title, handle, "linkedin_public")
                    leads.append({
                        "source": "linkedin_public",
                        "author": handle,
                        "email": email,
                        "repo_title": title,
                        "url": clean_url,
                        "niche": keyword,
                        "draft_pitch": pitch
                    })
        except Exception as e:
            print(f"    [WARN] LinkedIn Search error for '{keyword}': {e}")

        if self.gh_token:
            try:
                enc_kw = urllib.parse.quote(keyword)
                u_data = self._gh_api_get(f"https://api.github.com/search/users?q={enc_kw}&per_page=15")
                if u_data and "items" in u_data:
                    for item in u_data["items"]:
                        u_login = item.get("login")
                        u_info = self._gh_api_get(f"https://api.github.com/users/{u_login}")
                        if not u_info:
                            continue
                        bio = u_info.get("bio") or ""
                        blog = u_info.get("blog") or ""
                        full_text = f"{bio} {blog}"
                        email = extract_clean_email(u_info.get("email") or bio)
                        li_m = re.search(r'https?://(?:www\.)?linkedin\.com/in/([a-zA-Z0-9_-]+)', full_text)
                        if li_m:
                            li_handle = li_m.group(1)
                            li_url = f"https://www.linkedin.com/in/{li_handle}"
                            title = f"LinkedIn Profile: {li_handle} ({u_login}) - {bio[:70]}"
                            pitch = generate_cold_pitch(keyword, title, li_handle, "linkedin_public")
                            leads.append({
                                "source": "linkedin_public",
                                "author": li_handle,
                                "email": email,
                                "repo_title": title,
                                "url": li_url,
                                "niche": keyword,
                                "draft_pitch": pitch
                            })
            except Exception as e:
                print(f"    [WARN] GH User LinkedIn search error for '{keyword}': {e}")

        return leads

    def search_reddit_public(self, keyword: str) -> List[dict]:
        """Search public Reddit developer threads for target keyword."""
        leads = []
        query = f"site:reddit.com/r/ {keyword}"
        try:
            url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            resp = self.session.get(url, timeout=12)
            soup = BeautifulSoup(resp.text, 'html.parser')
            for r in soup.find_all('div', class_='result'):
                a = r.find('a', class_='result__url')
                snip = r.find('a', class_='result__snippet')
                if not a:
                    continue
                raw_href = a.get('href', '')
                m = re.search(r'uddg=([^&]+)', raw_href)
                clean_url = urllib.parse.unquote(m.group(1)) if m else raw_href

                if 'reddit.com/r/' in clean_url:
                    snip_text = snip.get_text(strip=True) if snip else ''
                    author_m = re.search(r'reddit\.com/r/[^/]+/comments/[^/]+/([^/]+)', clean_url)
                    author = author_m.group(1) if author_m else 'reddit_dev'
                    email = extract_clean_email(snip_text)
                    title = f"Reddit Post: {snip_text[:70]}"
                    pitch = generate_cold_pitch(keyword, title, author, "reddit_public")
                    leads.append({
                        "source": "reddit_public",
                        "author": author,
                        "email": email,
                        "repo_title": title,
                        "url": clean_url,
                        "niche": keyword,
                        "draft_pitch": pitch
                    })
        except Exception as e:
            print(f"    [WARN] Reddit Search error for '{keyword}': {e}")
        return leads

    def search_communities(self, keyword: str) -> List[dict]:
        """Search public Discord & Telegram dev communities for target keywords."""
        leads = []
        queries = [
            ("telegram_public", f"site:t.me {keyword}"),
            ("discord_public", f"site:discord.gg {keyword}")
        ]
        for src, q in queries:
            try:
                url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(q)}"
                resp = self.session.get(url, timeout=10)
                soup = BeautifulSoup(resp.text, 'html.parser')
                for r in soup.find_all('div', class_='result'):
                    a = r.find('a', class_='result__url')
                    snip = r.find('a', class_='result__snippet')
                    if not a:
                        continue
                    raw_href = a.get('href', '')
                    m = re.search(r'uddg=([^&]+)', raw_href)
                    clean_url = urllib.parse.unquote(m.group(1)) if m else raw_href
                    snip_text = snip.get_text(strip=True) if snip else ''
                    handle = clean_url.split('/')[-1] or 'community'
                    email = extract_clean_email(snip_text)
                    title = f"Dev Community ({src}): {handle} - {snip_text[:70]}"
                    pitch = generate_cold_pitch(keyword, title, handle, src)
                    leads.append({
                        "source": src,
                        "author": handle,
                        "email": email,
                        "repo_title": title,
                        "url": clean_url,
                        "niche": keyword,
                        "draft_pitch": pitch
                    })
                time.sleep(1.0)
            except Exception as e:
                print(f"    [WARN] Community search error for '{q}': {e}")

        return leads

def fetch_devto_leads(topic: str, max_pages: int = 2) -> List[dict]:
    """Search Dev.to API for technical developer articles and profiles."""
    leads = []
    headers = {"User-Agent": "Universal-Web3-MCP-LeadScraper/1.0"}
    tag = topic.lower().replace("-", "")
    p_limit = min(max_pages, 20)
    for page in range(1, p_limit + 1):
        url = f"https://dev.to/api/articles?tag={tag}&per_page=50&page={page}"
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                articles = json.loads(resp.read().decode("utf-8"))
                if not isinstance(articles, list) or not articles:
                    break
                for art in articles:
                    author_info = art.get("user", {})
                    author = author_info.get("name") or author_info.get("username") or "Unknown"
                    title = art.get("title", "")
                    art_url = art.get("url", "")
                    body = art.get("description", "") + " " + (art.get("readable_publish_date") or "")
                    email = extract_clean_email(body)
                    gh_username = author_info.get("github_username")
                    if gh_username:
                        title += f" [GitHub: https://github.com/{gh_username}]"
                    pitch = generate_cold_pitch(topic, title, author, "devto_article")
                    leads.append({
                        "source": "devto_article",
                        "author": author,
                        "email": email,
                        "repo_title": title,
                        "url": art_url,
                        "niche": topic,
                        "draft_pitch": pitch
                    })
        except Exception as e:
            print(f"[WARN] Dev.to Search error for {topic}: {e}")
            break
    return leads

def fetch_hackernews_leads(topic: str, max_pages: int = 2) -> List[dict]:
    """Search HackerNews via Algolia API for forum leads."""
    leads = []
    headers = {"User-Agent": "Universal-Web3-MCP-LeadScraper/1.0"}
    p_limit = min(max_pages, 50)
    for page in range(0, p_limit):
        query_enc = urllib.parse.quote(topic)
        url = f"https://hn.algolia.com/api/v1/search?query={query_enc}&hitsPerPage=50&page={page}"
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                hits = data.get("hits", [])
                for hit in hits:
                    author = hit.get("author") or "Unknown"
                    title = hit.get("title") or hit.get("story_title") or f"HN Post by {author}"
                    item_id = hit.get("objectID")
                    item_url = hit.get("url") or f"https://news.ycombinator.com/item?id={item_id}"
                    text = hit.get("story_text") or hit.get("comment_text") or ""

                    email = extract_clean_email(text)
                    pitch = generate_cold_pitch(topic, title, author, "hn_forum")

                    leads.append({
                        "source": "hn_forum",
                        "author": author,
                        "email": email,
                        "repo_title": title,
                        "url": item_url,
                        "niche": topic,
                        "draft_pitch": pitch
                    })
        except Exception as e:
            print(f"[WARN] HN Search error for {topic}: {e}")
            break
    return leads

def save_leads_to_db(leads: List[dict], db_path: str = DB_PATH) -> Tuple[int, int]:
    """Save leads into SQLite DB, ignoring duplicates on URL."""
    conn = init_db(db_path)
    cur = conn.cursor()
    inserted = 0
    skipped = 0

    for lead in leads:
        try:
            cur.execute("""
                INSERT INTO mcp_leads (source, author, email, repo_title, url, niche, draft_pitch)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                lead["source"],
                lead["author"],
                lead.get("email", ""),
                lead["repo_title"],
                lead["url"],
                lead["niche"],
                lead["draft_pitch"]
            ))
            inserted += 1
        except sqlite3.IntegrityError:
            skipped += 1

    conn.commit()
    conn.close()
    return inserted, skipped

def get_db_stats(db_path: str = DB_PATH) -> dict:
    """Query DB stats for reporting."""
    if not os.path.exists(db_path):
        return {"total_leads": 0, "leads_with_email": 0, "by_niche": {}, "by_source": {}}
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM mcp_leads")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM mcp_leads WHERE email IS NOT NULL AND email != ''")
    with_email = cur.fetchone()[0]

    cur.execute("SELECT niche, COUNT(*) FROM mcp_leads GROUP BY niche")
    by_niche = dict(cur.fetchall())

    cur.execute("SELECT source, COUNT(*) FROM mcp_leads GROUP BY source")
    by_source = dict(cur.fetchall())

    conn.close()
    return {
        "total_leads": total,
        "leads_with_email": with_email,
        "by_niche": by_niche,
        "by_source": by_source
    }

def print_milestone_report(stats: dict):
    """Print clean milestone report."""
    total = stats["total_leads"]
    emails = stats["leads_with_email"]
    print("\n" + "=" * 70)
    print(f"  🔥 PROGRESS MILESTONE REPORT 🔥")
    print(f"  Total Leads in Database:     {total:,}")
    print(f"  Verified Developer Emails:   {emails:,} / 10,000 Goal ({emails/10000*100:.1f}%)")
    print("=" * 70)

def run_lead_generation(topics: List[str] = TARGET_TOPICS, social_keywords: List[str] = SOCIAL_KEYWORDS, max_pages: int = 2):
    """Execute complete lead generation cycle across GitHub, HackerNews, Dev.to, Reddit, and Social Media platforms."""
    token = get_github_token()
    print(f"[*] Starting Scaled Lead Generation Engine (GitHub + Dev.to + HN + Social Media)...")
    print(f"[*] GitHub Token Active: {'YES' if token else 'NO (Rate limited to 60 req/hr)'}")
    print(f"[*] Target Niche Topics ({len(topics)}): {', '.join(topics[:8])}... (+{len(topics)-8} more)")
    print(f"[*] Social Media Keywords ({len(social_keywords)}): {', '.join(social_keywords)}")
    print(f"[*] Max Pages per topic/source: {max_pages}")
    print("=" * 70)

    gh_scraper = GitHubLeadScraper(token)
    social_scraper = SocialMediaLeadScraper(token)
    total_inserted = 0

    # Retrieve existing URLs to skip duplicates immediately
    existing_urls = get_existing_urls()
    print(f"[*] Loaded {len(existing_urls):,} existing lead URLs from database.")

    # 1. GitHub, Dev.to & HackerNews Niche Lead Scrapes
    print("\n[SECTION 1: GitHub, Dev.to & HackerNews Deep Scrapes]")
    for topic in topics:
        print(f"\n[+] Hunting niche: {topic}")
        topic_leads = []

        repos = gh_scraper.search_repositories(topic, max_pages=max_pages, existing_urls=existing_urls)
        print(f"    - GitHub Repos:     {len(repos)}")
        topic_leads.extend(repos)

        commits = gh_scraper.search_commits(topic, max_pages=max_pages, existing_urls=existing_urls)
        print(f"    - GitHub Commits:   {len(commits)}")
        topic_leads.extend(commits)

        issues = gh_scraper.search_issues_prs(topic, max_pages=max_pages, existing_urls=existing_urls)
        print(f"    - GitHub Issues/PRs:{len(issues)}")
        topic_leads.extend(issues)

        users = gh_scraper.search_users(topic, max_pages=max_pages, existing_urls=existing_urls)
        print(f"    - GitHub Developers:{len(users)}")
        topic_leads.extend(users)

        devto_leads = fetch_devto_leads(topic, max_pages=max_pages)
        print(f"    - Dev.to Articles:  {len(devto_leads)}")
        topic_leads.extend(devto_leads)

        hn_leads = fetch_hackernews_leads(topic, max_pages=max_pages)
        print(f"    - HackerNews:       {len(hn_leads)}")
        topic_leads.extend(hn_leads)

        ins, skip = save_leads_to_db(topic_leads)
        total_inserted += ins
        print(f"    => Saved {ins} new leads (Skipped {skip} duplicates)")

    # 2. Social Media & Community Scrapes (X, LinkedIn, Reddit, Discord, Telegram)
    print("\n[SECTION 2: Social Media Platforms (X, LinkedIn, Reddit, Discord, Telegram)]")
    for kw in social_keywords:
        print(f"\n[+] Searching Social Keyword: '{kw}'")
        social_leads = []

        x_results = social_scraper.search_x_social(kw)
        print(f"    - X (Twitter) Bios & Posts: {len(x_results)}")
        social_leads.extend(x_results)

        li_results = social_scraper.search_linkedin_public(kw)
        print(f"    - LinkedIn Profiles:       {len(li_results)}")
        social_leads.extend(li_results)

        reddit_results = social_scraper.search_reddit_public(kw)
        print(f"    - Reddit Developer Threads:{len(reddit_results)}")
        social_leads.extend(reddit_results)

        comm_results = social_scraper.search_communities(kw)
        print(f"    - Dev Communities:          {len(comm_results)}")
        social_leads.extend(comm_results)

        ins, skip = save_leads_to_db(social_leads)
        total_inserted += ins
        print(f"    => Saved {ins} new social media leads (Skipped {skip} duplicates)")

    stats = get_db_stats()
    print_milestone_report(stats)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Continuous High-Capacity Lead Scraper for Web3 MCP & Social Media")
    parser.add_argument("--pages", type=int, default=2, help="Max search pages per topic/source")
    parser.add_argument("--stats", action="store_true", help="Print current database stats and exit")
    parser.add_argument("--continuous", action="store_true", help="Run continuous scaling loops until target lead volume reached")
    parser.add_argument("--target-emails", type=int, default=10000, help="Target verified email count for continuous loop")
    args = parser.parse_args()

    if args.stats:
        stats = get_db_stats()
        print(json.dumps(stats, indent=2))
    elif args.continuous:
        print(f"[*] Launching Continuous Lead Scaling Loop (Target: {args.target_emails:,} verified emails)...")
        iteration = 1
        while True:
            stats = get_db_stats()
            emails = stats["leads_with_email"]
            if emails >= args.target_emails:
                print(f"[SUCCESS] Reached target of {args.target_emails:,} verified emails!")
                break
            print(f"\n==================== LOOP ITERATION #{iteration} (Current Verified Emails: {emails:,}) ====================")
            run_lead_generation(TARGET_TOPICS, SOCIAL_KEYWORDS, max_pages=args.pages)
            iteration += 1
            time.sleep(5)
    else:
        run_lead_generation(TARGET_TOPICS, SOCIAL_KEYWORDS, max_pages=args.pages)
