# SutraAgentBot: Clean Sovereign Conversational Agent & VM Execution
# Copyright (c) 2026 Ashutosh Singh (salvationfinder / Anant Anaadi Group)
import os
import sys
import json
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sutra_agent_core import (
    SutraAgentCompiler, SutraAgentVM, query_ollama, _looks_like_sutralang,
    COLOR_RESET, COLOR_YELLOW, COLOR_GREEN, COLOR_BLUE, COLOR_CYAN, COLOR_RED, COLOR_MAGENTA
)

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
        pass

def synthesize_response(user_query, registry):
    filtered_registry = {k: str(v)[:1000] for k, v in registry.items() if k not in ("history", "memory_history")}
    if not filtered_registry:
        return None
    
    state_context = json.dumps(filtered_registry, indent=2)
    synthesis_system_prompt = f"""You are SutraAgent.
The user asked: '{user_query}'
State values from VM execution:
{state_context}

Synthesize a concise, clean response in Hinglish/English. Strictly 1-3 sentences. No code debug dumps."""
    
    result = query_ollama(user_query, system_prompt=synthesis_system_prompt)
    if result and not _looks_like_sutralang(result):
        return result
    return None

def run_query(user_query: str, compiler: SutraAgentCompiler, vm: SutraAgentVM, verbose: bool = False):
    sutra_code = query_ollama(user_query)
    if not sutra_code:
        print(f"{COLOR_RED}Could not compile query to SutraLang via Non-Neural Engine.{COLOR_RESET}")
        return

    if verbose:
        print(f"\n{COLOR_CYAN}[Compiled SutraLang Program]{COLOR_RESET}")
        print("-" * 50)
        print(sutra_code)
        print("-" * 50)

    try:
        ast = compiler.compile_program(sutra_code)
        vm.karta_registry = load_memory()
        vm.dynamic_tool_used = False
        
        # Mute VM debug logs if not verbose
        original_log = vm.log
        if not verbose:
            vm.log = lambda msg: None

        vm.execute(ast)
        vm.log = original_log
        save_memory(vm.karta_registry)
        
        if vm.dynamic_tool_used:
            answer = synthesize_response(user_query, vm.karta_registry)
            if answer:
                print(f"{COLOR_GREEN}🤖 SutraAgent:{COLOR_RESET} {answer}\n")
                try:
                    from sutra_voice_assistant import speak
                    speak(answer)
                except Exception:
                    pass
    except Exception as e:
        print(f"{COLOR_RED}Execution Failed: {e}{COLOR_RESET}\n")

def record_and_transcribe_mic(seconds: int = 5) -> str:
    """Records audio via Termux microphone and transcribes speech to text."""
    audio_path = "/data/data/com.termux/files/home/voice_query.aac"
    if os.path.exists(audio_path):
        try:
            os.remove(audio_path)
        except Exception:
            pass
            
    print(f"\n{COLOR_RED}🔴 RECORDING MICROPHONE ({seconds} seconds)... Speak now!{COLOR_RESET}")
    import subprocess, time
    subprocess.run(["termux-microphone-record", "-f", audio_path, "-e", "aac", "-l", str(seconds)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(seconds + 0.2)
    subprocess.run(["termux-microphone-record", "-q"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
        print(f"{COLOR_YELLOW}🔇 Audio recording failed. Grant mic permission to Termux:API.{COLOR_RESET}\n")
        return ""
        
    print(f"{COLOR_CYAN}⏳ Transcribing speech...{COLOR_RESET}")
    try:
        sys.path.insert(0, "/data/data/com.termux/files/home")
        from transcribe import transcribe
        text = transcribe(audio_path)
        if text:
            print(f"{COLOR_GREEN}🎙️ Chiransh Recognized:{COLOR_RESET} '{text}'\n")
            return text
        else:
            print(f"{COLOR_YELLOW}🔇 No speech detected.{COLOR_RESET}\n")
            return ""
    except Exception as e:
        print(f"{COLOR_RED}Transcription Error: {e}{COLOR_RESET}\n")
        return ""

def is_input_complete(text):
    dq = text.count('"') - text.count('\\"')
    sq = text.count("'") - text.count("\\'")
    p_open = text.count('(') - text.count(')')
    if dq % 2 != 0 or sq % 2 != 0 or p_open > 0:
        return False
    return True

def main():
    parser = argparse.ArgumentParser(description="SutraOS Sovereign Conversational Bot")
    parser.add_argument("query", nargs="*", help="Query to run")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show SutraLang VM compilation & AST debug logs")
    parser.add_argument("-m", "--mic", action="store_true", help="Record from mic immediately")
    args = parser.parse_args()

    compiler = SutraAgentCompiler()
    vm = SutraAgentVM()

    if args.mic:
        text = record_and_transcribe_mic(5)
        if text:
            run_query(text, compiler, vm, verbose=args.verbose)
        return

    if args.query:
        query_str = " ".join(args.query)
        run_query(query_str, compiler, vm, verbose=args.verbose)
        return

    print(f"{COLOR_CYAN}====================================================================={COLOR_RESET}")
    print(f"{COLOR_YELLOW}   SUTRAOS SOVEREIGN MACHINE (100% Offline & Pure Symbolic){COLOR_RESET}")
    print(f"{COLOR_CYAN}====================================================================={COLOR_RESET}")
    print(f"Type {COLOR_YELLOW}mic{COLOR_RESET} or {COLOR_YELLOW}/voice{COLOR_RESET} to speak. Type {COLOR_YELLOW}exit{COLOR_RESET} to quit.\n")

    while True:
        try:
            user_input = input(f"{COLOR_MAGENTA}sutraos> {COLOR_RESET}").strip()
            while not is_input_complete(user_input):
                try:
                    more = input(f"{COLOR_CYAN}... {COLOR_RESET}")
                    user_input += " " + more.strip()
                except (KeyboardInterrupt, EOFError):
                    break
        except (KeyboardInterrupt, EOFError):
            print("\nShutting down...")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit"):
            print("Goodbye Ashutosh bhai!")
            break

        if user_input.lower() in ("mic", "/mic", "/voice", "voice"):
            text = record_and_transcribe_mic(5)
            if text:
                run_query(text, compiler, vm, verbose=args.verbose)
            continue

        run_query(user_input, compiler, vm, verbose=args.verbose)

if __name__ == "__main__":
    main()
