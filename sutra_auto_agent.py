#!/usr/bin/env python3
# sutra_auto_agent.py — Autonomous SutraAgent with file R/W and SQLite goal loop
import os
import sys
import time
import json

# Import unified compiler, VM, and tools from core
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sutra_agent_core import (
    SutraAgentCompiler, SutraAgentVM, query_ollama,
    COLOR_RESET, COLOR_YELLOW, COLOR_GREEN, COLOR_BLUE, COLOR_CYAN, COLOR_RED, COLOR_MAGENTA
)
from sutra_goals import add_goal, get_pending, mark_done, mark_failed, list_goals

# Execute a single natural language task
def execute_task(user_query, compiler, vm, silent=False):
    """Compile and run a NL query. Returns (success, output_text)."""
    if not silent:
        print(f"\n{COLOR_BLUE}[AutoAgent] Compiling: {user_query[:80]}...{COLOR_RESET}")

    sutra_code = query_ollama(user_query)
    if not sutra_code:
        return False, "Ollama unavailable or timeout."

    if not silent:
        print(f"{COLOR_CYAN}[SutraLang]{COLOR_RESET}\n{sutra_code}\n{'-'*40}")

    try:
        ast = compiler.compile_program(sutra_code)
        vm.karta_registry = {}
        vm.execute(ast)
        # Collect last printed value if any
        last_val = list(vm.karta_registry.values())[-1] if vm.karta_registry else ""
        return True, str(last_val)
    except Exception as e:
        return False, str(e)

# Autonomous Goal Loop
def autonomous_loop(interval=30):
    """Continuously process pending goals from SQLite sutra_life.db."""
    compiler = SutraAgentCompiler()
    vm = SutraAgentVM()

    print(f"{COLOR_CYAN}{'='*60}{COLOR_RESET}")
    print(f"{COLOR_YELLOW}  SutraAgent Autonomous Loop — ACTIVE{COLOR_RESET}")
    print(f"{COLOR_CYAN}  Checking goals every {interval}s. Ctrl+C to stop.{COLOR_RESET}")
    print(f"{COLOR_CYAN}{'='*60}{COLOR_RESET}\n")

    while True:
        pending = get_pending()
        if pending:
            print(f"{COLOR_GREEN}[Loop] {len(pending)} pending goal(s) found.{COLOR_RESET}")
            for goal in pending:
                print(f"\n{COLOR_YELLOW}[Goal {goal['id']}]{COLOR_RESET} {goal['text']}")
                success, result = execute_task(goal["text"], compiler, vm)
                if success:
                    mark_done(goal["id"], result[:500])
                    print(f"{COLOR_GREEN}✓ Done. Result: {result[:100]}{COLOR_RESET}")
                else:
                    mark_failed(goal["id"], result[:300])
                    print(f"{COLOR_RED}✗ Failed: {result[:100]}{COLOR_RESET}")
        else:
            print(f"[Loop] No pending goals. Sleeping {interval}s...", end="\r")

        try:
            time.sleep(interval)
        except KeyboardInterrupt:
            print(f"\n{COLOR_YELLOW}[Loop] Shutting down.{COLOR_RESET}")
            break

# Interactive REPL (extended)
def interactive_repl():
    compiler = SutraAgentCompiler()
    vm = SutraAgentVM()

    print(f"{COLOR_CYAN}{'='*60}{COLOR_RESET}")
    print(f"{COLOR_YELLOW}  SutraAgent — Autonomous Extended Bot{COLOR_RESET}")
    print(f"{COLOR_GREEN}  Tools: web, pdf, shell, file-r/w, goals, codebase{COLOR_RESET}")
    print(f"  Type {COLOR_YELLOW}goals{COLOR_RESET} to list goals, {COLOR_YELLOW}exit{COLOR_RESET} to quit")
    print(f"{COLOR_CYAN}{'='*60}{COLOR_RESET}\n")

    while True:
        try:
            user_query = input(f"{COLOR_MAGENTA}sutra_auto> {COLOR_RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nShutting down.")
            break

        if not user_query:
            continue
        if user_query.lower() == "exit":
            break
        if user_query.lower() == "goals":
            goals = list_goals()
            if not goals:
                print("No goals stored.")
            else:
                print(f"\n{'ID':<15} {'STATUS':<10} {'GOAL'}")
                print("-" * 70)
                for g in goals:
                    color = COLOR_GREEN if g["status"] == "completed" else (COLOR_RED if g["status"] == "failed" else COLOR_YELLOW)
                    print(f"{g['id']:<15} {color}{g['status']:<10}{COLOR_RESET} {g['text'][:50]}")
            print()
            continue

        execute_task(user_query, compiler, vm)

def main():
    args = sys.argv[1:]

    if "--loop" in args:
        interval = 30
        for a in args:
            if a.startswith("--interval="):
                interval = int(a.split("=")[1])
        autonomous_loop(interval=interval)
    elif args and not args[0].startswith("--"):
        # Single query mode
        compiler = SutraAgentCompiler()
        vm = SutraAgentVM()
        execute_task(" ".join(args), compiler, vm)
    else:
        interactive_repl()

if __name__ == "__main__":
    main()
