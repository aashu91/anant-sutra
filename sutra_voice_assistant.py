#!/usr/bin/env python3
import sys
import os
import re
import subprocess
import json

# Add sutralang path to sys.path to import compiler & VM
sys.path.append("/data/data/com.termux/files/home/sutralang")
from sutralang_compiler import SutraCompiler
from sutralang_vm import SutraVM

# Termux colors
COLOR_RESET = "\033[0m"
COLOR_YELLOW = "\033[93m"
COLOR_GREEN = "\033[92m"
COLOR_BLUE = "\033[94m"
COLOR_CYAN = "\033[96m"
COLOR_RED = "\033[91m"
COLOR_MAGENTA = "\033[95m"

TTS_BINARY = "/data/data/com.termux/files/usr/bin/termux-tts-speak"

def speak(text):
    if os.path.exists(TTS_BINARY):
        try:
            subprocess.run([TTS_BINARY, text], check=True)
        except Exception:
            pass

class SutraVoiceCompiler(SutraCompiler):
    def translate_to_sutra(self, query):
        query_clean = query.strip().lower()
        
        # 1. Add Task pattern: "ek task banao..." / "add task..." / "banao task..."
        match_add = re.search(r'(?:ek\s+task\s+banao|add\s+task|banao\s+task|add)\s+["\']?([^"\']+)["\']?', query_clean)
        if match_add:
            task_title = match_add.group(1).strip()
            # Dynamic category mapping
            category = "YOUTUBE" if any(w in task_title for w in ["youtube", "video", "channel", "reel", "upload", "edit"]) else "GENERAL"
            return (
                f'ek variable cmd value "python /data/data/com.termux/files/home/sutralang/sutra_life_helper.py --add \'{task_title}\' --cat \'{category}\'"\n'
                f'ek variable res value ""\n'
                f'res ko cmd se shodh_karo\n'
                f'print res'
            )
            
        # 2. Complete Task pattern: "task <id> complete karo" / "task <id> done"
        match_complete = re.search(r'(?:task\s+(\d+)\s+(?:complete|done|khatam)|complete\s+task\s+(\d+)|mark\s+(\d+)\s+as\s+done)', query_clean)
        if match_complete:
            task_id = next(g for g in match_complete.groups() if g is not None)
            return (
                f'ek variable cmd value "python /data/data/com.termux/files/home/sutralang/sutra_life_helper.py --complete {task_id}"\n'
                f'ek variable res value ""\n'
                f'res ko cmd se shodh_karo\n'
                f'print res'
            )
            
        # 3. List Tasks pattern: "tasks dikhao" / "suchi dikhao" / "show tasks"
        if any(p in query_clean for p in ["tasks dikhao", "suchi dikhao", "show tasks", "list tasks", "pending tasks"]):
            return (
                f'ek variable cmd value "python /data/data/com.termux/files/home/sutralang/sutra_life_helper.py --list"\n'
                f'ek variable res value ""\n'
                f'res ko cmd se shodh_karo\n'
                f'print res'
            )
            
        # 4. YouTube Status pattern: "youtube status" / "uploads dikhao" / "pending uploads"
        if any(p in query_clean for p in ["youtube status", "uploads dikhao", "pending uploads", "youtube queue", "video queue"]):
            return (
                f'ek variable cmd value "python /data/data/com.termux/files/home/sutralang/sutra_life_helper.py --youtube"\n'
                f'ek variable res value ""\n'
                f'res ko cmd se shodh_karo\n'
                f'print res'
            )

            
        # Fallback to standard hello/reply if nothing matches
        return (
            f'ek variable reply value "Mujhe command samajh nahi aayi, bhai. Kripya add, list, complete, ya youtube status command ka use karein."\n'
            f'print reply'
        )

