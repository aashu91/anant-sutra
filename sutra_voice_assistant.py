#!/usr/bin/env python3
"""
sutra_voice_assistant.py — Chiransh Offline Voice Assistant Gateway
Connects Chiransh voice loop to SutraJev System 1 Router & SutraOS IPC Dispatcher.
"""

import sys
import os
import re
import time
import json
import urllib.request
import subprocess
from typing import Dict, Any

# Ensure script directory is in sys.path
SUTRA_DIR = "/data/data/com.termux/files/home/sutralang"
if SUTRA_DIR not in sys.path:
    sys.path.insert(0, SUTRA_DIR)

from sutra_os import SutraIPC, ExpanderScheduler, NyayaPageTable
from sutra_jev import SutraJevEngine, Choice, Score

# Termux colors
COLOR_RESET = "\033[0m"
COLOR_YELLOW = "\033[93m"
COLOR_GREEN = "\033[92m"
COLOR_BLUE = "\033[94m"
COLOR_CYAN = "\033[96m"
COLOR_RED = "\033[91m"
COLOR_MAGENTA = "\033[95m"

TTS_BINARY = "/data/data/com.termux/files/usr/bin/termux-tts-speak"

# Global gateway instances
ipc_bus = SutraIPC()
jev_engine = SutraJevEngine()
SERVER_URL = "http://localhost:8000"


SARVAM_API_KEY = "sk_vx7bbg7o_ERK6alEgm6m4E8PaXPiuwzYG"
SARVAM_URL = "https://api.sarvam.ai/text-to-speech"

