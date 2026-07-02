# sutra_agent_core.py — Unified compiler, VM, and tools for SutraAgent
import os
import sys
import json
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

SYSTEM_PROMPT = """You are the SutraLang Semantic Compiler. You translate natural language into SutraLang code. Output ONLY valid SutraLang statements. NEVER output explanations, greetings, markdown, or conversational text.

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
9. [name] ko [content_var] aur "[filepath]" me likho  (write file)
10. [name] ko "[goal]" me sochi  (save goal)

CRITICAL: For codebase files use chhavo/patho. For run/execute use shodh_karo. For edit/write use likho. For real-time data use khojo. NEVER output anything except valid SutraLang code.

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
    
    # 1. Simple greetings / identity
    greetings = ["hello", "hi", "namaste", "hey"]
    if any(query_clean.startswith(g) for g in greetings) or "who are you" in query_clean:
        return 'ek variable reply value "Namaste! Main tumhara local sovereign AI chatbot hoon."\nprint reply'

        
    # 2. Web Search Query
    # Matches: "Search on the web for X and print it", "Search web for X", "Search X", "Google X", "Khojo X"
    # Example: "Search on the web for Polymarket news and print it."
    m = re.search(r'^(?:search\s+(?:on\s+the\s+web\s+for|web\s+for|for)?|google|khojo)\s+(.+?)(?:\s+and\s+print\s+it\.?)?$', query, re.IGNORECASE)
    if m:
        q_val = m.group(1).strip().strip('"\'')
        return f'ek variable query value "{q_val}"\nek variable search_res value ""\nsearch_res ko query se khojo\nprint search_res'
        
    # 3. File Read Query
    # Matches: "read file X and print it", "read X", "patho X", "show file X"
    m = re.search(r'^(?:read\s+(?:the\s+)?(?:file\s+)?|patho|show\s+file\s+)(.+?)(?:\s+and\s+print\s+it\.?)?$', query, re.IGNORECASE)
    if m:
        path_val = m.group(1).strip().strip('"\'')
        return f'ek variable content value ""\ncontent ko "{path_val}" se patho\nprint content'

    # 4. Codebase Search Query
    # Matches: "Search local codebase for X and show it.", "search code for X", "chhavo X"
    m = re.search(r'^(?:search\s+(?:local\s+)?(?:codebase|code)\s+for|chhavo)\s+(.+?)(?:\s+and\s+show\s+it\.?)?$', query, re.IGNORECASE)
    if m:
        q_val = m.group(1).strip().strip('"\'')
        return f'ek variable query value "{q_val}"\nek variable code_res value ""\ncode_res ko query se chhavo\nprint code_res'

    # 5. Shell Command Query
    # Matches: "run shell command X", "run command X", "execute X", "run X", "shodh_karo X"
    m = re.search(r'^(?:run\s+(?:shell\s+)?(?:command\s+)?|execute|shodh_karo)\s+(.+)$', query, re.IGNORECASE)
    if m:
        cmd_val = m.group(1).strip().strip('"\'')
        return f'ek variable cmd value "{cmd_val}"\nek variable res value ""\nres ko cmd se shodh_karo\nprint res'

    # 6. Save Goal Query
    # Matches: "save goal X", "add goal X", "sochi X"
    m = re.search(r'^(?:save\s+goal|add\s+goal|sochi)\s+(.+)$', query, re.IGNORECASE)
    if m:
        goal_val = m.group(1).strip().strip('"\'')
        return f'ek variable g value ""\ng ko "{goal_val}" me sochi\nprint g'

    # 7. Auto-detect search intent for real-time/factual queries (like btc price, weather, news)
    # Example: "whats the btc price right now"
    search_keywords = ["price", "weather", "news", "status of", "btc", "ethereum", "bitcoin", "market", "who is", "what is"]
    if any(kw in query_clean for kw in search_keywords):
        q_val = query.strip().strip('"\'')
        return f'ek variable query value "{q_val}"\nek variable search_res value ""\nsearch_res ko query se khojo\nprint search_res'

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
    req.add_header('Content-Type', 'application/json')
    try:
        response = urllib.request.urlopen(req, json.dumps(data).encode('utf-8'), timeout=180)
        res_data = json.loads(response.read().decode('utf-8'))
        return res_data.get("response", "").strip()
    except Exception as e:
        print(f"{COLOR_RED}Error calling Ollama API: {e}{COLOR_RESET}")
        return None

def query_ollama(prompt, system_prompt=SYSTEM_PROMPT):
    # Try fast-path translation first to bypass slow Ollama inference
    fast_code = fast_path_translate(prompt)
    if fast_code:
        return fast_code

    # First attempt
    result = _call_ollama_raw(prompt, system_prompt)
    if result and _looks_like_sutralang(result):
        return result

    # Retry once with a stricter nudge if model returned conversational garbage
    if result is not None:
        print(f"{COLOR_YELLOW}[query_ollama] Model returned non-SutraLang text, retrying...{COLOR_RESET}")
        retry_prompt = f"TRANSLATE THIS TO SUTRALANG CODE ONLY. No explanations. No markdown.\n\nUser request: {prompt}"
        result = _call_ollama_raw(retry_prompt, system_prompt)
        if result and _looks_like_sutralang(result):
            return result

    # Last resort: wrap whatever the model said in a print so it displays gracefully
    # ponytail: ceiling — 2B model is unreliable, this prevents compiler crash
    if result:
        safe_text = result.replace('"', '\\"').replace('\n', ' ')[:300]
        return f'ek variable reply value "{safe_text}"\nprint reply'

    return None


# Command safety checker
def is_command_safe(command):
    cmd_lower = command.lower()
    
    # 1. Block root-like operations and package managers
    forbidden_tokens = {'sudo', 'su', 'chown', 'chmod', 'dd', 'mkfs', 'fdisk', 'mount', 'umount', 'passwd', 'pkg', 'apt', 'npm', 'yarn', 'bun', 'pip'}
    words = re.split(r'\s+', cmd_lower)
    for t in forbidden_tokens:
        if t in words or any(word.startswith(t) for word in words):
            return False, f"Forbidden command token/prefix: '{t}'"
            
    # 2. Block direct path traversals or accesses outside of home directory
    if '..' in command:
        return False, "Directory traversal (..) is strictly forbidden for security."
        
    abs_paths = re.findall(r'/[a-zA-Z0-9_\-\.\/]+', command)
    for path in abs_paths:
        norm = os.path.abspath(path)
        if not norm.startswith("/data/data/com.termux/files/home"):
            return False, f"Access to path outside home directory is forbidden: '{path}'"
            
    # 3. Block output redirections to paths outside home
    redirections = re.findall(r'>\s*([a-zA-Z0-9_\-\.\/]+)', command)
    for target in redirections:
        if target.startswith('/') and not target.startswith('/data/data/com.termux/files/home'):
            return False, f"Redirection to path outside home directory is forbidden: '{target}'"
            
    return True, ""

# Web search
def web_search(query):
    try:
        url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
        
        snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
        if not snippets:
            snippets = re.findall(r'<td class="result-snippet"[^>]*>(.*?)</td>', html, re.DOTALL)
            
        results = []
        for snip in snippets[:3]:
            clean = re.sub(r'<[^>]*>', '', snip)
            clean = clean.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&#x27;', "'")
            results.append(clean.strip())
            
        if results:
            return " | ".join(results)
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

# Safe path validator for file operations
def safe_path(path):
    path = os.path.expanduser(str(path).strip().strip('"'))
    norm = os.path.realpath(path)
    if not norm.startswith("/data/data/com.termux/files/home"):
        return None, f"Access denied: path outside home — '{path}'"
    return norm, ""

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


        # 1. Khaj — Web search: result ko "query" se khojo
        m = re.search(r'(\w+)\s+ko\s+((?:"[^"]*")|\w+)\s+se\s+khojo', line, re.IGNORECASE) or \
            re.search(r'search\s+((?:"[^"]*")|\w+)\s+into\s+(\w+)', line, re.IGNORECASE)
        if m:
            karta = m.group(1) if "se khojo" in line.lower() else m.group(2)
            query = m.group(2) if "se khojo" in line.lower() else m.group(1)
            return {"Kriya": "Khaj", "Karta": karta, "Query": query.strip('"')}

        # 2. Path — PDF read: result ko "file" aur "query" se padho
        m = re.search(r'(\w+)\s+ko\s+((?:"[^"]*")|\w+)\s+aur\s+((?:"[^"]*")|\w+)\s+se\s+padho', line, re.IGNORECASE) or \
            re.search(r'read\s+pdf\s+((?:"[^"]*")|\w+)\s+with\s+((?:"[^"]*")|\w+)\s+into\s+([\w]+)', line, re.IGNORECASE)
        if m:
            if "se padho" in line.lower():
                return {"Kriya": "Path", "Karta": m.group(1), "File": m.group(2).strip('"'), "Query": m.group(3).strip('"')}
            else:
                return {"Kriya": "Path", "Karta": m.group(3), "File": m.group(1).strip('"'), "Query": m.group(2).strip('"')}

        # 3. Shodh — Shell exec: result ko "command" se shodh_karo
        m = re.search(r'(\w+)\s+ko\s+((?:"[^"]*")|\w+)\s+se\s+shodh_karo', line, re.IGNORECASE) or \
            re.search(r'execute\s+shell\s+((?:"[^"]*")|\w+)\s+into\s+(\w+)', line, re.IGNORECASE)
        if m:
            karta = m.group(1) if "se shodh_karo" in line.lower() else m.group(2)
            command = m.group(2) if "se shodh_karo" in line.lower() else m.group(1)
            return {"Kriya": "Shodh", "Karta": karta, "Command": command.strip('"')}

        # 4. Chhav — Code search: result ko "query" se chhavo
        m = re.search(r'(\w+)\s+ko\s+((?:"[^"]*")|\w+)\s+se\s+chhavo', line, re.IGNORECASE) or \
            re.search(r'search\s+code\s+((?:"[^"]*")|\w+)\s+into\s+(\w+)', line, re.IGNORECASE)
        if m:
            karta = m.group(1) if "se chhavo" in line.lower() else m.group(2)
            query = m.group(2) if "se chhavo" in line.lower() else m.group(1)
            return {"Kriya": "Chhav", "Karta": karta, "Query": query.strip('"')}

        # 5. Patho — File read: result ko "path" se patho
        m = re.search(r'(\w+)\s+ko\s+((?:"[^"]*")|\w+)\s+se\s+patho', line, re.IGNORECASE)
        if m:
            return {"Kriya": "Patho", "Karta": m.group(1), "Path": m.group(2).strip('"')}

        # 6. Likho — File write: result ko content_var aur "path" me likho
        m = re.search(r'(\w+)\s+ko\s+(\w+)\s+aur\s+((?:"[^"]*")|\w+)\s+me\s+likho', line, re.IGNORECASE)
        if m:
            return {"Kriya": "Likho", "Karta": m.group(1), "Content": m.group(2), "Path": m.group(3).strip('"')}

        # 7. Sochi — Save goal: g ko "goal text" me sochi
        m = re.search(r'(\w+)\s+ko\s+((?:"[^"]*")|\w+)\s+me\s+sochi', line, re.IGNORECASE)
        if m:
            return {"Kriya": "Sochi", "Karta": m.group(1), "GoalText": m.group(2).strip('"')}

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
