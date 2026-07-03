#!/usr/bin/env python3
import urllib.request
import urllib.parse
import json
import ssl
import sys

def fetch_funded_issues():
    # We query the GitHub Search API directly for issues containing Polar.sh badges
    query = 'polar.sh pledge is:issue is:open'
    encoded_query = urllib.parse.quote(query)
    url = f"https://api.github.com/search/issues?q={encoded_query}"
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    context = ssl._create_unverified_context()
    
    try:
        print("Polling GitHub Search API for issues with Polar.sh badges...")
        with urllib.request.urlopen(req, context=context, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            
        results = data.get("items", [])
        if not results:
            print("No active funded issues found via GitHub search.")
            return
            
        print(f"Found {len(results)} active Polar-badged issues on GitHub.\n")
        print(f"{'Repository':<35} | {'Issue Title'}")
        print("-" * 80)
        
        count = 0
        for issue in results:
            if "pull_request" in issue:
                continue # Skip pull requests
            
            body = issue.get("body", "") or ""
            if "polar.sh" not in body.lower():
                continue # Skip issues without a polar link in the main description

            title = issue.get("title", "")
            if len(title) > 40:
                title = title[:37] + "..."
                
            repo_url = issue.get("repository_url", "")
            repo_full = "/".join(repo_url.split("/")[-2:])
            if len(repo_full) > 35:
                repo_full = repo_full[:32] + "..."
                
            print(f"{repo_full:<35} | {title} (#{issue.get('number')})")
            count += 1
            if count >= 10:
                break
            
        if count == 0:
            print("No actually funded open issues (excluding PRs and false positives) found in this page.")
            
        print("-" * 80)

        print("View full results by visiting their respective GitHub repository pages.")
            
    except Exception as e:
        print(f"Error fetching issues from GitHub Search: {e}", file=sys.stderr)

if __name__ == "__main__":
    fetch_funded_issues()
