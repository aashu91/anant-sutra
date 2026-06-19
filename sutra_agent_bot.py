# SutraAgentBot: Conversational agent running local LLM and executing tools via SutraLang VM
import os
import sys
import json
import re
import urllib.request
import urllib.parse
import subprocess
from pypdf import PdfReader

# Imports from sutralang codebase
from sutralang_compiler import SutraCompiler
from sutralang_vm import SutraVM

# Configuration
MODEL_NAME = "sutra-agent:latest"
OLLAMA_API_URL = "http://localhost:11434/api/generate"

COLOR_RESET = "\033[0m"
COLOR_YELLOW = "\033[93m"
COLOR_GREEN = "\033[92m"
COLOR_BLUE = "\033[94m"
COLOR_CYAN = "\033[96m"
COLOR_RED = "\033[91m"
COLOR_MAGENTA = "\033[95m"

SYSTEM_PROMPT = """You are the SutraLang Semantic Compiler and Agent Coordinator. Your task is to translate the user's natural language request into a formal SutraLang script.

SutraLang syntax rules (strictly follow this syntax):
1. Create variable:
   ek variable [name] value [val]
   (val can be a number like 100 or double-quoted string like "Hello")
2. Web Search:
   [name] ko [query] se khojo
   (Example: res ko "Polymarket price" se khojo -> calls web search)
3. Read PDF:
   [name] ko [file] aur [query] se padho
   (Example: doc_text ko "data.pdf" aur "score" se padho -> reads PDF)
4. Execute Shell / Code:
   [name] ko [command] se shodh_karo
   (Example: shell_res ko "python -c 'print(5+5)'" se shodh_karo -> executes shell)
5. Print / Display:
   print [name]
   [name] ko dikhao
6. String joining:
   [name] ko [val1] aur [val2] se jodo
7. Search Codebase / Local Files:
   [name] ko [query] se chhavo
   (Example: code_res ko "SutraAgentVM" se chhavo -> searches local codebase files)

Do NOT use any other syntax.

Examples:

User: Search on the web for Polymarket news and print it.
Output:
ek variable query value "Polymarket news"
ek variable search_res value ""
search_res ko query se khojo
print search_res

User: Hello! Who are you?
Output:
ek variable reply value "Namaste! Main tumhara local sovereign AI chatbot hoon."
print reply

User: Read page details from report.pdf about standard revenue and show it.
Output:
ek variable file value "report.pdf"
ek variable query value "standard revenue"
ek variable details value ""
details ko file aur query se padho
print details

User: Run a python command to calculate the factorial of 5 and show result.
Output:
ek variable cmd value "python -c 'import math; print(math.factorial(5))'"
ek variable res value ""
res ko cmd se shodh_karo
print res

User: Search local codebase for "SutraAgentVM" and show it.
Output:
ek variable query value "SutraAgentVM"
ek variable code_res value ""
code_res ko query se chhavo
print code_res

Output ONLY the formal SutraLang statements, one per line. Do not include any explanations, markdown code blocks, comments, or extra text."""

def query_ollama(prompt):
    data = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "system": SYSTEM_PROMPT,
        "stream": False,
        "options": {
            "temperature": 0.1
        }
    }
    req = urllib.request.Request(OLLAMA_API_URL)
    req.add_header('Content-Type', 'application/json')
    try:
        response = urllib.request.urlopen(req, json.dumps(data).encode('utf-8'), timeout=90)
        res_data = json.loads(response.read().decode('utf-8'))
        return res_data.get("response", "").strip()
    except Exception as e:
        print(f"{COLOR_RED}Error calling Ollama API: {e}{COLOR_RESET}")
        return None

# Web search tool using DuckDuckGo HTML parser
def web_search(query):
    try:
        url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
        
        # Parse duckduckgo results using regex
        snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
        if not snippets:
            snippets = re.findall(r'<td class="result-snippet"[^>]*>(.*?)</td>', html, re.DOTALL)
            
        results = []
        for snip in snippets[:3]:
            # Strip html tags
            clean = re.sub(r'<[^>]*>', '', snip)
            # Unescape html entities
            clean = clean.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&#x27;', "'")
            results.append(clean.strip())
            
        if results:
            return " | ".join(results)
        return "No search results found on DuckDuckGo."
    except Exception as e:
        return f"Web search failed: {str(e)}"

