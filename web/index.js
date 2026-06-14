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

    // SutraOS Simulator Frontend Logic
    const coreGridVisualizer = document.getElementById("core-grid-visualizer");
    const taskNameInput = document.getElementById("task-name-input");
    const addTaskBtn = document.getElementById("add-task-btn");
    const tickSchedBtn = document.getElementById("tick-sched-btn");
    
    const allocProcInput = document.getElementById("alloc-proc-input");
    const allocSizeInput = document.getElementById("alloc-size-input");
    const allocLimitInput = document.getElementById("alloc-limit-input");
    const allocMemBtn = document.getElementById("alloc-mem-btn");
    const nyayaSyllogismOutput = document.getElementById("nyaya-syllogism-output");

    async function updateOSStatus() {
        try {
            const res = await fetch("/api/os/status");
            const data = await res.json();
            
            // Render Cores Load
            coreGridVisualizer.innerHTML = "";
            for (let i = 0; i < 8; i++) {
                const tasks = data.load[i] || [];
                const card = document.createElement("div");
                card.className = "core-card" + (tasks.length > 0 ? " active" : "");
                
                const name = document.createElement("div");
                name.className = "core-name";
                name.innerText = `CORE ${i}`;
                
                const load = document.createElement("div");
                load.className = "core-load";
                load.innerText = tasks.length > 0 ? tasks.join(", ") : "Idle";
                
                card.appendChild(name);
                card.appendChild(load);
                coreGridVisualizer.appendChild(card);
            }
        } catch (err) {
            console.error("Failed to fetch OS status:", err);
        }
    }

    const osTabBtn = document.querySelector('[data-target="sutraos-sim"]');
    if (osTabBtn) {
        osTabBtn.addEventListener("click", () => {
            updateOSStatus();
        });
    }

    addTaskBtn.addEventListener("click", async () => {
        const name = taskNameInput.value.trim();
        if (!name) return;
        
        try {
            await fetch("/api/os/task/add", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name: name })
            });
            updateOSStatus();
        } catch (err) {
            console.error(err);
        }
    });

    tickSchedBtn.addEventListener("click", async () => {
        try {
            const res = await fetch("/api/os/tick", { method: "POST" });
            const data = await res.json();
            
            terminalStdout.innerHTML = "";
            const divHeader = document.createElement("div");
            divHeader.className = "terminal-line";
            divHeader.innerText = "// Ramanujan Scheduler Expander Walk Ticked:";
            terminalStdout.appendChild(divHeader);
            
            data.movements.forEach(m => {
                const div = document.createElement("div");
                div.className = "terminal-line";
                div.innerText = `  ${m}`;
                terminalStdout.appendChild(div);
            });
            
            updateOSStatus();
        } catch (err) {
            console.error(err);
        }
    });

    allocMemBtn.addEventListener("click", async () => {
        const proc = allocProcInput.value.trim();
        const size = parseInt(allocSizeInput.value) || 0;
        const limit = parseInt(allocLimitInput.value) || 0;
        if (!proc) return;
        
        try {
            const res = await fetch("/api/os/allocate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ process: proc, size: size, limit: limit })
            });
            const data = await res.json();
            
            nyayaSyllogismOutput.innerHTML = "";
            data.syllogism.forEach(step => {
                const div = document.createElement("div");
                div.className = "nyaya-line" + (data.success ? " success" : " error");
                div.innerText = step;
                nyayaSyllogismOutput.appendChild(div);
            });
        } catch (err) {
            console.error(err);
        }
    });
});

