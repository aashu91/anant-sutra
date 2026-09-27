# sutra_dialogue_graph.py — Zero-LLM Quantized Dialogue & Intent Engine
# Copyright (c) 2026 Ashutosh Singh (salvationfinder / Anant Anaadi Group)
# Distributed under the MIT License.

import re
import difflib
from datetime import datetime

QUANTIZED_INTENTS = {
    "ANANT_ANAADI": {
        "patterns": [
            "what is anant anaadi", "anant anaadi kya hai", "tell me about anant anaadi",
            "about anant anaadi", "anant anaadi brand", "anant anaadi research"
        ],
        "responses": [
            "🚩 Anant Anaadi: Ashutosh Singh (salvationfinder) dwara sthapit Hindi Research Journal & Knowledge Brand.\n"
            "• Focus: Ancient Indian history, Vedic physics, Sanskrit linguistic technology, and philosophy made accessible.\n"
            "• Tone: Cool professor in kurta & sneakers — evidence-backed, profound Hinglish.\n"
            "• Aesthetic: Navy (#0A192F) + Saffron Gold (#FF9933) + Cream (#F5F0DC) with high-density vector diagrams."
        ]
    },
    "TURIYA": {
        "patterns": [
            "what is turiya", "turiya world", "what is turiya.world", "turiya kya hai", "about turiya"
        ],
        "responses": [
            "⚖️ turiya.world: Evidence-First Misinformation Debunking Brand.\n"
            "• Focus: Fact-checking viral claims, historical distortion debunking, and linguistic proof.\n"
            "• Voice: Calm, devastating, objective, evidence-first without being preachy."
        ]
    },
    "POLY_BHAI": {
        "patterns": [
            "what is poly bhai", "poly bhai kya hai", "tell me about poly bhai", "about poly bhai"
        ],
        "responses": [
            "📈 Poly bhai: Discord-controlled Polymarket Algorithmic Trading & Misprice Tracking Bot.\n"
            "• Stack: CLOB API + Gamma API + APScheduler + SQLite.\n"
            "• Strategy: Signal-gated by Kronos model, tracking whale bets and 3.5%+ misprices."
        ]
    },
    "CHIRANSH": {
        "patterns": [
            "what is chiransh", "chiransh kya hai", "tell me about chiransh", "about chiransh"
        ],
        "responses": [
            "🎙️ Chiransh: Local-first Sovereign Voice Companion.\n"
            "• Tech: 100% offline Python + SQLite + Vosk + Termux TTS + SutraIPC bus.\n"
            "• Zero LLM latency, push-to-talk voice execution engine."
        ]
    },
    "SUTRALANG": {
        "patterns": [
            "sutralang kya h", "what is sutralang", "sutralang kya hai", "tell me about sutralang", "about sutralang"
        ],
        "responses": [
            "⚡ SutraLang: Paninian Symbolic Programming Language & Compiler for SutraOS.\n"
            "• Architecture: 100% Non-Neural, Zero-LLM, 0 Cloud Cost.\n"
            "• Components: Paninian AST compiler, bytecode VM, SutraJev System 1 decision engine, and Nyaya logic page table."
        ]
    },
    "CAPABILITIES": {
        "patterns": [
            "what can you do for me", "what can you do", "what you can do", "capabilities", "features", "kya kar sakte ho",
            "kya kya kar sakte ho", "help me", "options", "commands", "what you can do for me", "what you do"
        ],
        "responses": [
            "Main tumhare liye 5 core kaam zero-latency par kar sakta hoon:\n"
            "1. 🧠 Second Brain Search (/brain <query>)\n"
            "2. ⚡ TuriyaOS Kernel Status & Quine Health (/status)\n"
            "3. 🎨 Anant Anaadi Media & Panchang (/media)\n"
            "4. 📈 Poly bhai Trading Bot (/alpha)\n"
            "5. 🎙️ Chiransh Voice Assistant (/voice)\n\n"
            "Type 'sutros' in Termux to start chatting!"
        ]
    },
    "POLYMATH": {
        "patterns": [
            "polymath", "18 books", "schrodinger", "dyson", "bronowski", "nimzowitsch", "ellul", "bresson", "wisdom"
        ],
        "responses": [
            "📚 18 Books for Polymaths Core Teachings:\n"
            "• 'What is Life?' (Erwin Schrödinger): Breakthroughs occur at interdisciplinary boundaries.\n"
            "• 'My System' (Aron Nimzowitsch): Prophylaxis & structural positional dominance.\n"
            "• 'Notes on the Cinematographer' (Robert Bresson): Restraint & observation reveal hidden truths.\n"
            "• 'The Ascent of Man' (Jacob Bronowski): Imagination and questioning assumptions drive progress.\n"
            "• 'The Technological Society' (Jacques Ellul): Balancing technique with human values."
        ]
    },
    "IDENTITY": {
        "patterns": [
            "who are you", "who built you", "tum kaun ho", "who made you", "what is your name",
            "what are you", "aap kaun ho", "tera naam kya hai", "what is sutra", "about yourself"
        ],
        "responses": [
            "Main SutraAgent hoon — Ashutosh Singh (salvationfinder) ka 100% sovereign, local-first AI assistant. Main SutraLang VM, TuriyaOS Kernel, aur Obsidian Second Brain se connected hoon."
        ]
    },
    "STATUS": {
        "patterns": [
            "status", "system status", "health", "turiya status", "kernel status", "telemetry", "kernel health"
        ],
        "action": "shodh",
        "command": "python3 /data/data/com.termux/files/home/turiyaos_kernel.py status"
    },
    "SECOND_BRAIN": {
        "patterns": [
            "second brain", "obsidian", "note", "notes", "blueprint", "dharma", "abundance",
            "smriti", "search brain", "vault", "dinacharya os", "siddhanta", "nishkama"
        ],
        "action": "smriti"
    },
    "MEDIA_ACTION": {
        "patterns": [
            "render reel", "create post", "generate poster", "anant anaadi media", "panchang reel", "render poster"
        ],
        "action": "shodh",
        "command": "python3 /data/data/com.termux/files/home/turiyaos_kernel.py media"
    },
    "ACADEMIA": {
        "patterns": [
            "bca", "assignment", "dinacharya", "acad", "academia", "bca_new", "courses", "exam"
        ],
        "action": "shodh",
        "command": "python3 /data/data/com.termux/files/home/turiyaos_kernel.py acad"
    },
    "TRADING": {
        "patterns": [
            "poly bhai trades", "polymarket trades", "trading bot status", "poly alpha"
        ],
        "action": "shodh",
        "command": "python3 /data/data/com.termux/files/home/turiyaos_kernel.py alpha"
    },
    "VOICE": {
        "patterns": [
            "chiransh voice", "start voice", "listen voice", "voice chat"
        ],
        "action": "shodh",
        "command": "python3 /data/data/com.termux/files/home/turiyaos_kernel.py voice"
    },
    "CONVERSATIONAL_CHAT": {
        "patterns": [
            "kya baat kr rhe ho", "kya baat kar rahe ho", "kya bol rahe ho", "what are you talking about",
            "kuch bhi", "galat bata rahe ho", "samajh nahi aaya", "bro", "dude", "arre bhai"
        ],
        "responses": [
            "Arey bhai sorry! Vault se galat note match ho gaya tha. Direct batao, kis topic ya system par baat karni hai?",
            "Sahi bol rahe ho bhai, pehle wala output out of context chala gaya tha. Seedhe batao, main 100% accurate result deta hoon!"
        ]
    },
    "GREETING": {
        "patterns": [
            "hello", "hi", "namaste", "hey", "kaise ho", "aur bhai", "kya haal hai",
            "good morning", "good evening", "good night", "hlo", "helo", "yo", "wassup",
            "kaisa hai", "kaise ho bhai"
        ],
        "responses": [
            "Namaste Ashutosh bhai! Sab badhiya. Batao aaj kis par kaam karein — Anant Anaadi, Poly bhai, ya BCA tasks?",
            "Ekdum badhiya bhai! Local sovereign engine fully active hai.",
            "Namaste! Main active hoon. Second Brain search, code editing, ya system tasks — batao kya command run karein?"
        ]
    }
}