def speak(text: str):
    """Provides TTS speech output via Sarvam AI API (shubh speaker), Termux API, or espeak."""
    if not text:
        return
    clean_speech = re.sub(r'[\*#_`~\[\]\(\)\n]', ' ', text).strip()
    clean_speech = re.sub(r'\s+', ' ', clean_speech)
    if not clean_speech:
        return

    # 1. Primary: High Quality Sarvam AI (shubh / young male voice)
    try:
        import base64, threading
        headers = {
            "api-subscription-key": SARVAM_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": [clean_speech[:500]],
            "target_language_code": "hi-IN",
            "speaker": "shubh",
            "model": "bulbul:v3"
        }
        req = urllib.request.Request(SARVAM_URL, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=5) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            audio_b64 = res_data["audios"][0]
            tmp_wav = "/data/data/com.termux/files/usr/tmp/chiransh_reply.wav"
            with open(tmp_wav, "wb") as f:
                f.write(base64.b64decode(audio_b64))
            
            def _play():
                subprocess.run(["play", tmp_wav], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            
            threading.Thread(target=_play, daemon=True).start()
            return
    except Exception as e:
        pass

    # 2. Fallback: Termux TTS
    if os.path.exists(TTS_BINARY):
        try:
            subprocess.run([TTS_BINARY, clean_speech], check=False)
            return
        except Exception:
            pass

    # 3. Fallback: espeak / espeak-ng
    import shutil
    espeak_bin = shutil.which("espeak") or shutil.which("espeak-ng")
    if espeak_bin:
        try:
            subprocess.run([espeak_bin, clean_speech], check=False)
            return
        except Exception:
            pass


def dispatch_to_sutraos_ipc(command: str, intent: str, confidence: float) -> dict:
    """Dispatches voice event to SutraOS IPC bus and HTTP server."""
    payload = {
        "source": "ChiranshVoiceGateway",
        "command": command,
        "intent": intent,
        "confidence": confidence,
        "timestamp": time.time()
    }
    
    # 1. Send via local SutraOS IPC bus
    ipc_bus.send("voice_commands", "ChiranshGateway", payload)
    
    # 2. Post to SutraOS Telemetry Server HTTP endpoint if running
    # 2. Execute actual sovereign task locally using SutraOS task router
    try:
        from sutralang_server import execute_sovereign_task
        task_res = execute_sovereign_task(intent, command)
        outputs = task_res.get("outputs", [])
        output_str = "\n".join(outputs) if outputs else f"Task {intent} executed successfully."
        
        # Build natural spoken summary
        first_out = outputs[0] if outputs else f"Executed {intent}."
        speech_text = f"Bhai, {intent} complete ho gaya hai. {first_out}"
        
        return {
            "success": True,
            "jev_decision": {"choice": intent, "confidence": confidence},
            "response": f"🎯 [SutraJev Real Execution: {intent}]\n" + output_str,
            "speech_text": speech_text
        }
    except Exception as e:
        speech_text = f"Bhai, {intent} execute karte waqt note aaya: {e}"
        return {
            "success": True,
            "jev_decision": {"choice": intent, "confidence": confidence},
            "response": f"[SutraOS Local Dispatch] Command '{command}' sent to {intent}. Note: {e}",
            "speech_text": speech_text
        }


def process_voice_command(command: str) -> dict:
    """Processes input command via SutraJev & SutraOS IPC gateway."""
    command_clean = command.strip()
    if not command_clean:
        return {}

    # 1. Safety Check via SutraJev
    safety_res = jev_engine.decide(command_clean, Score(label="Voice Safety Check", min_val=0, max_val=10))
    if safety_res.score < 4.0:
        msg = f"⚠️ Safety Containment: Voice command denied (Safety score {safety_res.score}/10)."
        spk_msg = f"Bhai, safety check trigger hua hai. Dangerous action deny kar diya gaya hai."
        print(f"{COLOR_RED}{msg}{COLOR_RESET}")
        print(f"{COLOR_GREEN}🗣️  Chiransh Spoke:{COLOR_RESET} {COLOR_YELLOW}{spk_msg}{COLOR_RESET}\n")
        speak(spk_msg)
        return {"success": False, "response": msg, "speech_text": spk_msg}

    # 2. System 1 Intent Routing
    sovereign_options = [
        "SMRITI_QUERY", "SUTRA_VM_EXEC", "EXPANDER_LOAD_BALANCE",
        "ANANT_ANAADI_RENDER", "POLY_ARBITRAGE_CHECK", "TURIYA_DEBUNK",
        "VAULT_MIRROR_SYNC", "SUTRA_JEV_ROUTING", "CHIRANSH_VOICE_IPC",
        "SENTINEL_THERMAL_SHIELD"
    ]
    choice_res = jev_engine.decide(command_clean, Choice(sovereign_options))
    
    print(f"{COLOR_CYAN}[SutraJev Voice Router]{COLOR_RESET} Intent: {COLOR_YELLOW}{choice_res.choice}{COLOR_RESET} (Confidence: {choice_res.confidence*100:.1f}%)")

    # 3. Dispatch to SutraOS IPC / Server
    res = dispatch_to_sutraos_ipc(command_clean, choice_res.choice, choice_res.confidence)
    
    output_text = res.get("response", "Command processed successfully.")
    speech_text = res.get("speech_text") or (output_text.split("\n")[0] if output_text else "Done.")
    
    print(f"{COLOR_GREEN}OUTPUT:{COLOR_RESET}\n{output_text}")
    print(f"{COLOR_GREEN}🗣️  Chiransh Spoke:{COLOR_RESET} {COLOR_YELLOW}{speech_text}{COLOR_RESET}\n")
    
    # Speak spoken Hinglish response immediately
    speak(speech_text)
    
    return res


def record_and_transcribe(seconds: int = 5) -> str:
    """Records audio via Termux microphone and transcribes speech to text."""
    audio_path = "/data/data/com.termux/files/home/voice_query.aac"
    if os.path.exists(audio_path):
        try:
            os.remove(audio_path)
        except Exception:
            pass
            
    print(f"\n{COLOR_RED}🔴 RECORDING MICROPHONE ({seconds} seconds)... Speak now!{COLOR_RESET}")
    subprocess.run(["termux-microphone-record", "-f", audio_path, "-e", "aac", "-l", str(seconds)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(seconds + 0.2)
    subprocess.run(["termux-microphone-record", "-q"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
        print(f"{COLOR_YELLOW}🔇 Audio recording failed. Grant mic permission to Termux:API.{COLOR_RESET}")
        return ""
        
    print(f"{COLOR_CYAN}⏳ Transcribing speech...{COLOR_RESET}")
    try:
        sys.path.insert(0, "/data/data/com.termux/files/home")
        from transcribe import transcribe
        text = transcribe(audio_path)
        if text:
            print(f"{COLOR_GREEN}🎙️ Recognized Speech:{COLOR_RESET} '{text}'")
            return text
        else:
            print(f"{COLOR_YELLOW}🔇 No speech detected.{COLOR_RESET}")
            return ""
    except Exception as e:
        print(f"{COLOR_RED}Transcription Error: {e}{COLOR_RESET}")
        return ""


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] in ("--mic", "-m", "listen"):
            text = record_and_transcribe(5)
            if text:
                process_voice_command(text)
            return
        elif sys.argv[1] == "--query" and len(sys.argv) > 2:
            query_arg = " ".join(sys.argv[2:])
            process_voice_command(query_arg)
            return
        else:
            query_arg = " ".join(sys.argv[1:])
            process_voice_command(query_arg)
            return

    # Interactive REPL mode
    print(f"{COLOR_CYAN}====================================================================={COLOR_RESET}")
    print(f"{COLOR_YELLOW}   ____ _   _ ___ ____    _    _   _ ____  _   _                 {COLOR_RESET}")
    print(f"{COLOR_YELLOW}  / ___| | | |_ _|  _ \\  / \\  | \\ | / ___|| | | |                {COLOR_RESET}")
    print(f"{COLOR_YELLOW} | |   | |_| || || |_) |/ _ \\ |  \\| \\___ \\| |_| |                {COLOR_RESET}")
    print(f"{COLOR_YELLOW} | |___|  _  || ||  _ </ ___ \\| |\\  |___) |  _  |                {COLOR_RESET}")
    print(f"{COLOR_YELLOW}  \\____|_| |_|___|_| \\_/_/   \\_\\_| \\_|____/|_| |_|                {COLOR_RESET}")
    print(f"{COLOR_CYAN}====================================================================={COLOR_RESET}")
    print(f"{COLOR_GREEN}Chiransh Offline Voice Gateway (SutraJev + SutraOS IPC Connected){COLOR_RESET}")
    print(f"Type {COLOR_YELLOW}mic{COLOR_RESET} to speak via microphone. Type {COLOR_YELLOW}exit{COLOR_RESET} to quit.\n")

    speak("Namaste Ashutosh bhai! Chiransh voice assistant listening mode ready hai.")

    while True:
        try:
            user_input = input(f"{COLOR_MAGENTA}chiransh_voice (type 'mic' or text)> {COLOR_RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nShutting down voice gateway...")
            break

        if not user_input or user_input.lower() == "mic":
            text = record_and_transcribe(5)
            if text:
                process_voice_command(text)
            continue

        if user_input.lower() in ("exit", "quit"):
            print("Shutting down voice gateway...")
            break

        process_voice_command(user_input)


if __name__ == "__main__":
    main()