# Subclass VM to implement Shodh (Shell Exec) Dhatu
class SutraVoiceVM(SutraVM):
    def execute(self, ast_program):
        for step in ast_program:
            kriya = step.get("Kriya")
            if kriya == "Shodh":
                self.kriya_shodh(step)
            else:
                super().execute([step])

    def kriya_shodh(self, step):
        karta = step.get("Karta")
        command_val = step.get("Command")
        resolved_cmd = self.resolve_string(command_val)
        
        # Verify safety (local sandbox limit)
        if '..' in resolved_cmd or 'sudo' in resolved_cmd:
            self.karta_registry[karta] = "Security Exception: Forbidden path/command"
            return
            
        try:
            res = subprocess.run(resolved_cmd, shell=True, capture_output=True, text=True, timeout=10)
            output = res.stdout.strip()
            self.karta_registry[karta] = output if output else "Done."
        except Exception as e:
            self.karta_registry[karta] = f"Execution failed: {str(e)}"

# Custom compiler linking Shodh Dhatu
class SutraVoiceCompilerLinker(SutraVoiceCompiler):
    def compile_line(self, line):
        line = line.strip()
        # Parse Shodh Dhatu: [karta] ko [command] se shodh_karo
        match_shodh = re.search(r'(\w+)\s+ko\s+((?:"[^"]*")|\w+)\s+se\s+shodh_karo', line, re.IGNORECASE)
        if match_shodh:
            karta = match_shodh.group(1)
            command = match_shodh.group(2)
            if command.startswith('"') and command.endswith('"'):
                command = command[1:-1]
            return {"Kriya": "Shodh", "Karta": karta, "Command": command}
        return super().compile_line(line)

def run_sutra_query(query):
    compiler = SutraVoiceCompilerLinker()
    vm = SutraVoiceVM()
    
    # 1. Compile conversational query to SutraLang script
    sutra_code = compiler.translate_to_sutra(query)
    
    print(f"\n{COLOR_CYAN}[SutraLang Vyakarana Script]{COLOR_RESET}")
    print("-" * 45)
    print(sutra_code)
    print("-" * 45)
    
    # 2. Compile to AST and run
    try:
        ast = compiler.compile_program(sutra_code)
        # Suppress logging during stdout execution to keep console clean
        vm.karta_registry = {}
        
        # Capture standard stdout of VM run
        vm.execute(ast)
    except Exception as e:
        print(f"{COLOR_RED}Error running VM: {e}{COLOR_RESET}")

def main():
    print(f"{COLOR_CYAN}====================================================================={COLOR_RESET}")
    print(f"{COLOR_YELLOW}   ____  _   _ _____ ____    _      _     ___ _____ _____            {COLOR_RESET}")
    print(f"{COLOR_YELLOW}  / ___|| | | |_   _|  _ \\  / \\    | |   |_ _|  ___| ____|           {COLOR_RESET}")
    print(f"{COLOR_YELLOW}  \\___ \\| | | | | | | |_) |/ _ \\   | |    | || |_  |  _|             {COLOR_RESET}")
    print(f"{COLOR_YELLOW}   ___) | |_| | | | |  _ </ ___ \\  | |___ | ||  _| | |___            {COLOR_RESET}")
    print(f"{COLOR_YELLOW}  |____/ \\___/  |_| |_| \\_/_/   \\_\\ |_____|___|_|   |_____|          {COLOR_RESET}")
    print(f"{COLOR_CYAN}====================================================================={COLOR_RESET}")
    print(f"{COLOR_GREEN}SutraLang Conversational Voice Assistant (Zero-UI, Offline TTS){COLOR_RESET}")
    print(f"Type {COLOR_YELLOW}exit{COLOR_RESET} to quit.\n")
    
    # Welcome voice greeting
    speak("Sovereign voice assistant activated. How can I help you today?")
    
    while True:
        try:
            user_input = input(f"{COLOR_MAGENTA}sutra_voice> {COLOR_RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nShutting down voice assistant...")
            break
            
        if not user_input:
            continue
            
        if user_input.lower() == "exit":
            print("Shutting down voice assistant...")
            break
            
        run_sutra_query(user_input)

if __name__ == "__main__":
    main()