def resolve_quantized_intent(user_query: str):
    query_clean = user_query.strip().lower()
    query_clean = re.sub(r'[^\w\s]', '', query_clean)
    words = set(query_clean.split())

    # 1. Exact match / full phrase match
    for intent_key, data in QUANTIZED_INTENTS.items():
        patterns = data["patterns"]
        for p in patterns:
            if p == query_clean or p in query_clean:
                return _build_intent_response(intent_key, data, user_query)

    return None, None

def _build_intent_response(intent_key: str, data: dict, user_query: str):
    if "responses" in data:
        import random
        resp_text = random.choice(data["responses"]).replace("\n", "\\n")
        sutra_code = f'ek variable reply value "{resp_text}"\nprint reply'
        return intent_key, sutra_code

    action = data.get("action")
    if action == "smriti":
        q_val = user_query.strip().strip('"\'')
        sutra_code = f'ek variable query value "{q_val}"\nek variable brain_res value ""\nbrain_res ko query se smriti\nprint brain_res'
        return intent_key, sutra_code

    if action == "shodh":
        cmd = data.get("command", "")
        sutra_code = f'ek variable cmd_output value ""\ncmd_output ko "{cmd}" se shodh_karo\nprint cmd_output'
        return intent_key, sutra_code

    return None, None
