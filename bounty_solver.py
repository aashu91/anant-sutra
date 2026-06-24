#!/usr/bin/env python3
import sys
import os
import re
import json
import urllib.request
import urllib.parse
import ssl
import subprocess
import shutil
import time

COLOR_RESET = "\033[0m"
COLOR_YELLOW = "\033[93m"
COLOR_GREEN = "\033[92m"
COLOR_BLUE = "\033[94m"
COLOR_CYAN = "\033[96m"
COLOR_RED = "\033[91m"

WORKSPACE_DIR = "/data/data/com.termux/files/home/sutralang/temp_workspace"
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "sutra-agent:latest"

def log(msg, color=COLOR_BLUE):
    print(f"{color}[BountySolver] {msg}{COLOR_RESET}")

def get_github_pat_and_info():
    # Extract GitHub Personal Access Token and username from git remote URL
    try:
        res = subprocess.run(["git", "remote", "-v"], capture_output=True, text=True, cwd="/data/data/com.termux/files/home/sutralang")
        out = res.stdout
        
        # Match pattern: https://<username>:<token>@github.com/...
        user_token_match = re.search(r'https://([^:]+):([^@]+)@github\.com', out)
        if user_token_match:
            username = user_token_match.group(1).strip()
            token = user_token_match.group(2).strip()
            return token, username
    except Exception as e:
        log(f"Warning: Failed to extract PAT from remote: {e}", COLOR_YELLOW)
    return None, None

def fetch_issue_details(repo_full, issue_number, token=None):
    # Fetch issue body and title from GitHub REST API
    url = f"https://api.github.com/repos/{repo_full}/issues/{issue_number}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    if token:
        req.add_header('Authorization', f'token {token}')
        
    context = ssl._create_unverified_context()
    try:
        with urllib.request.urlopen(req, context=context, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
        return data.get("title", ""), data.get("body", "")
    except Exception as e:
        log(f"Error fetching issue details: {e}", COLOR_RED)
        return None, None

def fork_repository(repo_full, token):
    log(f"Forking repository '{repo_full}' to your account...", COLOR_YELLOW)
    url = f"https://api.github.com/repos/{repo_full}/forks"
    req = urllib.request.Request(url, data=b"", headers={
        'User-Agent': 'Mozilla/5.0',
        'Authorization': f'token {token}',
        'Content-Type': 'application/json'
    })
    context = ssl._create_unverified_context()
    try:
        with urllib.request.urlopen(req, context=context, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
        log("Fork request sent successfully.", COLOR_GREEN)
        # Sleep to allow GitHub to populate the new repository fork
        log("Waiting 6 seconds for GitHub to finish forking...", COLOR_YELLOW)
        time.sleep(6)
        return data.get("name")
    except Exception as e:
        log(f"Failed to fork repository: {e}", COLOR_RED)
        return None

def detect_test_command(repo_path):
    # Auto-detect language and test framework
    if os.path.exists(os.path.join(repo_path, "package.json")):
        return "npm test"
    elif os.path.exists(os.path.join(repo_path, "pytest.ini")) or os.path.exists(os.path.join(repo_path, "conftest.py")):
        return "pytest"
    elif os.path.exists(os.path.join(repo_path, "Cargo.toml")):
        return "cargo test"
    elif os.path.exists(os.path.join(repo_path, "go.mod")):
        return "go test ./..."
    return None

def generate_patch_with_ollama(issue_title, issue_body, codebase_context, target_file):
    # Queries local Ollama for the patch, using Ponytail rules
    prompt = f"""You are a professional software engineer following the 'Ponytail' philosophy (minimalism, YAGNI, standard library first, native platform features, zero boilerplate, minimal changes). Fix the following issue in the codebase.

Issue Title: {issue_title}
Issue Description:
{issue_body}

File to modify: {target_file}
Current File Content / Context:
{codebase_context}

Ponytail Rules for your changes:
1. Do not add any new dependencies or unnecessary abstractions.
2. Use standard library or existing dependencies to solve the issue.
3. Write the minimum amount of code that safely works.
4. Keep modifications strictly contained to the target area.

Provide ONLY the modified file contents. Do not explain anything, do not output any markdown blocks, simply output the raw file contents that should replace the current file.
"""
    data = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1}
    }
    
    req = urllib.request.Request(OLLAMA_API_URL, data=json.dumps(data).encode('utf-8'))
    req.add_header('Content-Type', 'application/json')
    
    try:
        log("Querying local Ollama model for code modification...", COLOR_YELLOW)
        with urllib.request.urlopen(req, timeout=90) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            return res_data.get("response", "").strip()
    except Exception as e:
        log(f"Error calling local Ollama server: {e}", COLOR_RED)
        return None

