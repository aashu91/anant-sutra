# SutraAgentBot: Conversational agent running local LLM and executing tools via SutraLang VM
# Copyright (c) 2026 Ashutosh Singh (salvationfinder / Anant Anaadi Group)
# Distributed under the MIT License. See LICENSE for details.
import os
import sys
import json

# Import unified compiler, VM, and tools from core
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sutra_agent_core import (
    SutraAgentCompiler, SutraAgentVM, query_ollama,
    COLOR_RESET, COLOR_YELLOW, COLOR_GREEN, COLOR_BLUE, COLOR_CYAN, COLOR_RED, COLOR_MAGENTA
)

# Memory management utilities for state persistence
MEMORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sutra_memory.json")

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_memory(registry):
    try:
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2)
    except Exception as e:
        print(f"{COLOR_RED}Failed to save memory: {e}{COLOR_RESET}")

def synthesize_response(user_query, registry):
    filtered_registry = {}
    for k, v in registry.items():
        val_str = str(v)
        if len(val_str) > 1000:
            val_str = val_str[:1000] + "... [Truncated]"
        filtered_registry[k] = val_str
    
    state_context = json.dumps(filtered_registry, indent=2)
    synthesis_system_prompt = """You are the SutraAgent response synthesiser.
The user asked a query, and we executed a dynamic tool to fetch the actual details.
We obtained the following registry values from the SutraLang VM execution:
---
STATE VALUES:
{state}
---
Task:
1. Synthesize a clean, natural, and highly accurate answer in Hinglish/English matching the user's query.
2. Rely ONLY on the provided state values. Do not use generic training cutoff facts.
3. Do not mention "registry", "SutraLang", "state", or "VM" in the final output unless specifically asked. Present the facts directly.
""".replace("{state}", state_context)
    
    print(f"{COLOR_BLUE}[SutraBot] Synthesizing final answer from tool execution outputs...{COLOR_RESET}")
    result = query_ollama(user_query, system_prompt=synthesis_system_prompt)
    return result

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
        
        print(f"[Compiled SutraLang Program]")
        print("-" * 50)
        print(sutra_code)
        print("-" * 50)
        
        try:
            ast = compiler.compile_program(sutra_code)
            vm.karta_registry = load_memory()
            vm.dynamic_tool_used = False
            vm.execute(ast)
            save_memory(vm.karta_registry)
            
            if vm.dynamic_tool_used:
                answer = synthesize_response(user_query, vm.karta_registry)
                if answer:
                    print(f"\n➔ [SUTRAAGENT ANSWER] {answer}\n")
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
    print(f"Type {COLOR_YELLOW}exit{COLOR_RESET} to quit. Type {COLOR_YELLOW}/clear{COLOR_RESET} to reset memory. Ask anything!\n")

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
            
        if user_query.lower() == "/clear":
            if os.path.exists(MEMORY_FILE):
                os.remove(MEMORY_FILE)
            print(f"{COLOR_YELLOW}Memory registry has been cleared.{COLOR_RESET}\n")
            continue

        if user_query.lower().startswith("/dream"):
            dream_query = user_query[6:].strip()
            if not dream_query:
                try:
                    # Access task DB using unified sqlite format
                    import sqlite3
                    conn = sqlite3.connect("/data/data/com.termux/files/home/sutra_life.db")
                    cursor = conn.cursor()
                    cursor.execute("SELECT title FROM tasks WHERE status = 'PENDING' LIMIT 1")
                    row = cursor.fetchone()
                    conn.close()
                    if row:
                        dream_query = row[0]
                        print(f"{COLOR_YELLOW}[Dreaming] Loading pending task/goal: '{dream_query}'...{COLOR_RESET}")
                except Exception:
                    pass
                if not dream_query:
                    dream_query = "Simulate Ramanujan expander graph partition dynamics and loop until optimal balance"
                    print(f"{COLOR_YELLOW}[Dreaming] No pending goals. Dreaming of: '{dream_query}'...{COLOR_RESET}")
            
            print(f"\n{COLOR_BLUE}[SutraBot] Entering deep reflection (dreaming)...{COLOR_RESET}")
            print(f"{COLOR_CYAN}  -> Phase 1: Compiling simulation logic with loops...{COLOR_RESET}")
            
            dream_prompt = f"Create a simulation program with loops to analyze or run the goal: {dream_query}"
            sutra_code = query_ollama(dream_prompt)
            if not sutra_code:
                print(f"{COLOR_RED}Dreaming interrupted: Ollama timed out.{COLOR_RESET}\n")
                continue
                
            print(f"\n{COLOR_CYAN}[Dream AST Program]{COLOR_RESET}")
            print("-" * 50)
            print(sutra_code)
            print("-" * 50)
            
            print(f"\n{COLOR_CYAN}  -> Phase 2: Running state VM loops...{COLOR_RESET}")
            try:
                ast = compiler.compile_program(sutra_code)
                vm.karta_registry = load_memory()
                vm.dynamic_tool_used = False
                vm.execute(ast)
                save_memory(vm.karta_registry)
                
                print(f"{COLOR_CYAN}  -> Phase 3: Synthesizing lessons learned...{COLOR_RESET}")
                synthesis_prompt = f"Write a short, profound dream reflection about solving: {dream_query}. State values: {json.dumps(vm.karta_registry)}"
                dream_synthesis = query_ollama(
                    synthesis_prompt,
                    system_prompt="You are the SutraAgent Dream Analyst. Summarize the simulation run, what variables were updated, and how this helps. Keep it short and profound in Hinglish."
                )
                print(f"\n➔ {COLOR_GREEN}[SUTRAAGENT DREAM REFLECTION]{COLOR_RESET}\n{dream_synthesis}\n")
            except Exception as e:
                print(f"{COLOR_RED}Dream collapsed in VM: {e}{COLOR_RESET}\n")
            continue

        print(f"\n{COLOR_BLUE}[SutraBot] Querying local LLM for SutraLang compilation...{COLOR_RESET}")
        sutra_code = query_ollama(user_query)
        if not sutra_code:
            print(f"{COLOR_RED}Could not compile query to SutraLang. Check if Ollama server is running.{COLOR_RESET}\n")
            continue

        print(f"\n{COLOR_CYAN}[Generated Unambiguous SutraLang Program]{COLOR_RESET}")
        print("-" * 50)
        print(sutra_code)
        print("-" * 50)

        try:
            print(f"\n{COLOR_BLUE}[SutraBot] Compiling program to Vyakarana AST...{COLOR_RESET}")
            ast = compiler.compile_program(sutra_code)
            
            print(f"{COLOR_BLUE}[SutraBot] Executing in SutraLang VM...{COLOR_RESET}")
            vm.karta_registry = load_memory()
            vm.dynamic_tool_used = False
            vm.execute(ast)
            save_memory(vm.karta_registry)
            
            if vm.dynamic_tool_used:
                answer = synthesize_response(user_query, vm.karta_registry)
                if answer:
                    print(f"\n➔ {COLOR_GREEN}[SUTRAAGENT ANSWER]{COLOR_RESET} {answer}\n")
            print()
        except Exception as e:
            print(f"{COLOR_RED}Compilation/Execution Failed: {e}{COLOR_RESET}\n")

if __name__ == "__main__":
    main()
