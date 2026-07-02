# SutraAgent: Conversational Sovereign Agent & Rule Manager
# Handles offline interactive execution, self-learning, and bytecode registry

import os
import sys
import json
import subprocess
import re

RULES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rules_db")
CATALOG_PATH = os.path.join(RULES_DIR, "catalog.json")

# Termux colors
COLOR_RESET = "\033[0m"
COLOR_YELLOW = "\033[93m"
COLOR_GREEN = "\033[92m"
COLOR_BLUE = "\033[94m"
COLOR_CYAN = "\033[96m"
COLOR_RED = "\033[91m"
COLOR_MAGENTA = "\033[95m"

def setup_db() -> None:
    """Creates the rules database directory and initial empty catalog if missing."""
    os.makedirs(RULES_DIR, exist_ok=True)
    if not os.path.exists(CATALOG_PATH):
        with open(CATALOG_PATH, 'w', encoding='utf-8') as f:
            json.dump({}, f)

def load_catalog() -> dict:
    """Loads and returns the rule catalog JSON mapping."""
    with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_catalog(catalog: dict) -> None:
    """Saves the rule catalog mapping to disk."""
    with open(CATALOG_PATH, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2)

def register_rule(name: str, description: str, source_code: str) -> bool:
    """Compiles a SutraLang source string into native bytecode and registers it in the catalog."""
    setup_db()
    catalog = load_catalog()
    
    bytecode_filename = f"{name}.sutrab"
    bytecode_path = os.path.join(RULES_DIR, bytecode_filename)
    
    cpp_vm = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sutra")
    if not os.path.exists(cpp_vm):
        cpp_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sutralang.cpp")
        print(f"{COLOR_BLUE}[SutraAgent] C++ VM binary missing. Compiling sutralang.cpp...{COLOR_RESET}")
        subprocess.run(["g++", "-O3", "-std=c++17", cpp_src, "-o", cpp_vm])

    # Compile source to bytecode using C++ compiler
    try:
        res = subprocess.run([cpp_vm, "--compile-line", source_code, bytecode_path], capture_output=True, text=True)
        if res.returncode != 0:
            print(f"{COLOR_RED}Syntax Error compiling rule: {res.stderr.strip()}{COLOR_RESET}")
            return False
    except Exception as e:
        print(f"{COLOR_RED}Compilation Error: {e}{COLOR_RESET}")
        return False

    # Update catalog
    catalog[name] = {
        "description": description,
        "bytecode_file": bytecode_filename,
        "source": source_code,
        "size_bytes": os.path.getsize(bytecode_path)
    }
    save_catalog(catalog)
    return True

def run_bytecode(bytecode_path: str) -> None:
    """Loads and runs a compiled bytecode file (.sutrab) on the C++ virtual machine."""
    cpp_vm = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sutra")
    if not os.path.exists(cpp_vm):
        # Compile if missing
        cpp_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sutralang.cpp")
        print(f"{COLOR_BLUE}[SutraAgent] C++ VM binary missing. Compiling sutralang.cpp...{COLOR_RESET}")
        subprocess.run(["g++", "-O3", "-std=c++17", cpp_src, "-o", cpp_vm])
        
    try:
        res = subprocess.run([cpp_vm, "--run", bytecode_path], capture_output=True, text=True, timeout=5)
        if res.stdout:
            print(res.stdout, end="")
        if res.returncode != 0:
            print(f"{COLOR_RED}VM Runtime Error: {res.stderr.strip()}{COLOR_RESET}")
    except subprocess.TimeoutExpired:
        print(f"{COLOR_RED}Execution Error: VM execution timed out (infinite loop?){COLOR_RESET}")
    except Exception as e:
        print(f"{COLOR_RED}Execution Spawn Error: {e}{COLOR_RESET}")

