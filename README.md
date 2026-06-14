# SutraLang: The Paninian Vibe Coding Language

SutraLang is a sovereign, zero-dependency programming language and execution environment written from scratch in C++. It translates conversational natural language (Hinglish/English) prompts directly into a mathematically precise, context-free Sanskrit AST (Vyakarana AST) and executes it on a custom native virtual machine (SutraVM).

---

## Quick Start (Zero Dependencies)

Since SutraLang is written in pure standard C++, it requires no external libraries, python dependencies, node packages, or cloud connections. You only need a standard C++ compiler (`g++` or `clang++`).

### 1. Clone the repository
```bash
git clone https://github.com/anant-anaadi/sutralang.git
cd sutralang
```

### 2. Compile from source
```bash
g++ -O3 -std=c++17 sutralang.cpp -o sutra
```
*(On Windows, run: `g++ -O3 -std=c++17 sutralang.cpp -o sutra.exe`)*

### 3. Run a vibe coding script
Create a file named `my_code.sutra` containing:
```sutra
ek variable banao score value 100
score ko 25 se badhao
print score
score ko 50 se kam karo
score ko dikhao
```

Execute it directly:
```bash
./sutra my_code.sutra
```

### 4. Open the Interactive REPL Shell
Run the binary without arguments to enter the live command line shell:
```bash
./sutra
```
Inside the shell, type conversational commands directly:
```sutra
sutra> ek variable banao temp value 5
[Vibe -> Sanskrit] ek variable banao temp value 5 ➔ temp + sruj(maan=5)
[SutraVM] Srujana: Created variable 'temp' with Maan = 5

sutra> temp ko 15 se badhao
[Vibe -> Sanskrit] temp ko 15 se badhao ➔ temp + vrdh(karana=15)
[SutraVM] Vardhanam: 'temp' increased by 15. New Maan = 20

sutra> temp ko dikhao
[Vibe -> Sanskrit] temp ko dikhao ➔ temp + drsh()
➔ [DARSHANAM] temp = 20
```

---

## The Sanskrit Logic Pipeline

Every conversational command passes through our **Vibe Translation Engine** which maps the natural syntax into Sanskrit grammatical roles (*Karaka-Kriya* relations) before execution:

*   **sruj (सृज् - Srujana):** Instantiates variable memory space (`Karta`) with a default value (`Maan`).
*   **vrdh (वृध् - Vardhanam):** Increments state variable (`Karma`) by a specific instrument value (`Karana`).
*   **hras (ह्रस् - Hrasanam):** Decrements state variable (`Karma`) by a specific instrument value (`Karana`).
*   **drsh (दृश् - Darshanam):** Resolves state and prints it to standard output.
*   **pravah (प्रवाह् - Pravahanam):** Initiates a loop boundary condition (`Seema`).
