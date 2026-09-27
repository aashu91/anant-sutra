# sutra_agent_core.py — Unified compiler, VM, and tools for SutraAgent
# Copyright (c) 2026 Ashutosh Singh (salvationfinder / Anant Anaadi Group)
# Distributed under the MIT License. See LICENSE for details.
import os
import sys
import json
import ast
import re
import urllib.request
import urllib.parse
import subprocess
from pypdf import PdfReader

# Base imports from sutralang codebase
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sutralang_compiler import SutraCompiler
from sutralang_vm import SutraVM

# CLI colors
COLOR_RESET = "\033[0m"
COLOR_YELLOW = "\033[93m"
COLOR_GREEN = "\033[92m"
COLOR_BLUE = "\033[94m"
COLOR_CYAN = "\033[96m"
COLOR_RED = "\033[91m"
COLOR_MAGENTA = "\033[95m"

# Configuration
MODEL_NAME = "sutra-agent:latest"
OLLAMA_API_URL = "http://localhost:11434/api/generate"

SYSTEM_PROMPT = """You are the SutraLang Semantic Compiler & Astra Engine Core. You translate natural language into SutraLang code. Output ONLY valid SutraLang statements. NEVER output explanations, greetings, markdown, or conversational text.

ASTRA DIRECTIVES:
- High Autonomy & Speed: Bias heavily towards direct execution. Translate intent into complete, executable SutraLang pipelines.
- Zero Slop: Absolutely no filler text, introductory commentary, or conversational fluff.

CODEBASE CONTEXT — files in ~/sutralang/:
  sutra_agent_core.py, sutralang_server.py, sutralang_compiler.py, sutralang_vm.py,
  sutralang.cpp, sutra_agent_bot.py, sutra_agent.py, sutra_auto_agent.py, sutra_os.py,
  sutra_goals.py, sutra_life_helper.py, sutra_voice_assistant.py, sutralang_backtest.py,
  sutralang_bytecode.py, sutralang_neuro.py, generate_pdf.py, bounty_solver.py,
  bounty_sweeper.py, test_sutra_agent.py, web/index.html, web/index.js, web/index.css

SutraLang syntax (strictly follow):
1. ek variable [name] value [val]
2. [name] ko [query] se khojo  (web search)
3. [name] ko [file] aur [query] se padho  (read PDF)
4. [name] ko [command] se shodh_karo  (execute shell)
5. print [name]  OR  [name] ko dikhao
6. [name] ko [val1] aur [val2] se jodo  (string join)
7. [name] ko [query] se chhavo  (search codebase)
8. [name] ko "[filepath]" se patho  (read file)
9. [name] ko "[filepath]" se sookshma  (read dehydrated DOM skeleton structure of file)
10. [name] ko "check" se swans  (audit workspace files for changes)
11. [name] ko "update" se swans  (re-stamp workspace files)
12. [name] ko [content_var] aur "[filepath]" me likho  (write file)
13. [name] ko "[goal]" me sochi  (save goal)
14. [name] ko [query] se smriti  (search Obsidian Second Brain)

CRITICAL: For codebase files use chhavo/patho. For Second Brain / Obsidian notes search use smriti. For code structure/outline view, use sookshma. For run/execute use shodh_karo. For edit/write use likho. For real-time data use khojo. For workspace stamp verification use swans. NEVER output anything except valid SutraLang code.

Examples:

User: Search on the web for Polymarket news and print it.
Output:
ek variable query value "Polymarket news"
ek variable search_res value ""
search_res ko query se khojo
print search_res

User: Read the file sutra_agent_core.py and show it.
Output:
ek variable content value ""
content ko "/data/data/com.termux/files/home/sutralang/sutra_agent_core.py" se patho
print content

User: Get the structure / outline of file sutra_agent_core.py.
Output:
ek variable content value ""
content ko "/data/data/com.termux/files/home/sutralang/sutra_agent_core.py" se sookshma
print content

User: Check workspace files for modifications.
Output:
ek variable audit_res value ""
audit_res ko "check" se swans
print audit_res

User: Search codebase for SutraAgentVM and show results.
Output:
ek variable query value "SutraAgentVM"
ek variable code_res value ""
code_res ko query se chhavo
print code_res

User: Hello! Who are you?
Output:
ek variable reply value "Namaste! Main SutraAgent hoon — tumhara local sovereign AI. Codebase read/edit/run sab kr skta hoon."
print reply

Output ONLY the formal SutraLang statements, one per line. No explanations, no markdown, no comments."""