# PDF read tool using pypdf
def read_pdf(file_path, query=""):
    try:
        # Resolve absolute or relative path
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
            
        # Match query keywords in paragraphs
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

# Safety checking logic for shell execution
def is_command_safe(command):
    cmd_lower = command.lower()
    
    # 1. Block root-like operations and package managers
    forbidden_tokens = {'sudo', 'su', 'chown', 'chmod', 'dd', 'mkfs', 'fdisk', 'mount', 'umount', 'passwd', 'pkg', 'apt', 'npm', 'yarn', 'bun', 'pip'}
    # Tokenize to check exact word matches
    words = re.split(r'\s+', cmd_lower)
    for t in forbidden_tokens:
        if t in words or any(word.startswith(t) for word in words):
            return False, f"Forbidden command token/prefix: '{t}'"
            
    # 2. Block direct path traversals or accesses outside of home directory
    if '..' in command:
        return False, "Directory traversal (..) is strictly forbidden for security."
        
    # Find absolute paths (starting with /)
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

# Local search tool for codebase indexing (RAG)
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
        
    if not matches:
        return "No local files matched the search query."
        
    matches.sort(key=lambda x: x[1], reverse=True)
    
    results = []
    for file_path, score, content in matches[:3]:
        rel_path = os.path.relpath(file_path, root_dir)
        lines = content.split('\n')
        matching_lines = []
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(kw in line_lower for kw in keywords):
                matching_lines.append(f"L{i+1}: {line.strip()}")
                if len(matching_lines) >= 3:
                    break
        snippet = "\n  ".join(matching_lines) if matching_lines else "Keyword match in structure."
        results.append(f"File: {rel_path} (Score: {score})\n  {snippet}")
        
    return "\n---\n".join(results)

# Shell execution tool
def execute_shell(command):
    # Verify command safety
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


# Custom SutraCompiler for Agent VM
class SutraAgentCompiler(SutraCompiler):
    def compile_line(self, line):
        line = line.strip()
        if not line:
            return None
            
        # 1. Web Search pattern
        # result ko "query" se khojo
        match_khaj = re.search(r'(\w+)\s+ko\s+((?:"[^"]*")|\w+)\s+se\s+khojo', line, re.IGNORECASE) or \
                     re.search(r'search\s+((?:"[^"]*")|\w+)\s+into\s+(\w+)', line, re.IGNORECASE)
        if match_khaj:
            if "se khojo" in line.lower():
                karta = match_khaj.group(1)
                query = match_khaj.group(2)
            else:
                query = match_khaj.group(1)
                karta = match_khaj.group(2)
            
            if query.startswith('"') and query.endswith('"'):
                query = query[1:-1]
            return {"Kriya": "Khaj", "Karta": karta, "Query": query}
            
        # 2. PDF read pattern
        # result ko "file" aur "query" se padho
        match_path = re.search(r'(\w+)\s+ko\s+((?:"[^"]*")|\w+)\s+aur\s+((?:"[^"]*")|\w+)\s+se\s+padho', line, re.IGNORECASE) or \
                     re.search(r'read\s+pdf\s+((?:"[^"]*")|\w+)\s+with\s+((?:"[^"]*")|\w+)\s+into\s+(\w+)', line, re.IGNORECASE)
        if match_path:
            if "se padho" in line.lower():
                karta = match_path.group(1)
                file_path = match_path.group(2)
                query = match_path.group(3)
            else:
                file_path = match_path.group(1)
                query = match_path.group(2)
                karta = match_path.group(3)
                
            if file_path.startswith('"') and file_path.endswith('"'):
                file_path = file_path[1:-1]
            if query.startswith('"') and query.endswith('"'):
                query = query[1:-1]
            return {"Kriya": "Path", "Karta": karta, "File": file_path, "Query": query}
            
        # 3. Shell Execution pattern
        # result ko "command" se shodh_karo
        match_shodh = re.search(r'(\w+)\s+ko\s+((?:"[^"]*")|\w+)\s+se\s+shodh_karo', line, re.IGNORECASE) or \
                      re.search(r'execute\s+shell\s+((?:"[^"]*")|\w+)\s+into\s+(\w+)', line, re.IGNORECASE)
        if match_shodh:
            if "se shodh_karo" in line.lower():
                karta = match_shodh.group(1)
                command = match_shodh.group(2)
            else:
                command = match_shodh.group(1)
                karta = match_shodh.group(2)
                
            if command.startswith('"') and command.endswith('"'):
                command = command[1:-1]
            return {"Kriya": "Shodh", "Karta": karta, "Command": command}

        # 4. Codebase Search pattern: result ko "query" se chhavo
        match_chhav = re.search(r'(\w+)\s+ko\s+((?:"[^"]*")|[\w\d]+)\s+se\s+chhavo', line, re.IGNORECASE) or \
                      re.search(r'search\s+code\s+((?:"[^"]*")|[\w\d]+)\s+into\s+(\w+)', line, re.IGNORECASE)
        if match_chhav:
            if "se chhavo" in line.lower():
                karta = match_chhav.group(1)
                query = match_chhav.group(2)
            else:
                query = match_chhav.group(1)
                karta = match_chhav.group(2)
            
            if query.startswith('"') and query.endswith('"'):
                query = query[1:-1]
            return {"Kriya": "Chhav", "Karta": karta, "Query": query}

        # Fallback to standard compiler patterns
        return super().compile_line(line)


