# launch.py — Interactive Onboarding Launcher for SutraOS & SutraLang
# Copyright (c) 2026 Ashutosh Singh (salvationfinder / Anant Anaadi Group)

import os
import sys
import subprocess

COLOR_CYAN = "\033[96m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_MAGENTA = "\033[95m"
COLOR_RESET = "\033[0m"

def print_banner():
    print(f"{COLOR_CYAN}")
    print("=" * 65)
    print("      🚀 TURIYA OS / SUTRA KERNEL (SOVEREIGN AI SYSTEM) 🚀")
    print("        Paninian Logic Engine & Misinformation Debunker")
    print("=" * 65)
    print(f"{COLOR_RESET}")


def main():
    print_banner()
    print("Welcome! Aap SutraOS ko kis mode me run karna chahte hain?\n")
    print(f"  {COLOR_GREEN}[1]{COLOR_RESET} 🌐  Web Dashboard Portal (Local UI on http://localhost:8000)")
    print(f"  {COLOR_GREEN}[2]{COLOR_RESET} 🤖  Sovereign Agent REPL (Interactive Local AI Shell)")
    print(f"  {COLOR_GREEN}[3]{COLOR_RESET} ⚡  Native C++ Engine (High-Speed Bytecode REPL)")
    print(f"  {COLOR_GREEN}[4]{COLOR_RESET} 🛡️  SutraOS Kernel Diagnostic (Run 6-Primitive Verification Test)")
    print(f"  {COLOR_GREEN}[5]{COLOR_RESET} ❌  Exit\n")

    try:
        choice = input(f"{COLOR_YELLOW}Choose an option (1-5): {COLOR_RESET}").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nExiting SutraOS Launcher.")
        sys.exit(0)

    base_dir = os.path.dirname(os.path.abspath(__file__))

    if choice == "1":
        print(f"\n{COLOR_GREEN}Starting Web Server Gateway... Open http://localhost:8000 in your browser.{COLOR_RESET}\n")
        subprocess.run([sys.executable, os.path.join(base_dir, "sutralang_server.py")])
    elif choice == "2":
        print(f"\n{COLOR_GREEN}Starting Sovereign Agent Shell...{COLOR_RESET}\n")
        subprocess.run([sys.executable, os.path.join(base_dir, "sutra_agent_bot.py")])
    elif choice == "3":
        sutra_bin = os.path.join(base_dir, "sutra.exe" if os.name == 'nt' else "sutra")
        if not os.path.exists(sutra_bin):
            print(f"\n{COLOR_YELLOW}Compiling C++ binary first...{COLOR_RESET}")
            subprocess.run(["g++", "-O3", "-std=c++17", os.path.join(base_dir, "sutralang.cpp"), "-o", sutra_bin])
        print(f"\n{COLOR_GREEN}Launching C++ REPL...{COLOR_RESET}\n")
        subprocess.run([sutra_bin])
    elif choice == "4":
        print(f"\n{COLOR_GREEN}Running SutraOS Kernel Diagnostic Suite...{COLOR_RESET}\n")
        subprocess.run([sys.executable, os.path.join(base_dir, "sutra_os.py")])
    else:
        print("Goodbye!")

if __name__ == "__main__":
    main()