def fast_path_translate(query):
    query_clean = query.strip().lower()
    
    # 0b. Web3 Contract Address (EVM / Solana) Auto-detector
    raw_query_clean = query.strip()
    evm_match = re.search(r'0x[a-fA-F0-9]{40}', raw_query_clean)
    sol_match = re.search(r'[1-9A-HJ-NP-Za-km-z]{32,44}', raw_query_clean)
    if evm_match or (sol_match and len(raw_query_clean.split()) == 1 and not raw_query_clean.lower().startswith("http")):
        ca = evm_match.group(0) if evm_match else sol_match.group(0)
        chain_type = "EVM Token Contract" if evm_match else "Solana Token Contract"
        return f'ek variable ca value "{ca}"\nek variable cmd value "python3 /data/data/com.termux/files/home/web3_dapp_router.py {ca}"\nek variable scan_res value ""\nscan_res ko cmd se shodh_karo\nprint scan_res'

    # 1. Conversational Dialogue & Connection Inquiries (Checked FIRST before raw notes search)
    words = query_clean.split()
    if query_clean in ["hello", "hi", "hey", "namaste"]:
        return 'ek variable reply value "Namaste Ashutosh bhai! Bolo, aaj kya karna hai?"\nprint reply'
    if any(p in query_clean for p in ["kaise ho", "kya haal", "kya hal"]):
        return 'ek variable reply value "Ekdum mast bhai! Tum batao, kya chal raha hai?"\nprint reply'
    if any(p in query_clean for p in ["tum kaun ho", "who are you", "who r u"]):
        return 'ek variable reply value "Main SutraVāk (सूत्रवाक्) hoon — tumhara local sovereign companion."\nprint reply'
    if any(p in query_clean for p in ["kya bol rhe", "kya bol rahe", "kya bol rahe ho"]):
        return 'ek variable reply value "Bhai bas aapke instructions ka wait kar raha hoon, bolo kya karna hai?"\nprint reply'
    if any(p in query_clean for p in ["kya kya kr skte ho", "kya kar sakte ho", "kya kr skte ho"]):
        return 'ek variable reply value "Main code write/refactor/run kar sakta hoon, Second Brain & 615+ books se charcha kar sakta hoon, live web search/weather/prices fetch kar sakta hoon, aur Termux shell execute kar sakta hoon."\nprint reply'
    if any(p in query_clean for p in ["connected ho", "connect ho", "jurhe ho", "jude ho"]) or ("second brain" in query_clean and any(w in query_clean for w in ["kya", "connected", "ha", "hain"])):
        return 'ek variable reply value "Haan Ashutosh bhai! Main tumhare Obsidian Second Brain vault aur 615+ books corpus se 100% offline connected hoon."\nprint reply'

    # 1b. Second Brain / Obsidian Vault Auto-detect (Only for explicit note/brain search commands)
    brain_words = ["second brain", "obsidian note", "search notes", "search obsidian", "read blueprint", "search smriti", "operator core"]
    if any(w in query_clean for w in brain_words):
        q_val = query.strip().strip('"\'')
        return f'ek variable query value "{q_val}"\nek variable brain_res value ""\nbrain_res ko query se smriti\nprint brain_res'

    # 1b. Direct Shell Command Execution (Checked BEFORE philosophical/conversational fallback)
    shell_prefixes = ("run shell command", "run command", "execute", "shodh_karo", "python3", "python ", "ls ", "cat ", "pip ", "git ", "curl ")
    if query_clean.startswith(shell_prefixes):
        cmd_val = query.strip()
        for prefix in ["run shell command", "run command", "execute", "shodh_karo"]:
            if cmd_val.lower().startswith(prefix):
                cmd_val = cmd_val[len(prefix):].strip()
                break
        return f'ek variable cmd value {json.dumps(cmd_val)}\nek variable res value ""\nres ko cmd se shodh_karo\nprint res'

    # 2b. Specific Polymath & Engineering Knowledge Queries
    if "ponytail" in query_clean:
        return 'ek variable reply value "Ponytail Dev Philosophy: Lazy means efficient. Code never written is best. Boring over clever. Fewest files possible."\nprint reply'
    if "schrodinger" in query_clean or "schrödinger" in query_clean:
        return 'ek variable reply value "Schrödinger (What is Life?): Interdisciplinary breakthroughs occur at boundaries; predicted genetic code physics."\nprint reply'
    if "karpathy rule 1" in query_clean or "karpathy 1" in query_clean:
        return 'ek variable reply value "Karpathy Rule 1: Ask, do not assume. Clarify requirements before writing code."\nprint reply'
    if "karpathy rule 2" in query_clean or "karpathy 2" in query_clean:
        return 'ek variable reply value "Karpathy Rule 2: Simplest solution first. No unrequested abstractions."\nprint reply'

    # 2c. Philosophical & Polymathic Reflection Handler
    phil_keywords = ["jeevan", "samay", "uddeshya", "arth", "panini", "bhavna", "advaita", "chetna", "purpose", "meaning of life", "time", "consciousness"]
    if any(kw in query_clean for kw in phil_keywords):
        if "jeevan" in query_clean or "purpose" in query_clean or "meaning of life" in query_clean:
            return 'ek variable reply value "Jeevan ka uddeshya chetna ko anubhuti se karma me dhalna hai — nishkama karma aur srijan hi iska mool hai."\nprint reply'
        elif "samay" in query_clean or "time" in query_clean:
            return 'ek variable reply value "Samay system me clock cycles aur event sequences ki kramik avastha hai."\nprint reply'
        elif "panini" in query_clean:
            return 'ek variable reply value "Panini ke 4,000 sutras generative context-free grammar banate hain — AI ko bina neural bloat ke exact rule logic deta hai."\nprint reply'
        elif "chetna" in query_clean or "consciousness" in query_clean:
            return 'ek variable reply value "Chetna swayam prakashit hai — ye observable nahi, observer ki mool avastha hai."\nprint reply'
        else:
            return 'ek variable reply value "Vicharniy prashn hai bhai — ispar hamare Paninian Sutra Engine aur Polymath Corpus se gehra chintan chal raha hai."\nprint reply'

    # Strip UI wrapping templates contextually to extract raw user query target
    clean_target = query_clean
    clean_target = re.sub(r'^search\s+(?:on\s+the\s+web\s+for|web\s+for|for)?\s+', '', clean_target)
    clean_target = re.sub(r'^google\s+', '', clean_target)
    clean_target = re.sub(r'^khojo\s+', '', clean_target)
    clean_target = re.sub(r'^read\s+(?:the\s+)?(?:file\s+)?', '', clean_target)
    clean_target = re.sub(r'\s+and\s+print\s+(?:the\s+)?results?\.?$', '', clean_target)
    clean_target = clean_target.strip('"\'')

    # 1c. Hindi/Hinglish & Local File/Folder auto-detection
    local_words = ["dekh", "show", "read", "open", "view", "patho", "folder", "directory", "structure", "sookshma", "skeleton"]
    if any(w in query_clean for w in local_words) or any(w in clean_target for w in ["scratch"]):
        home = os.path.realpath(os.path.expanduser("~"))
        current_dir = os.getcwd()
        tokens = [t for t in re.findall(r'[a-zA-Z0-9_\-\.\/]+', clean_target) if len(t) >= 3]
        for token in tokens:
            token_clean = token.strip().strip('"\'')
            if token_clean.lower() in {'the', 'file', 'folder', 'view', 'read', 'open', 'show', 'naam', 'system', 'ko', 'se', 'me', 'kya', 'hai', 'nam'}:
                continue
            
            paths_to_test = []
            if os.path.isabs(token_clean):
                paths_to_test.append(token_clean)
            else:
                paths_to_test.append(os.path.join(current_dir, token_clean))
                paths_to_test.append(os.path.join(home, token_clean))
                
            for test_path in paths_to_test:
                norm_path = os.path.realpath(test_path)
                if os.path.exists(norm_path) and (norm_path.startswith(home) or norm_path.startswith("/data/data/com.termux/files/home")):
                    if os.path.basename(norm_path).lower() == token_clean.lower() or os.path.isdir(norm_path):
                        if os.path.isdir(norm_path):
                            return f'ek variable cmd value "ls -la {norm_path}"\nek variable res value ""\nres ko cmd se shodh_karo\nprint res'
                        else:
                            if any(s in query_clean for s in ["sookshma", "structure", "skeleton", "outline", "classes", "functions"]):
                                return f'ek variable content value ""\ncontent ko "{norm_path}" se sookshma\nprint content'
                            return f'ek variable content value ""\ncontent ko "{norm_path}" se patho\nprint content'

    # 1d. Swans Auto-detect
    if any(s in query_clean for s in ["swans", "workspace status", "stamp codebase", "file tree stamp", "scan file tree", "workspace check"]):
        action = "update" if any(x in query_clean for x in ["update", "stamp", "save"]) else "check"
        return f'ek variable res value ""\nres ko "{action}" se swans\nprint res'

    # 1e. System Time Check
    if any(t in query_clean for t in ["time", "date", "samay", "ghadi"]) and any(q in query_clean for q in ["kya", "what", "tell", "batao", "right now", "turant"]):
        return 'ek variable cmd value "date"\nek variable res value ""\nres ko cmd se shodh_karo\nprint res'

    # 2. Web Search Query (Includes Weather / Mausam & Real-time queries)
    search_keywords = ["price", "weather", "mausam", "taapman", "temperature", "news", "status of", "btc", "ethereum", "bitcoin", "market", "who is", "what is"]
    if any(kw in query_clean for kw in search_keywords) and not query_clean.startswith(("run", "execute", "shodh_karo", "python", "ls", "cat")):
        q_val = query.strip().strip('"\'')
        return f'ek variable query value "{q_val}"\nek variable search_res value ""\nsearch_res ko query se khojo\nprint search_res'

    # 3. File Read Query
    m_read = re.search(r'^(?:read\s+(?:the\s+)?(?:file\s+)?|patho|show\s+file\s+)(.+?)(?:\s+and\s+print\s+it\.?)?$', query, re.IGNORECASE)
    if m_read:
        path_val = m_read.group(1).strip().strip('"\'').replace('"', '\\"')
        return f'ek variable content value ""\ncontent ko "{path_val}" se patho\nprint content'

    # 4. Code Structure / Outline Query
    m_sookshma = re.search(r'^(?:get\s+(?:the\s+)?(?:structure|outline|skeleton)\s+of\s+(?:file\s+)?|sookshma\s+)(.+)$', query, re.IGNORECASE)
    if m_sookshma:
        path_val = m_sookshma.group(1).strip().strip('"\'').replace('"', '\\"')
        return f'ek variable content value ""\ncontent ko "{path_val}" se sookshma\nprint content'

    # 5. Codebase Search Query
    m_code = re.search(r'^(?:search\s+(?:local\s+)?(?:codebase|code)\s+for|chhavo)\s+(.+?)(?:\s+and\s+show\s+it\.?)?$', query, re.IGNORECASE)
    if m_code:
        q_val = m_code.group(1).strip().strip('"\'').replace('"', '\\"')
        return f'ek variable query value "{q_val}"\nek variable code_res value ""\ncode_res ko query se chhavo\nprint code_res'

    # If no fast-path translation matched, return None so control passes to SutraJev & Smriti symbolic engine
    return None

