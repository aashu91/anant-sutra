# SutraLang & SutraAgent: Local Sovereign Developer Tool

SutraLang is a C++ compiled programming language running a Sanskrit-Hinglish syntax execution environment. SutraAgent is the semantic compiler built on top of it, translating natural language queries to SutraLang code and executing them through a local agent shell or web portal.

---

## 1. Quick Start

### Compile the Native C++ VM
```bash
g++ -O3 -std=c++17 sutralang.cpp -o sutra
```

### Run a Script
Create a script file (e.g., `test.sutra`):
```sutra
ek variable score value 100
score ko 25 se badhao
print score
```

Run it via the C++ VM:
```bash
./sutra test.sutra
```

### Enter the REPL
```bash
./sutra
```

---

## 2. SutraLang Core Syntax Reference

SutraLang code maps operations to core Sanskrit grammatical logic (*Karaka-Kriya* mappings):

| Operation | Syntax | Action | Sanskrit Root (Kriya) |
|---|---|---|---|
| **Define Variable** | `ek variable [name] value [val]` | Allocates memory space (`Karta`) with value (`Maan`) | `sruj` (Srujana) |
| **Print Variable** | `print [name]` or `[name] ko dikhao` | Output the value to stdout | `drsh` (Darshanam) |
| **Addition** | `[name] ko [val1] aur [val2] ka yog rkho` | Add values | `yog` |
| **Subtraction** | `[name] ko [val1] aur [val2] ka antar rkho` | Subtraction | `antar` |
| **Multiplication** | `[name] ko [val1] aur [val2] ka gunan rkho` | Multiplication | `gunan` |
| **Division** | `[name] ko [val1] aur [val2] ka bhagaphalam rkho` | Division (division by zero protected) | `bhagaphalam` |
| **Conditional** | `agar [condition]; [code]; sankalpa khatam` | Execute block if condition matches | `sankalpa` |
| **Loop** | `loop chalao jab tak [condition]; [code]; loop khatam` | Loop execution | `pravahanam` |

---

## 3. SutraAgent Web Chatbot Portal & Local Tools

The system includes a Python server that hosts a local chatbot portal on `http://localhost:8000`. The server queries a local Ollama model to generate SutraLang statements, which execute tools directly on your device.

### Setup and Start the Server
1. Start Ollama with the compiled model:
   ```bash
   ollama serve
   ```
2. Run the HTTP server:
   ```bash
   python sutralang_server.py
   ```
3. Open `http://localhost:8000` in your web browser.

### Agent Tool Keywords (SutraLang Extensions)

When prompting the agent in the portal, the model compiles the natural language request into specific tool commands:

- **Web Search (`khojo`)**:
  `res ko "Polymarket btc price" se khojo` (Searches DuckDuckGo and saves results to `res`)
- **Read File (`patho`)**:
  `content ko "README.md" se patho` (Reads file content directly from disk)
- **Write File (`likho`)**:
  `res ko content aur "output.txt" me likho` (Writes text to a local file path)
- **Codebase Search (`chhavo`)**:
  `code_res ko "SutraAgentVM" se chhavo` (Searches directory files recursively for match)
- **Execute Shell (`shodh_karo`)**:
  `shell_res ko "python -c 'print(5+5)'" se shodh_karo` (Runs system command inside security sandbox)
- **Save Goal (`sochi`)**:
  `g ko "Run daily checks" me sochi` (Stores goals in local SQLite database)

---

## 4. Run Automated Test Suite

Verify that compiler functions, math, loops, and self-learning registries are operating cleanly:
```bash
python test_sutra_agent.py
```