def run_local_tests(repo_path, test_cmd):
    log(f"Running validation tests: {test_cmd}...", COLOR_YELLOW)
    try:
        res = subprocess.run(test_cmd, shell=True, cwd=repo_path, capture_output=True, text=True, timeout=30)
        if res.returncode == 0:
            log("Test suite verification: PASSED (Exit Code 0)", COLOR_GREEN)
            return True
        else:
            log(f"Test suite verification: FAILED (Exit Code {res.returncode})", COLOR_RED)
            print(res.stderr)
            return False
    except subprocess.TimeoutExpired:
        log("Test suite execution timed out.", COLOR_RED)
        return False
    except Exception as e:
        log(f"Failed to execute tests: {e}", COLOR_RED)
        return False

def submit_pull_request(repo_full, branch_name, title, token, username):
    # Submit PR via GitHub REST API from username:branch_name to upstream repo_full:main
    url = f"https://api.github.com/repos/{repo_full}/pulls"
    data = {
        "title": f"fix: {title}",
        "body": "Automated patch submitted via Sutra BountySolver agent loop.",
        "head": f"{username}:{branch_name}",
        "base": "main"
    }
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={
        'User-Agent': 'Mozilla/5.0',
        'Authorization': f'token {token}',
        'Content-Type': 'application/json'
    })
    
    context = ssl._create_unverified_context()
    try:
        with urllib.request.urlopen(req, context=context, timeout=10) as response:
            res_data = json.loads(response.read().decode('utf-8'))
        log(f"Pull Request submitted successfully! URL: {res_data.get('html_url')}", COLOR_GREEN)
        return True
    except Exception as e:
        log(f"Failed to submit Pull Request: {e}", COLOR_RED)
        return False

def main():
    if len(sys.argv) < 4:
        print("Usage: python bounty_solver.py <org/repo> <issue_number> <relative_target_file>")
        sys.exit(1)
        
    repo_full = sys.argv[1]
    issue_number = sys.argv[2]
    target_file = sys.argv[3]
    
    token, username = get_github_pat_and_info()
    if not token or not username:
        log("Error: GitHub credentials not found in remote config. Authenticate git first.", COLOR_RED)
        sys.exit(1)
        
    log(f"Targeting: {repo_full} | Issue #{issue_number}")
    
    # 1. Fetch details
    title, body = fetch_issue_details(repo_full, issue_number, token)
    if not title:
        sys.exit(1)
        
    # 2. Fork the repository
    repo_name = fork_repository(repo_full, token)
    if not repo_name:
        log("Cannot proceed without creating repository fork.", COLOR_RED)
        sys.exit(1)
        
    # 3. Setup workspace and clone fork
    if os.path.exists(WORKSPACE_DIR):
        shutil.rmtree(WORKSPACE_DIR)
    os.makedirs(WORKSPACE_DIR, exist_ok=True)
    
    clone_url = f"https://x-access-token:{token}@github.com/{username}/{repo_name}.git"
    log(f"Cloning fork repository into temporary workspace...")
    try:
        subprocess.run(["git", "clone", clone_url, WORKSPACE_DIR], check=True, capture_output=True)
    except Exception as e:
        log(f"Failed to clone repository fork: {e}", COLOR_RED)
        sys.exit(1)
        
    # 4. Read current file content
    target_file_path = os.path.join(WORKSPACE_DIR, target_file)
    if not os.path.exists(target_file_path):
        log(f"Error: Target file '{target_file}' not found in cloned repository.", COLOR_RED)
        sys.exit(1)
        
    with open(target_file_path, 'r', encoding='utf-8') as f:
        file_content = f.read()
        
    # 5. Generate patch using Ollama
    new_content = generate_patch_with_ollama(title, body, file_content, target_file)
    if not new_content:
        sys.exit(1)
        
    # 6. Apply patch
    with open(target_file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    log("Patch applied to local file.", COLOR_GREEN)
    
    # 7. Detect and run tests
    test_cmd = detect_test_command(WORKSPACE_DIR)
    if test_cmd:
        tests_passed = run_local_tests(WORKSPACE_DIR, test_cmd)
        if not tests_passed:
            log("Cancelling PR submission due to failed verification tests.", COLOR_YELLOW)
            sys.exit(1)
    else:
        log("No test framework detected. Skipping verification tests.", COLOR_YELLOW)
        
    # 8. Push branch to fork and submit PR
    branch_name = f"fix-issue-{issue_number}"
    try:
        subprocess.run(["git", "checkout", "-b", branch_name], cwd=WORKSPACE_DIR, check=True, capture_output=True)
        subprocess.run(["git", "add", target_file], cwd=WORKSPACE_DIR, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", f"fix: solve issue #{issue_number}"], cwd=WORKSPACE_DIR, check=True, capture_output=True)
        
        log(f"Pushing branch '{branch_name}' to fork origin...")
        subprocess.run(["git", "push", "origin", branch_name], cwd=WORKSPACE_DIR, check=True, capture_output=True)
    except Exception as e:
        log(f"Git commit/push operation failed: {e}", COLOR_RED)
        sys.exit(1)
        
    # Submit PR back to upstream repo
    submit_pull_request(repo_full, branch_name, title, token, username)

if __name__ == "__main__":
    main()