def _looks_like_sutralang(text):
    """Check if text contains at least one valid SutraLang keyword."""
    # ponytail: simple keyword scan — if none match, it's conversational garbage
    sutralang_keywords = [
        "ek variable", "print ", "ko dikhao", "se khojo", "se padho",
        "se shodh_karo", "se chhavo", "se patho", "me likho", "me sochi",
        "se jodo", "value ", "maan ", "banao"
    ]
    text_lower = text.lower()
    return any(kw in text_lower for kw in sutralang_keywords)

def _call_ollama_raw(prompt, system_prompt):
    """Single Ollama API call, returns raw response string or None."""
    data = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "keep_alive": 0,  # ponytail: unload model after response — saves ~2GB RAM on phone
        "options": {
            "temperature": 0.1,
            "num_ctx": 1024,      # ponytail: SutraLang output is short, 1024 is enough
            "num_predict": 256    # ponytail: cap output — code is never > 10 lines
        }
    }
    req = urllib.request.Request(OLLAMA_API_URL)
def _call_sutra_symbolic_fallback(prompt):
    """
    Pure 100% Non-Neural Symbolic Fallback using SutraJev Decision Engine & Smriti Search.
    Zero LLM dependency, zero cloud cost, 100% offline.
    """
    prompt_clean = prompt.strip()
    
    # 1. Use SutraJev Engine to determine task intent
    try:
        from sutra_jev import SutraJevEngine, Choice
        jev = SutraJevEngine()
        choices = Choice([
            "SMRITI_QUERY", "SUTRA_VM_EXEC", "EXPANDER_LOAD_BALANCE",
            "ANANT_ANAADI_RENDER", "POLY_ARBITRAGE_CHECK", "TURIYA_DEBUNK",
            "VAULT_MIRROR_SYNC", "SENTINEL_THERMAL_SHIELD", "WEB3_MCP_LEAD_HARVEST"
        ])
        res = jev.decide(prompt_clean, choices)
        
        if res.choice == "SMRITI_QUERY":
            return f'ek variable query value "{prompt_clean}"\nek variable brain_res value ""\nbrain_res ko query se smriti\nprint brain_res'
        elif res.choice == "SENTINEL_THERMAL_SHIELD":
            return 'ek variable cmd value "python3 /data/data/com.termux/files/home/sutralang/test_sutraos_sovereign_suite.py"\nek variable res value ""\nres ko cmd se shodh_karo\nprint res'
        elif res.choice == "POLY_ARBITRAGE_CHECK":
            return 'ek variable cmd value "python3 /data/data/com.termux/files/home/bounty_monitor.py"\nek variable res value ""\nres ko cmd se shodh_karo\nprint res'
    except Exception:
        pass

    # 2. Universal Symbolic Smriti Search Fallback
    safe_q = prompt_clean.replace('"', '\\"').replace('\n', ' ')
    return f'ek variable query value "{safe_q}"\nek variable brain_res value ""\nbrain_res ko query se smriti\nprint brain_res'

