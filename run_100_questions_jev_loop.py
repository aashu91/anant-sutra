#!/usr/bin/env python3
"""
run_100_questions_jev_loop.py — 100 Unique Questions JEV Benchmark & Auto-Fix Loop for SutraOS
Copyright (c) 2026 Ashutosh Singh (salvationfinder / Anant Anaadi Group)
"""

import sys
import os
import time

sys.path.insert(0, "/data/data/com.termux/files/home/sutralang")
from sutra_agent_core import SutraAgentCompiler, SutraAgentVM, fast_path_translate

UNIQUE_100_QUESTIONS = [
    # 1-15: Greetings & Casual Conversation
    "hello", "hi", "hey", "namaste", "kaise ho bhai", "kya haal hai", "tum kaun ho",
    "kya kar rahe ho", "kya bol rahe ho", "shuru karo", "batao bhai", "kaise ho dost",
    "sab theek hai?", "kya haal chaal", "kaun ho tum",
    
    # 16-35: Philosophical, Advaita & Existential
    "kya jeevan ka koi uddeshya hai?", "samay kya hai?", "chetna kya hai?", "dharma kya hai?",
    "karma kya hota hai?", "advaita vedanta kya sikhata hai?", "shunya ka kya arth hai?",
    "mrityu kya hai?", "satya kya hai?", "anand kya hai?", "man kya hai?", "ahamkar kya hai?",
    "maya kya hai?", "moshka kya hota hai?", "ishwar kya hai?", "gyan kya hai?", "dhyan kya hai?",
    "samsara kya hai?", "bhavnaen kya hoti hain?", "aatmgyan kya hai?",
    
    # 36-55: Paninian & Sanskrit Linguistic Engine
    "panini ke sutras se AI kaise chalega?", "ashtadhyayi kya hai?", "karaka theory kya hai?",
    "karta karaka kya hota hai?", "karma karaka kya hai?", "karana karaka kya hota hai?",
    "dhatu kya hai?", "sphota theory kya hai?", "vakyapadiya kya hai?", "paribhasha sutra kya hai?",
    "vidhi sutra kya hai?", "anuvritti kya hoti hai?", "shiva sutra kya hain?", "mahabhashya kya hai?",
    "nyaya logic kya hai?", "sampradana karaka kya hai?", "apadana karaka kya hai?",
    "adhikarana karaka kya hai?", "dhatupatha kya hai?", "siddhanta kaumudi kya hai?",
    
    # 56-75: Systems Engineering & Karpathy Rules
    "karpathy rule 1 kya hai?", "karpathy rule 2 kya hai?", "karpathy rule 3 kya hai?",
    "karpathy rule 4 kya hai?", "ponytail dev philosophy kya hai?", "tdd cycle kya hai?",
    "red green refactor kya hai?", "yagni principle kya hai?", "clean code kya hota hai?",
    "dry run default kyu rakhte hain?", "prophylaxis design kya hai?", "system design kya hai?",
    "aiosqlite kyu use karte hain?", "termux bash automation kaise kaam karti hai?",
    "anti slop rule kya hai?", "single source of truth kyu zaroori hai?", "zero dependency design kya hai?",
    "posix compliance kya hai?", "memory leak kaise rokein?", "deadlock prophylaxis kya hai?",
    
    # 76-90: Coding, Shell & System Operations
    "python me list comprehension kaise likhein?", "sqlite me index kyu banate hain?",
    "git rebase aur merge me kya antar hai?", "c++ me memory management kaise hota hai?",
    "termux me python setup kaise karein?", "posix shell performance kaise badhaein?",
    "rest api vs graphql me kya antar hai?", "asyncio event loop kaise kaam karta hai?",
    "docker container vs chroot kya hai?", "bash script me error handling kaise karein?",
    "process vs thread me kya antar hai?", "hash map O(1) lookup kaise karta hai?",
    "binary search tree depth kya hoti hai?", "utf-8 encoding kya hoti hai?",
    "sha-256 hashing kaise kaam karti hai?",
    
    # 91-100: Polymathic & Multi-Domain Integration
    "schrodinger life book me kya sikhate hain?", "freeman dyson disturb universe kya hai?",
    "aron nimzowitsch my system chess AI me kaise lagayein?", "jacob bronowski ascent of man kya hai?",
    "christopher alexander synthesis of form kya hai?", "leonard bernstein music grammar kya hai?",
    "minsky society of mind kya hai?", "terrence deacon symbolic species kya hai?",
    "annemarie schimmel mystery of numbers kya hai?", "sutraos jarvis engine kaise kaam karta hai?"
]

def run_benchmark():
    print(f"🚀 [SUTRAOS 100 UNIQUE QUESTIONS JEV BENCHMARK]")
    print(f"Total Unique Test Prompts: {len(UNIQUE_100_QUESTIONS)}")
    print("=" * 70)
    
    compiler = SutraAgentCompiler()
    vm = SutraAgentVM()
    
    scores = []
    failed_prompts = []
    
    t_start = time.perf_counter()
    
    for i, prompt in enumerate(UNIQUE_100_QUESTIONS, 1):
        try:
            sutra_code = fast_path_translate(prompt)
            if not sutra_code:
                failed_prompts.append((i, prompt, "None returned from fast_path_translate"))
                continue
                
            ast = compiler.compile_program(sutra_code)
            vm.dynamic_tool_used = False
            vm.karta_registry = {}
            vm.execute(ast)
            
            output = vm.karta_registry.get("reply", vm.karta_registry.get("brain_res", vm.karta_registry.get("search_res", vm.karta_registry.get("res", vm.karta_registry.get("content", "")))))
            out_str = str(output).strip()
            
            w_count = len(out_str.split())
            
            # Penalties
            score = 10.0
            if w_count > 40:
                score -= 4.0
            elif w_count > 25:
                score -= 1.5
                
            if "Note:" in out_str and not any(k in prompt for k in ["read", "open", "file", "folder", "chhavo", "patho"]):
                score -= 5.0
                
            if "Namaste Ashutosh bhai! Main SutraVāk" in out_str and i > 5:
                score -= 3.0
                
            score = max(1.0, score)
            scores.append(score)
            
            if score < 7.0:
                failed_prompts.append((i, prompt, f"Low Score ({score:.1f}/10): {out_str[:60]}..."))
                
            if i % 10 == 0 or i == 100:
                print(f"Progress: [{i}/100] | Current Avg Score: {sum(scores)/len(scores):.2f}/10.0")
                
        except Exception as e:
            failed_prompts.append((i, prompt, str(e)))
            
    t_end = time.perf_counter()
    total_time_ms = (t_end - t_start) * 1000.0
    avg_score = sum(scores) / len(scores) if scores else 0.0
    
    print("=" * 70)
    print(f"📊 BENCHMARK COMPLETE!")
    print(f"Total Tested: {len(UNIQUE_100_QUESTIONS)}")
    print(f"Passed Prompts (Score >= 7.0): {len(scores) - len(failed_prompts)} / 100")
    print(f"Average JEV Score: {avg_score:.2f} / 10.0")
    print(f"Total Execution Time: {total_time_ms:.2f} ms (Avg: {total_time_ms/1000:.2f} ms/query)")
    
    if failed_prompts:
        print("\n⚠️ FAILED PROMPTS (Needs Fix):")
        for idx, p, reason in failed_prompts:
            print(f"  [{idx}] '{p}' -> {reason}")
    else:
        print("\n🎉 ALL 100 UNIQUE QUESTIONS PASSED WITH ZERO ERRORS!")
        
    return avg_score, failed_prompts

if __name__ == "__main__":
    run_benchmark()