# Custom SutraVM for Agent Tools
class SutraAgentVM(SutraVM):
    # Overriding execute to handle our custom compiled Dhatus
    def execute(self, ast_program):
        self.log("Initializing Sanskrit Agent AST execution...")
        for step in ast_program:
            kriya = step.get("Kriya")
            if not kriya:
                raise ValueError("AST error: Step does not define a 'Kriya'.")
            
            method_name = f"kriya_{kriya.lower()}"
            if hasattr(self, method_name):
                method = getattr(self, method_name)
                method(step)
            else:
                # Fallback to base class
                super().execute([step])
        self.log("Agent AST execution completed.")

    # Implementation of Khaj Dhatu (Web Search)
    def kriya_khaj(self, step):
        karta = step.get("Karta")
        query_val = step.get("Query")
        # Resolve if it is variable reference
        resolved_query = self.resolve_string(query_val)
        self.log(f"Khaj Dhatu: Performing web search for '{resolved_query}'...")
        search_result = web_search(resolved_query)
        self.karta_registry[karta] = search_result
        self.log(f"Khaj: Web search completed. Stored results in '{karta}'.")

    # Implementation of Path Dhatu (Read PDF)
    def kriya_path(self, step):
        karta = step.get("Karta")
        file_val = step.get("File")
        query_val = step.get("Query")
        resolved_file = self.resolve_string(file_val)
        resolved_query = self.resolve_string(query_val)
        self.log(f"Path Dhatu: Loading PDF file '{resolved_file}' with query '{resolved_query}'...")
        pdf_result = read_pdf(resolved_file, resolved_query)
        self.karta_registry[karta] = pdf_result
        self.log(f"Path: PDF read completed. Stored results in '{karta}'.")

    # Implementation of Shodh Dhatu (Shell Exec)
    def kriya_shodh(self, step):
        karta = step.get("Karta")
        command_val = step.get("Command")
        resolved_cmd = self.resolve_string(command_val)
        self.log(f"Shodh Dhatu: Spawning shell command: {resolved_cmd}")
        shell_result = execute_shell(resolved_cmd)
        self.karta_registry[karta] = shell_result
        self.log(f"Shodh: Shell command completed. Stored results in '{karta}'.")

    # Implementation of Chhav Dhatu (Codebase Search)
    def kriya_chhav(self, step):
        karta = step.get("Karta")
        query_val = step.get("Query")
        resolved_query = self.resolve_string(query_val)
        self.log(f"Chhav Dhatu: Scanning local codebase for '{resolved_query}'...")
        search_result = local_code_search(resolved_query)
        self.karta_registry[karta] = search_result
        self.log(f"Chhav: Codebase search completed. Stored results in '{karta}'.")


