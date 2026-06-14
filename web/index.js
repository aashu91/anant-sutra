document.addEventListener("DOMContentLoaded", () => {
    // Tab switching logic
    const tabButtons = document.querySelectorAll(".tab-btn");
    const tabPanels = document.querySelectorAll(".tab-panel");

    tabButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const target = btn.dataset.target;
            
            tabButtons.forEach(b => b.classList.remove("active"));
            tabPanels.forEach(p => p.classList.remove("active"));
            
            btn.classList.add("active");
            document.getElementById(target).classList.add("active");
        });
    });

    // Mode toggling logic
    const modeButtons = document.querySelectorAll(".mode-btn");
    const playgroundInput = document.getElementById("playground-input");
    const translatedPanelWrapper = document.getElementById("translated-panel-wrapper");
    let currentMode = "vibe"; // "vibe" or "raw"

    modeButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const mode = btn.dataset.mode;
            currentMode = mode;
            
            modeButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            
            if (mode === "vibe") {
                playgroundInput.placeholder = "Enter your natural language prompt here... (e.g. Create a variable score with value 85. If score is greater than 50, print Success.)";
                playgroundInput.value = 'Create a score variable with value 85. If score is greater than 50, print "Success: Score is greater than 50".';
                translatedPanelWrapper.style.display = "flex";
            } else {
                playgroundInput.placeholder = "Enter raw Paninian SutraLang code here...\n\nExample:\ncounter + sruj(maan=0)\ncounter + drsh()";
                playgroundInput.value = 'score + sruj(maan=85)\nscore + drsh()\n\nscore + sankalpa(sharta=bada, karana=50)\n  "Success: Score is greater than 50" + drsh()\nsankalpa_khatam';
                translatedPanelWrapper.style.display = "none";
            }
        });
    });

    // Check Ollama connection status on load
    const ollamaDot = document.querySelector(".ollama-dot");
    fetch("http://localhost:11434/api/tags")
        .then(res => {
            if (res.ok) {
                ollamaDot.classList.add("connected");
            }
        })
        .catch(err => {
            console.log("Ollama server not reachable directly from browser CORS:", err);
            // We still assume it runs via backend server if direct CORS fails
        });

    // Run / Compile action
    const runBtn = document.getElementById("run-btn");
    const translatedCodeBox = document.getElementById("translated-code-box");
    const astJsonBox = document.getElementById("ast-json-box");
    const bytecodeHexBox = document.getElementById("bytecode-hex-box");
    const terminalStdout = document.getElementById("terminal-stdout");

    runBtn.addEventListener("click", async () => {
        const inputVal = playgroundInput.value.trim();
        if (!inputVal) return;

        // Reset UI boxes
        runBtn.disabled = true;
        runBtn.innerText = "Processing...";
        terminalStdout.innerHTML = `<div class="terminal-line">// Querying compiler pipeline...</div>`;
        
        try {
            const response = await fetch("/api/run", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    prompt: inputVal,
                    mode: currentMode
                })
            });

            const data = await response.json();
            
            runBtn.disabled = false;
            runBtn.innerText = "Compile & Run";
            terminalStdout.innerHTML = ""; // Clear console

            if (data.success) {
                // 1. Show Translated Code (in Vibe Mode)
                if (currentMode === "vibe") {
                    translatedCodeBox.innerText = data.translated;
                }
                
                // 2. Render AST
                astJsonBox.innerText = JSON.stringify(data.ast, null, 2);
                
                // 3. Render Bytecode Hex Grid
                renderBytecodeHex(data.bytecode);
                
                // 4. Show output logs
                const lines = data.stdout.split("\n");
                lines.forEach(line => {
                    if (line.trim()) {
                        const div = document.createElement("div");
                        div.className = "terminal-line";
                        div.innerText = line;
                        terminalStdout.appendChild(div);
                    }
                });
            } else {
                // Show compilation/translation error
                if (data.translated && currentMode === "vibe") {
                    translatedCodeBox.innerText = data.translated;
                }
                astJsonBox.innerText = "// Compilation failed.";
                bytecodeHexBox.innerHTML = `<span class="hex-placeholder">// Execution halted.</span>`;
                
                const errDiv = document.createElement("div");
                errDiv.className = "terminal-line terminal-err";
                errDiv.innerText = `Error: ${data.error}`;
                terminalStdout.appendChild(errDiv);
            }
        } catch (err) {
            runBtn.disabled = false;
            runBtn.innerText = "Compile & Run";
            terminalStdout.innerHTML = `<div class="terminal-line terminal-err">Network Error: Could not connect to Sutra Server. Check that sutralang_server.py is running.</div>`;
            console.error(err);
        }
    });

    // Helper to render hex bytes in grid
    function renderBytecodeHex(hexString) {
        bytecodeHexBox.innerHTML = "";
        if (!hexString) {
            bytecodeHexBox.innerHTML = `<span class="hex-placeholder">// Hex stream empty.</span>`;
            return;
        }
        
        for (let i = 0; i < hexString.length; i += 2) {
            const byte = hexString.substr(i, 2).toUpperCase();
            const span = document.createElement("span");
            span.className = "hex-byte";
            span.innerText = byte;
            bytecodeHexBox.appendChild(span);
        }
    }
});
