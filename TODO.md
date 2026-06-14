# SutraLang Project Roadmap

This is the sovereign task list for the Sanskrit-backed Vibe Coding language ecosystem.

## Core Objective
Build a lightweight, offline-first programming language where conversational Hinglish/English prompts compile to a deterministic Sanskrit AST (Vyakarana AST) and run on a custom VM, avoiding probabilistic ambiguity and Big Tech LLM dependencies.

## Tasks & Phases

### Phase 1: Local AST & VM Prototype (Completed)
- [x] Create `sutralang_vm.py` stack machine interpreter supporting `Srujana`, `Vardhanam`, `Hrasanam`, `Darshanam`, and `Pravahanam`.
- [x] Create regex-based compiler `sutralang_compiler.py` translating basic Hinglish structures to Sanskrit AST.
- [x] Run end-to-end loop test demonstrating code execution.

### Phase 2: Parser Expansion & Sanskrit Validation
- [x] Add more Kriyas: `Yogaphalam` (Arithmetic expressions) and `Sandhanam` (String concatenation).
- [ ] Add `Tulanā` (Comparison) and Panini-style prefix/suffix checking (Dhatu + Pratyaya mapping) to validate variable types and memory allocation.
- [x] Support complex conditions (`Adhikarana` branching like If-Else / Sankalpa).

### Phase 3: Neuro-Symbolic Integration (LLM to AST Compiler)
- [ ] Write a script that uses a small local model (e.g., Gemma 2B via Ollama / Llama.cpp) to convert complex, free-form conversational prompt strings into the exact JSON-based Vyakarana AST.
- [ ] Implement validator rules to block/retry compiler generation if the LLM breaks Paninian syntax constraints.

### Phase 4: Sovereign Sanskrit Bytecode (VM compiler)
- [ ] Compile Sanskrit AST to a binary bytecode representation (Sutra Bytecode - `.sutra`).
- [ ] Rewrite the interpreter VM in highly optimized C/C++ so it can run instantly on mobile/embedded systems (Termux / NDK integration).

### Phase 5: Sovereign Operating System (SutraOS)
- [ ] Design the Paninian Microkernel (SutraKernel) simulation running process scheduling via Ramanujan Expander Graphs.
- [ ] Implement Nyaya Logic Page Table (memory manager) to prevent memory leaks/overflows via formal logic validation.
- [ ] Connect Chiransh local voice companion to SutraVM-OS to act as the primary keyboard/voice interface, running offline on local devices.