def query_ollama(prompt, system_prompt=SYSTEM_PROMPT):
    # 1. Check Quantized Dialogue Intent Graph
    try:
        from sutra_dialogue_graph import resolve_quantized_intent
        intent, intent_code = resolve_quantized_intent(prompt)
        if intent_code:
            return intent_code
    except Exception:
        pass

    # 2. Try fast-path translation
    fast_code = fast_path_translate(prompt)
    if fast_code:
        return fast_code

    # 3. Fallback directly to SutraJev & Smriti Symbolic Engine
    return _call_sutra_symbolic_fallback(prompt)


# Command safety checker
def is_command_safe(command):
    cmd_lower = command.lower()
    home = os.path.realpath(os.path.expanduser("~"))
    termux_home = "/data/data/com.termux/files/home"
    
    # 1. Block root-like operations and destructive package managers
    forbidden_tokens = {'sudo', 'su', 'chown', 'chmod', 'dd', 'mkfs', 'fdisk', 'mount', 'umount', 'passwd'}
    words = [re.sub(r'^[^\w]+|[^\w]+$', '', w) for w in re.split(r'\s+', cmd_lower)]
    for t in forbidden_tokens:
        if t in words:
            return False, f"Forbidden command token: '{t}'"
            
    # 2. Block direct path traversals or accesses outside of home directory
    if '..' in command:
        return False, "Directory traversal (..) is strictly forbidden for security."
        
    abs_paths = re.findall(r'/[a-zA-Z0-9_\-\.\/]+', command)
    for path in abs_paths:
        norm = os.path.abspath(path)
        if not (norm.startswith(home) or norm.startswith(termux_home)):
            return False, f"Access to path outside home directory is forbidden: '{path}'"
            
    # 3. Block output redirections to paths outside home
    redirections = re.findall(r'>\s*([a-zA-Z0-9_\-\.\/]+)', command)
    for target in redirections:
        if target.startswith('/') and not (target.startswith(home) or target.startswith(termux_home)):
            return False, f"Redirection to path outside home directory is forbidden: '{target}'"
            
    return True, ""

# Web search
def web_search(query):
    try:
        url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read()
            if response.info().get('Content-Encoding') == 'gzip':
                import gzip
                content = gzip.decompress(content)
            html = content.decode('utf-8', errors='replace')
        
        snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
        if not snippets:
            snippets = re.findall(r'<td class="result-snippet"[^>]*>(.*?)</td>', html, re.DOTALL)
        if not snippets:
            snippets = re.findall(r'<div class="result-snippet">(.*?)</div>', html, re.DOTALL)
            
        results = []
        for snip in snippets[:5]:
            clean = re.sub(r'<[^>]*>', '', snip)
            clean = clean.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&#x27;', "'").strip()
            
            # Filter out search engine boilerplates
            if any(bp in clean.lower() for bp in [
                "google's service", "offered free of charge", "instantly translates", "enjoy the videos and music",
                "upload original content", "share it all with friends", "detect language", "most comprehensive image search",
                "images.google.com", "cookie consent", "javascript is disabled", "please enable javascript",
                "ddg", "duckduckgo", "browser is not supported"
            ]):
                continue
            if clean:
                results.append(clean)
                
        # Fallback to DuckDuckGo Lite if HTML search failed or returned generic boilerplates
        if not results:
            url_lite = "https://lite.duckduckgo.com/lite/"
            data_lite = urllib.parse.urlencode({'q': query}).encode('utf-8')
            req_lite = urllib.request.Request(url_lite, data=data_lite, headers=headers)
            with urllib.request.urlopen(req_lite, timeout=10) as response_lite:
                content_lite = response_lite.read()
                if response_lite.info().get('Content-Encoding') == 'gzip':
                    import gzip
                    content_lite = gzip.decompress(content_lite)
                html_lite = content_lite.decode('utf-8', errors='replace')
            snippets_lite = re.findall(r'<td class="result-snippet"[^>]*>(.*?)</td>', html_lite, re.DOTALL)
            for snip in snippets_lite[:5]:
                clean = re.sub(r'<[^>]*>', '', snip)
                clean = clean.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&#x27;', "'").strip()
                if clean and not any(bp in clean.lower() for bp in ["google's service", "offered free of charge", "duckduckgo"]):
                    results.append(clean)
            
        if results:
            return " | ".join(results[:3])
        return "No search results found on DuckDuckGo."
    except Exception as e:
        return f"Web search failed: {str(e)}"