def main():
    compiler = SutraAgentCompiler()
    vm = SutraAgentVM()

    # CLI Single query execution mode
    if len(sys.argv) > 1:
        user_query = " ".join(sys.argv[1:])
        sutra_code = query_ollama(user_query)
        if not sutra_code:
            print(f"Error: Could not compile query to SutraLang. Check if Ollama server is running.")
            sys.exit(1)
        
        # Output compiled code
        print(f"[Compiled SutraLang Program]")
        print("-" * 50)
        print(sutra_code)
        print("-" * 50)
        
        # Execute program
        try:
            ast = compiler.compile_program(sutra_code)
            vm.karta_registry = {}
            vm.execute(ast)
            sys.exit(0)
        except Exception as e:
            print(f"Execution failed: {e}")
            sys.exit(1)

    # REPL Interactive Console mode
    print(f"{COLOR_CYAN}====================================================================={COLOR_RESET}")
    print(f"{COLOR_YELLOW}   ____  _   _ _____ ____    _       ____   ___ _____                {COLOR_RESET}")
    print(f"{COLOR_YELLOW}  / ___|| | | |_   _|  _ \\  / \\     | __ ) / _ \\_   _|               {COLOR_RESET}")
    print(f"{COLOR_YELLOW}  \\___ \\| | | | | | | |_) |/ _ \\    |  _ \\| | | || |                 {COLOR_RESET}")
    print(f"{COLOR_YELLOW}   ___) | |_| | | | |  _ </ ___ \\   | |_) | |_| || |                 {COLOR_RESET}")
    print(f"{COLOR_YELLOW}  |____/ \\___/  |_| |_| \\_/_/   \\_\\  |____/ \\___/ |_|                 {COLOR_RESET}")
    print(f"{COLOR_CYAN}====================================================================={COLOR_RESET}")
    print(f"{COLOR_GREEN}SutraLang Sovereign Neuro-Symbolic Agent Bot (sutra-agent + Web + PDF + Shell){COLOR_RESET}")
    print(f"Type {COLOR_YELLOW}exit{COLOR_RESET} to quit. Ask anything!\n")

    while True:
        try:
            user_query = input(f"{COLOR_MAGENTA}sutra_bot> {COLOR_RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nShutting down SutraAgentBot...")
            break
            
        if not user_query:
            continue
            
        if user_query.lower() == "exit":
            print("Shutting down SutraAgentBot...")
            break

        print(f"\n{COLOR_BLUE}[SutraBot] Querying local LLM for SutraLang compilation...{COLOR_RESET}")
        sutra_code = query_ollama(user_query)
        if not sutra_code:
            print(f"{COLOR_RED}Could not compile query to SutraLang. Check if Ollama server is running.{COLOR_RESET}\n")
            continue

        print(f"\n{COLOR_CYAN}[Generated Unambiguous SutraLang Program]{COLOR_RESET}")
        print("-" * 50)
        print(sutra_code)
        print("-" * 50)

        # Parse program logic
        try:
            print(f"\n{COLOR_BLUE}[SutraBot] Compiling program to Vyakarana AST...{COLOR_RESET}")
            ast = compiler.compile_program(sutra_code)
            
            print(f"{COLOR_BLUE}[SutraBot] Executing in SutraLang VM...{COLOR_RESET}")
            # Reset variable memory registry per query run
            vm.karta_registry = {}
            vm.execute(ast)
            print()
        except Exception as e:
            print(f"{COLOR_RED}Compilation/Execution Failed: {e}{COLOR_RESET}\n")

if __name__ == "__main__":
    main()