def main():
    setup_db()
    
    # Print beautiful ASCII banner
    print(f"{COLOR_CYAN}====================================================================={COLOR_RESET}")
    print(f"{COLOR_YELLOW}  ____  _   _ _____ ____    _       _     ____ _____ _   _ _____     {COLOR_RESET}")
    print(f"{COLOR_YELLOW} / ___|| | | |_   _|  _ \\  / \\     / \\   / ___| ____| \\ | |_   _|    {COLOR_RESET}")
    print(f"{COLOR_YELLOW} \\___ \\| | | | | | | |_) |/ _ \\   / _ \\ | |  _|  _| |  \\| | | |      {COLOR_RESET}")
    print(f"{COLOR_YELLOW}  ___) | |_| | | | |  _ </ ___ \\ / ___ \\| |_| | |___| |\\  | | |      {COLOR_RESET}")
    print(f"{COLOR_YELLOW} |____/ \\___/  |_| |_| \\_/_/   \\_\\_/   \\_\\____|_____|_| \\_| |_|      {COLOR_RESET}")
    print(f"{COLOR_CYAN}====================================================================={COLOR_RESET}")
    print(f"{COLOR_GREEN}Sovereign Paninian Symbolic AI Agent Console - 100% Offline & Pure C++{COLOR_RESET}")
    print(f"Type {COLOR_YELLOW}help{COLOR_RESET} to view commands. Type {COLOR_YELLOW}exit{COLOR_RESET} to quit.\n")

    while True:
        try:
            user_input = input(f"{COLOR_MAGENTA}sutra_agent> {COLOR_RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nShutting down SutraAgent...")
            break
            
        if not user_input:
            continue
            
        if user_input.lower() == "exit":
            print("Shutting down SutraAgent...")
            break

        # Command parsing
        if user_input.lower() == "help":
            print(f"\n{COLOR_YELLOW}SutraAgent Commands:{COLOR_RESET}")
            print(f"  {COLOR_GREEN}teach <name> \"<description>\": <body>{COLOR_RESET} - Teach a new bytecode rule")
            print(f"    Example: {COLOR_CYAN}teach greet \"Welcome user\": print \"Namaste Aashu\"{COLOR_RESET}")
            print(f"  {COLOR_GREEN}run <name>{COLOR_RESET}                            - Execute a learned bytecode rule")
            print(f"  {COLOR_GREEN}list{COLOR_RESET}                                  - List all learned rules in catalog")
            print(f"  {COLOR_GREEN}delete <name>{COLOR_RESET}                         - Delete a rule from catalog")
            print(f"  {COLOR_GREEN}<statement>{COLOR_RESET}                           - Direct execution of any SutraLang statement")
            print(f"    Example: {COLOR_CYAN}ek variable x value 10; print x{COLOR_RESET}\n")
            continue

        if user_input.lower() == "list":
            catalog = load_catalog()
            if not catalog:
                print(f"{COLOR_YELLOW}Catalog is empty. Teach me something!{COLOR_RESET}")
                continue
            print(f"\n{COLOR_YELLOW}Learned Rules Registry:{COLOR_RESET}")
            print(f"{'Rule Name':<20} | {'Description':<35} | {'Bytecode Size':<10}")
            print("-" * 75)
            for name, meta in catalog.items():
                print(f"{COLOR_GREEN}{name:<20}{COLOR_RESET} | {meta['description']:<35} | {meta['size_bytes']} bytes")
            print()
            continue

        # Pattern: teach <name> "<description>": <body>
        match_teach = re.match(r'^teach\s+(\w+)\s+"([^"]*)":\s*(.+)$', user_input, re.IGNORECASE)
        if match_teach:
            name = match_teach.group(1)
            desc = match_teach.group(2)
            body = match_teach.group(3)
            # Replace semicolon separators with newlines to support multi-line inline inputs
            body_formatted = body.replace(';', '\n')
            
            print(f"{COLOR_BLUE}[SutraAgent] Compiling rule '{name}'...{COLOR_RESET}")
            if register_rule(name, desc, body_formatted):
                print(f"{COLOR_GREEN}SutraAgent: I have successfully learned the rule '{name}'! It is compiled and saved.{COLOR_RESET}")
            continue

        # Simple teach pattern without description: teach <name>: <body>
        match_teach_simple = re.match(r'^teach\s+(\w+):\s*(.+)$', user_input, re.IGNORECASE)
        if match_teach_simple:
            name = match_teach_simple.group(1)
            body = match_teach_simple.group(2).replace(';', '\n')
            print(f"{COLOR_BLUE}[SutraAgent] Compiling rule '{name}'...{COLOR_RESET}")
            if register_rule(name, "User-defined rule", body):
                print(f"{COLOR_GREEN}SutraAgent: I have successfully learned the rule '{name}'!{COLOR_RESET}")
            continue

        # Pattern: run <name>
        match_run = re.match(r'^run\s+(\w+)$', user_input, re.IGNORECASE)
        if match_run:
            name = match_run.group(1)
            catalog = load_catalog()
            if name not in catalog:
                print(f"{COLOR_RED}Error: Rule '{name}' is unknown to me. Type 'list' to see what I know.{COLOR_RESET}")
                continue
            bytecode_path = os.path.join(RULES_DIR, catalog[name]["bytecode_file"])
            print(f"{COLOR_BLUE}[SutraAgent] Loading and executing '{name}' bytecode...{COLOR_RESET}")
            run_bytecode(bytecode_path)
            continue

        # Pattern: delete <name>
        match_del = re.match(r'^delete\s+(\w+)$', user_input, re.IGNORECASE)
        if match_del:
            name = match_del.group(1)
            catalog = load_catalog()
            if name not in catalog:
                print(f"{COLOR_RED}Error: Rule '{name}' does not exist.{COLOR_RESET}")
                continue
            bytecode_filename = catalog[name]["bytecode_file"]
            bytecode_path = os.path.join(RULES_DIR, bytecode_filename)
            if os.path.exists(bytecode_path):
                os.remove(bytecode_path)
            del catalog[name]
            save_catalog(catalog)
            print(f"{COLOR_GREEN}SutraAgent: Rule '{name}' has been deleted.{COLOR_RESET}")
            continue

        # Direct execution of statements (compile and run on fly via C++ VM)
        cpp_vm = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sutra")
        try:
            res = subprocess.run([cpp_vm, "--run-line", user_input], capture_output=True, text=True)
            if res.stdout:
                print(res.stdout, end="")
            if res.returncode != 0:
                print(f"{COLOR_RED}{res.stderr.strip()}{COLOR_RESET}")
        except Exception as e:
            print(f"{COLOR_RED}Execution Error: {e}{COLOR_RESET}")
            
if __name__ == "__main__":
    main()