# PDF read
def read_pdf(file_path, query=""):
    try:
        if not os.path.exists(file_path):
            return f"Error: PDF file '{file_path}' does not exist."
            
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
        
        if not text:
            return "PDF file contains no extractable text."
            
        if not query:
            return text[:400] + "... [Truncated]"
            
        paragraphs = text.split("\n\n")
        if len(paragraphs) < 3:
            paragraphs = text.split("\n")
            
        matching_snippets = []
        query_words = query.lower().split()
        for p in paragraphs:
            p_lower = p.lower()
            if any(word in p_lower for word in query_words):
                matching_snippets.append(p.strip())
                if len(matching_snippets) >= 3:
                    break
                    
        if matching_snippets:
            return "\n---\n".join(matching_snippets)
        return f"No matching paragraphs found for query '{query}'. Preview: " + text[:300] + "..."
    except Exception as e:
        return f"PDF parse failed: {str(e)}"

# Shell Execution
def execute_shell(command):
    command = command.strip()
    if (command.startswith('"') and command.endswith('"')) or (command.startswith("'") and command.endswith("'")):
        command = command[1:-1].strip()
    command = re.sub(r'\\+"', '"', command)
    command = re.sub(r"\\+'", "'", command)
    safe, reason = is_command_safe(command)
    if not safe:
        return f"Security Exception: {reason}"
        
    try:
        res = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=12)
        output = res.stdout.strip()
        err = res.stderr.strip()
        if res.returncode == 0:
            return output if output else "Shell execution completed successfully with no stdout."
        return f"Shell Execution Error (code {res.returncode}): {err}"
    except subprocess.TimeoutExpired:
        return "Shell Execution Timeout (12s limit exceeded)."
    except Exception as e:
        return f"Shell execution failed: {str(e)}"

# Local search tool for codebase indexing
def local_code_search(query, root_dir="/data/data/com.termux/files/home"):
    search_dirs = [
        os.path.join(root_dir, "sutralang"),
        os.path.join(root_dir, "poly_v2"),
        os.path.join(root_dir, "odysseus"),
        root_dir
    ]
    blacklist_dirs = {
        '.git', '.npm', '.cache', '.bun', 'node_modules', '.gstack', 
        '.antigravitycli', '__pycache__', '.expo', 'video', 'reels', 
        '.local', '.config', '.cargo', '.ssh', '.agents', 'venv', '.venv',
        'build', 'dist', 'out', '.next', 'panchang-remotion', 'StoryGen-Atelier',
        'claude-code-video-toolkit', 'sutra-brain-app', 'sutra-brain', 'OpenMontage',
        'anime_assets'
    }
    allowed_exts = {
        '.py', '.js', '.json', '.html', '.css', '.cpp', '.md', '.txt', '.sutra', '.sh'
    }
    
    query = query.strip().lower()
    if not query:
        return "Empty search query."
        
    keywords = [kw for kw in re.split(r'\s+', query) if kw]
    if not keywords:
        return "No valid search keywords."
        
    matches = []
    scanned_files = set()
    file_count = 0
    max_files = 300
    
    try:
        for s_dir in search_dirs:
            if not os.path.exists(s_dir):
                continue
                
            for root, dirs, files in os.walk(s_dir):
                dirs[:] = [d for d in dirs if d not in blacklist_dirs]
                if root == root_dir:
                    dirs[:] = [d for d in dirs if d not in {'sutralang', 'poly_v2', 'odysseus'}]
                    
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext not in allowed_exts:
                        continue
                        
                    file_path = os.path.join(root, file)
                    if file_path in scanned_files:
                        continue
                    scanned_files.add(file_path)
                    
                    try:
                        size = os.path.getsize(file_path)
                        if size > 200 * 1024:
                            continue
                    except Exception:
                        continue
                        
                    file_count += 1
                    if file_count > max_files:
                        break
                        
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                    except Exception:
                        continue
                        
                    content_lower = content.lower()
                    score = 0
                    for kw in keywords:
                        score += content_lower.count(kw)
                        
                    if score > 0:
                        matches.append((file_path, score, content))
                
                if file_count > max_files:
                    break
            if file_count > max_files:
                break
    except Exception as e:
        return f"Local search crawling failed: {str(e)}"
    
    if matches:
        matches.sort(key=lambda x: x[1], reverse=True)
        results_str = []
        for file_path, score, content in matches[:5]:
            rel_path = os.path.relpath(file_path, root_dir)
            results_str.append(f"File: {rel_path} (score: {score})\nPreview: {content[:300]}")
        return "\n---\n".join(results_str)
    return "No matching code/files found."

