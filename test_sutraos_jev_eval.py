#!/usr/bin/env python3
"""
test_sutraos_jev_eval.py — JEV Protocol Automated Evaluator for SutraVāk / SutraOS
Copyright (c) 2026 Ashutosh Singh (salvationfinder / Anant Anaadi Group)
"""

import sys
import os
import time

sys.path.insert(0, "/data/data/com.termux/files/home/sutralang")
from sutra_agent_core import SutraAgentCompiler, SutraAgentVM, fast_path_translate, COLOR_GREEN, COLOR_RED, COLOR_RESET

TEST_PROMPTS = [
    "hello",
    "kaise ho bhai",
    "kya jeevan ka koi uddeshya hai?",
    "samay kya hai?",
    "panini ke sutras se AI kaise chalega?",
    "tum kaun ho?"
]

def eval_sutraos():
    compiler = SutraAgentCompiler()
    vm = SutraAgentVM()
    
    print("🤖 [JEV EVALUATION LOOP START]")
    print("=" * 60)
    
    total_score = 0.0
    
    for idx, prompt in enumerate(TEST_PROMPTS, 1):
        t0 = time.perf_counter()
        sutra_code = fast_path_translate(prompt)
        t1 = time.perf_counter()
        
        # Execute VM
        ast = compiler.compile_program(sutra_code)
        vm.dynamic_tool_used = False
        vm.karta_registry = {}
        vm.execute(ast)
        
        output = vm.karta_registry.get("reply", vm.karta_registry.get("brain_res", vm.karta_registry.get("search_res", "")))
        
        # Scoring Criteria
        length_penalty = 0.0
        word_count = len(str(output).split())
        if word_count > 35:
            length_penalty = 3.0
        elif word_count > 20:
            length_penalty = 1.0
            
        human_score = 10.0 - length_penalty
        if "Namaste Ashutosh bhai! Main SutraVāk (सूत्रवाक्) hoon" in str(output) and ("hello" in prompt or "kaise ho" in prompt):
            # Penalize repetitive boilerplate intros
            human_score -= 3.0
            
        total_score += max(1.0, human_score)
        
        print(f"[{idx}] Prompt: '{prompt}'")
        print(f"    Translated Sutra: {sutra_code.strip().replace(chr(10), ' | ')}")
        print(f"    Response: '{output}'")
        print(f"    Word Count: {word_count} | Score: {max(1.0, human_score):.1f}/10 | Latency: {(t1-t0)*1000:.2f}ms")
        print("-" * 60)

    avg_score = total_score / len(TEST_PROMPTS)
    print(f"📊 Final JEV Evaluation Score: {avg_score:.2f} / 10.0")

if __name__ == "__main__":
    eval_sutraos()