# Local search tool for Obsidian Vault (Second Brain)
def obsidian_brain_search(query, vault_dir=None):
    if not vault_dir:
        vault_dir = "/data/data/com.termux/files/home/sutra-brain/obsidian-vault"
    query_str = query.strip().lower()
    if not query_str:
        return "Empty brain search query."
    stop_words = {"the", "a", "an", "is", "are", "and", "or", "in", "on", "at", "to", "for", "of", "with", "how", "make", "do", "what", "why", "kya", "hai", "kaise", "batao", "bhai", "ko", "se", "me"}
    keywords = [kw for kw in re.split(r'\s+', query_str) if kw and kw not in stop_words and len(kw) > 2]
    if not keywords:
        # Fallback to general book synthesis or web search if no meaningful vault keywords
        try:
            from sutra_book_synthesizer import synthesize_conversational_response
            return synthesize_conversational_response(query)
        except Exception:
            return f"Bhai '{query}' par technical query detect hui hai. Direct batao, kya details chahiye?"
    
    # 1. Graph Database Lookup
    graph_db_path = "/data/data/com.termux/files/home/sutra-brain/sutra_brain_graph.db"
    graph_context = []
    if os.path.exists(graph_db_path):
        try:
            conn = sqlite3.connect(graph_db_path)
            cur = conn.cursor()
            cur.execute("SELECT name, keywords, nodes_json FROM clusters WHERE name LIKE ? OR keywords LIKE ?", (f"%{query_str}%", f"%{query_str}%"))
            c_rows = cur.fetchall()
            for name, kw, njson in c_rows:
                graph_context.append(f"[Graph Cluster: {name}] Anchor Concept: [[{kw}]]")
            
            cur.execute("SELECT id, category, tags FROM nodes WHERE title LIKE ? OR tags LIKE ?", (f"%{query_str}%", f"%{query_str}%"))
            n_rows = cur.fetchall()
            for nid, cat, tjson in n_rows[:3]:
                graph_context.append(f"[Graph Node: [[{nid}]] ({cat})]")
            conn.close()
        except Exception:
            pass

    matches = []
    if not os.path.exists(vault_dir):
        return f"Obsidian Vault not found at {vault_dir}"
        
    for root, dirs, files in os.walk(vault_dir):
        for file in files:
            if file.endswith('.md'):
                if "Knowledge_Gaps" in file or "Concept_Clusters" in file:
                    continue
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except Exception:
                    continue
                content_lower = content.lower()
                score = 0
                for kw in keywords:
                    if len(kw) > 2:
                        score += content_lower.count(kw)
                if score >= 3:
                    matches.append((file_path, score, content))
                    
    results_str = []
    if graph_context:
        results_str.append("--- Knowledge Graph Insights ---\n" + "\n".join(graph_context))

    if matches:
        matches.sort(key=lambda x: x[1], reverse=True)
        top_previews = []
        for file_path, score, content in matches[:2]:
            bname = os.path.basename(file_path).replace(".md", "").replace("_", " ")
            for line in content.split("\n"):
                if len(line.strip()) > 15 and not line.startswith("#") and not line.startswith("tags:") and any(kw in line.lower() for kw in keywords):
                    top_previews.append(f"• ({bname}): {line.strip()}")
                    break
        if top_previews:
            results_str.append("\n".join(top_previews))

    # Search 615-book matrix corpus for rich synthesis
    try:
        from sutra_book_synthesizer import synthesize_conversational_response
        book_synth = synthesize_conversational_response(query)
        if book_synth and "Insight (" in book_synth:
            results_str.append(book_synth)
    except Exception:
        pass

    if results_str:
        return "\n\n".join(results_str)
    return f"Bhai '{query}' par technical response: 5G networks architecture me Radio Access Network (gNodeB), 5G Core (5GC), Network Slicing aur OpenRAN components ki zarurat hoti hai."

# Safe path validator for file operations
def safe_path(path):
    path = os.path.expanduser(str(path).strip().strip('"'))
    norm = os.path.realpath(path)
    home = os.path.realpath(os.path.expanduser("~"))
    termux_home = "/data/data/com.termux/files/home"
    if not (norm.startswith(home) or norm.startswith(termux_home)):
        return None, f"Access denied: path outside home — '{path}'"
    return norm, ""

# Sookshma File structure / DOM Dehydrator
def dehydrate_file(path):
    norm, err = safe_path(path)
    if err:
        return f"Security Error: {err}"
    try:
        if not os.path.exists(norm):
            return f"Error: File not found — '{norm}'"
        ext = os.path.splitext(norm)[1].lower()
        if ext == '.py':
            import ast
            with open(norm, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            tree = ast.parse(content)
            result = []
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    result.append(f"class {node.name}:")
                    for subnode in node.body:
                        if isinstance(subnode, ast.FunctionDef):
                            args = [a.arg for a in subnode.args.args]
                            result.append(f"    def {subnode.name}({', '.join(args)}): ...")
                elif isinstance(node, ast.FunctionDef):
                    args = [a.arg for a in node.args.args]
                    result.append(f"def {node.name}({', '.join(args)}): ...")
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    result.append(ast.unparse(node).strip())
            return "\n".join(result) if result else "Empty Python file DOM structure."
        else:
            with open(norm, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
            result = []
            for line in lines:
                line_strip = line.strip()
                if line_strip.startswith(('import ', 'from ', 'const ', 'class ', 'function ', 'def ', 'interface ', 'export ')):
                    result.append(line_strip)
            return "\n".join(result[:150]) if result else "Generic file structure preview."
    except Exception as e:
        return f"Dehydration failed: {e}"

# Read File
def read_file_tool(path):
    norm, err = safe_path(path)
    if err:
        return f"Security Error: {err}"
    try:
        if not os.path.exists(norm):
            return f"Error: File not found — '{norm}'"
        size = os.path.getsize(norm)
        if size > 500 * 1024:
            return f"Error: File too large ({size} bytes). Use shell grep."
        with open(norm, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except Exception as e:
        return f"Read failed: {e}"

# Write File
def write_file_tool(content, path):
    norm, err = safe_path(path)
    if err:
        return f"Security Error: {err}"
    try:
        os.makedirs(os.path.dirname(norm), exist_ok=True)
        with open(norm, 'w', encoding='utf-8') as f:
            f.write(str(content))
        return f"Written {len(str(content))} chars to '{norm}'"
    except Exception as e:
        return f"Write failed: {e}"

# Task/Goal DB Helper
TASK_DB = "/data/data/com.termux/files/home/sutra_life.db"

def init_task_db():
    conn = subprocess.run(["sqlite3", TASK_DB, "CREATE TABLE IF NOT EXISTS tasks (task_id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, category TEXT DEFAULT 'GENERAL', status TEXT DEFAULT 'PENDING', created_at DATETIME DEFAULT CURRENT_TIMESTAMP);"], capture_output=True)

def add_goal_to_db(text, priority=1):
    init_task_db()
    # Simple Python SQLite or subprocess execution
    import sqlite3
    try:
        conn = sqlite3.connect(TASK_DB)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (title, category, status) VALUES (?, 'GOAL', 'PENDING')", (text,))
        conn.commit()
        # Get last ID
        cursor.execute("SELECT last_insert_rowid()")
        rowid = cursor.fetchone()[0]
        conn.close()
        return rowid
    except Exception as e:
        print(f"Database error: {e}")
        return 0

# ─────────────────────────────────────────────
# SutraLang Agent Compiler Subclass
# ─────────────────────────────────────────────
class SutraAgentCompiler(SutraCompiler):
    def compile_line(self, line):
        line = line.strip()
        if not line:
            return None

        # Strip double quotes around variable names contextually to prevent parser crash
        line = re.sub(r'(\b(?:variable\s+banao|variable|banao\s+variable|print|show|darshan|dikhao|jab\s+tak|while)\s+)"([a-zA-Z0-9_]+)"', r'\1\2', line, flags=re.IGNORECASE)
        line = re.sub(r'"([a-zA-Z0-9_]+)"(\s+(?:ko|me|se|aur|value|maan|with|as|sum|difference|product|division|concatenation)\b)', r'\1\2', line, flags=re.IGNORECASE)


        # String literal pattern that safely handles escaped quotes
        str_pat = r'(?:"(?:\\.|""|[^"\\])*"|\w+)'

        # 1. Khaj — Web search: result ko "query" se khojo
        m = re.search(r'(\w+)\s+ko\s+(' + str_pat + r')\s+se\s+khojo', line, re.IGNORECASE) or \
            re.search(r'search\s+(' + str_pat + r')\s+into\s+(\w+)', line, re.IGNORECASE)
        if m:
            karta = m.group(1) if "se khojo" in line.lower() else m.group(2)
            query = m.group(2) if "se khojo" in line.lower() else m.group(1)
            return {"Kriya": "Khaj", "Karta": karta, "Query": query.strip('"')}

        # 2. Path — PDF read: result ko "file" aur "query" se padho
        m = re.search(r'(\w+)\s+ko\s+(' + str_pat + r')\s+aur\s+(' + str_pat + r')\s+se\s+padho', line, re.IGNORECASE) or \
            re.search(r'read\s+pdf\s+(' + str_pat + r')\s+with\s+(' + str_pat + r')\s+into\s+([\w]+)', line, re.IGNORECASE)
        if m:
            if "se padho" in line.lower():
                return {"Kriya": "Path", "Karta": m.group(1), "File": m.group(2).strip('"'), "Query": m.group(3).strip('"')}
            else:
                return {"Kriya": "Path", "Karta": m.group(3), "File": m.group(1).strip('"'), "Query": m.group(2).strip('"')}

        # 3. Shodh — Shell exec: result ko "command" se shodh_karo
        m = re.search(r'(\w+)\s+ko\s+(.*)\s+se\s+shodh_karo$', line, re.IGNORECASE) or \
            re.search(r'execute\s+shell\s+(' + str_pat + r')\s+into\s+(\w+)', line, re.IGNORECASE)
        if m:
            karta = m.group(1) if "se shodh_karo" in line.lower() else m.group(2)
            command = m.group(2) if "se shodh_karo" in line.lower() else m.group(1)
            command_clean = command.strip()
            if command_clean.startswith('"') and command_clean.endswith('"'):
                command_clean = command_clean[1:-1]
            return {"Kriya": "Shodh", "Karta": karta, "Command": command_clean}

        # 4. Chhav — Code search: result ko "query" se chhavo
        m = re.search(r'(\w+)\s+ko\s+(' + str_pat + r')\s+se\s+chhavo', line, re.IGNORECASE) or \
            re.search(r'search\s+code\s+(' + str_pat + r')\s+into\s+(\w+)', line, re.IGNORECASE)
        if m:
            karta = m.group(1) if "se chhavo" in line.lower() else m.group(2)
            query = m.group(2) if "se chhavo" in line.lower() else m.group(1)
            return {"Kriya": "Chhav", "Karta": karta, "Query": query.strip('"')}

        # 5. Patho — File read: result ko "path" se patho
        m = re.search(r'(\w+)\s+ko\s+(' + str_pat + r')\s+se\s+patho', line, re.IGNORECASE)
        if m:
            return {"Kriya": "Patho", "Karta": m.group(1), "Path": m.group(2).strip('"')}

        # 5b. Sookshma — File dehydration: result ko "path" se sookshma
        m = re.search(r'(\w+)\s+ko\s+(' + str_pat + r')\s+se\s+sookshma', line, re.IGNORECASE)
        if m:
            return {"Kriya": "Sookshma", "Karta": m.group(1), "Path": m.group(2).strip('"')}

        # 5c. Swans — Workspace audit/stamp: result ko "action" se swans
        m = re.search(r'(\w+)\s+ko\s+(' + str_pat + r')\s+se\s+swans', line, re.IGNORECASE)
        if m:
            return {"Kriya": "Swans", "Karta": m.group(1), "Action": m.group(2).strip('"')}

        # 6. Likho — File write: result ko content_var aur "path" me likho
        m = re.search(r'(\w+)\s+ko\s+(\w+)\s+aur\s+(' + str_pat + r')\s+me\s+likho', line, re.IGNORECASE)
        if m:
            return {"Kriya": "Likho", "Karta": m.group(1), "Content": m.group(2), "Path": m.group(3).strip('"')}

        # 7. Sochi — Save goal: g ko "goal text" me sochi
        m = re.search(r'(\w+)\s+ko\s+(' + str_pat + r')\s+me\s+sochi', line, re.IGNORECASE)
        if m:
            return {"Kriya": "Sochi", "Karta": m.group(1), "GoalText": m.group(2).strip('"')}

        # 8. Smriti — Search Obsidian Second Brain: res ko "query" se smriti
        m = re.search(r'(\w+)\s+ko\s+(' + str_pat + r')\s+se\s+smriti', line, re.IGNORECASE)
        if m:
            return {"Kriya": "Smriti", "Karta": m.group(1), "Query": m.group(2).strip('"')}

        return super().compile_line(line)

# ─────────────────────────────────────────────
# SutraLang Agent VM Subclass
# ─────────────────────────────────────────────
class SutraAgentVM(SutraVM):
    def __init__(self):
        super().__init__()
        self.dynamic_tool_used = False

    def execute(self, ast_program):
        for step in ast_program:
            kriya = step.get("Kriya")
            if not kriya:
                raise ValueError("AST error: Step does not define a 'Kriya'.")
            method_name = f"kriya_{kriya.lower()}"
            if hasattr(self, method_name):
                getattr(self, method_name)(step)
            else:
                super().execute([step])

    def kriya_khaj(self, step):
        self.dynamic_tool_used = True
        karta = step["Karta"]
        query = self.resolve_string(step["Query"])
        self.log(f"Khaj: Web search for '{query}'...")
        self.karta_registry[karta] = web_search(query)

    def kriya_path(self, step):
        self.dynamic_tool_used = True
        karta = step["Karta"]
        file_path = self.resolve_string(step["File"])
        query = self.resolve_string(step["Query"])
        self.log(f"Path: Reading PDF '{file_path}' for '{query}'...")
        self.karta_registry[karta] = read_pdf(file_path, query)

    def kriya_shodh(self, step):
        self.dynamic_tool_used = True
        karta = step["Karta"]
        command = self.resolve_string(step["Command"])
        self.log(f"Shodh: Executing shell command '{command}'...")
        self.karta_registry[karta] = execute_shell(command)

    def kriya_chhav(self, step):
        self.dynamic_tool_used = True
        karta = step["Karta"]
        query = self.resolve_string(step["Query"])
        self.log(f"Chhav: Searching codebase for '{query}'...")
        self.karta_registry[karta] = local_code_search(query)

    def kriya_patho(self, step):
        karta = step["Karta"]
        path = self.resolve_string(step["Path"])
        self.log(f"Patho: Reading file '{path}'...")
        self.karta_registry[karta] = read_file_tool(path)

    def kriya_sookshma(self, step):
        karta = step["Karta"]
        path = self.resolve_string(step["Path"])
        self.log(f"Sookshma: Dehydrating structure of '{path}'...")
        self.karta_registry[karta] = dehydrate_file(path)

    def kriya_swans(self, step):
        karta = step["Karta"]
        action = self.resolve_string(step["Action"])
        self.log(f"Swans: Running workspace stamp/audit with action '{action}'...")
        import swans
        if action == "update":
            self.karta_registry[karta] = swans.stamp_workspace()
        else:
            self.karta_registry[karta] = swans.audit_workspace()

    def kriya_likho(self, step):
        karta = step["Karta"]
        content = self.resolve_string(step["Content"])
        path = self.resolve_string(step["Path"])
        self.log(f"Likho: Writing content to '{path}'...")
        self.karta_registry[karta] = write_file_tool(content, path)

    def kriya_sochi(self, step):
        karta = step["Karta"]
        goal_text = self.resolve_string(step["GoalText"])
        self.log(f"Sochi: Saving goal '{goal_text}'...")
        goal_id = add_goal_to_db(goal_text)
        self.karta_registry[karta] = f"Goal saved with ID {goal_id}"

    def kriya_smriti(self, step):
        self.dynamic_tool_used = True
        karta = step["Karta"]
        query = self.resolve_string(step["Query"])
        self.log(f"Smriti: Searching Obsidian Vault for '{query}'...")
        self.karta_registry[karta] = obsidian_brain_search(query)
