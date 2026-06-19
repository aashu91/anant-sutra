document.addEventListener("DOMContentLoaded", () => {
    // ----------------------------------------------------
    // Tab Switching Logic (Left & Right Panes)
    // ----------------------------------------------------
    const leftTabBtns = document.querySelectorAll(".left-pane .tab-btn");
    const leftTabPanels = document.querySelectorAll(".left-pane .tab-panel");
    const rightTabBtns = document.querySelectorAll(".right-pane .tab-btn");
    const rightTabPanels = document.querySelectorAll(".right-pane .tab-panel");

    leftTabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const target = btn.dataset.target;
            leftTabBtns.forEach(b => b.classList.remove("active"));
            leftTabPanels.forEach(p => p.classList.remove("active"));
            btn.classList.add("active");
            document.getElementById(target).classList.add("active");

            if (target === "sutraos-sim") {
                updateOSStatus();
            }
        });
    });

    rightTabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const target = btn.dataset.target;
            rightTabBtns.forEach(b => b.classList.remove("active"));
            rightTabPanels.forEach(p => p.classList.remove("active"));
            btn.classList.add("active");
            document.getElementById(target).classList.add("active");
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
            // Will fallback to proxy status
        });

    // ----------------------------------------------------
    // SutraBot Chat Flow
    // ----------------------------------------------------
    const chatHistory = document.getElementById("chat-history-container");
    const chatPromptInput = document.getElementById("chat-prompt-input");
    const chatSendBtn = document.getElementById("chat-send-btn");
    const webSearchToggle = document.getElementById("web-search-toggle");
    const pdfFileInput = document.getElementById("pdf-file-input");

    // Visualizer Output Elements
    const translatedCodeBox = document.getElementById("translated-code-box");
    const astJsonBox = document.getElementById("ast-json-box");
    const terminalStdout = document.getElementById("terminal-stdout");

    // Helper to append message to chat window
    function appendMessage(sender, text, isUser = false) {
        const messageDiv = document.createElement("div");
        messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
        
        const senderDiv = document.createElement("div");
        senderDiv.className = "message-sender";
        senderDiv.innerText = sender;
        
        const textDiv = document.createElement("div");
        textDiv.className = "message-text";
        textDiv.innerHTML = text.replace(/\n/g, "<br>");

        messageDiv.appendChild(senderDiv);
        messageDiv.appendChild(textDiv);
        chatHistory.appendChild(messageDiv);
        
        // Scroll to bottom
        chatHistory.scrollTop = chatHistory.scrollHeight;
        return messageDiv;
    }

    async function handleSend() {
        let promptVal = chatPromptInput.value.trim();
        if (!promptVal) return;

        const useWebSearch = webSearchToggle.checked;
        const useCodeSearch = document.getElementById("codebase-search-toggle").checked;
        const pdfFile = pdfFileInput.value.trim();

        // Construct enriched agent instructions based on active UI toggles
        let apiPrompt = promptVal;
        if (pdfFile && useWebSearch) {
            apiPrompt = `Read PDF "${pdfFile}" about "${promptVal}" and search the web for Polymarket news, then show the summaries.`;
        } else if (pdfFile) {
            apiPrompt = `Read PDF "${pdfFile}" about "${promptVal}" and print the details.`;
        } else if (useWebSearch) {
            apiPrompt = `Search on the web for "${promptVal}" and print the results.`;
        } else if (useCodeSearch) {
            apiPrompt = `Search local codebase for "${promptVal}" and show it.`;
        }

        // 1. Append User Message
        appendMessage("You", promptVal, true);
        chatPromptInput.value = "";

        // 2. Append Thinking Indicator
        const thinkingBubble = appendMessage("SutraBot", "Thinking & compiling code... Please wait...");
        
        try {
            // Trigger right visualizer tab active
            const visTab = document.querySelector('[data-target="compiler-vis"]');
            if (visTab) visTab.click();

            // 3. POST request to /api/chat
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ prompt: apiPrompt })
            });

            const data = await response.json();
            
            // Remove thinking bubble
            thinkingBubble.remove();

            if (data.success) {
                // 4. Append Bot Response
                appendMessage("SutraBot", data.response);

                // 5. Update Compiler Trace panels in Right Pane
                translatedCodeBox.innerText = data.sutra_code;
                astJsonBox.innerText = JSON.stringify(data.ast, null, 2);

                // 6. Update SutraVM Console logs in Right Tab 3
                updateVMConsole(data.vm_logs);
            } else {
                appendMessage("SutraBot", `Error compiling/executing program: ${data.error}`);
                translatedCodeBox.innerText = data.sutra_code || "// Syntax error.";
                astJsonBox.innerText = "// Compilation failed.";
            }

        } catch (err) {
            thinkingBubble.remove();
            appendMessage("SutraBot", "Failed to connect to SutraServer. Please make sure sutralang_server.py is running.");
            console.error(err);
        }
    }

    chatSendBtn.addEventListener("click", handleSend);
    chatPromptInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            handleSend();
        }
    });

    // Helper to render VM logs into the stdout console panel
    function updateVMConsole(logs) {
        terminalStdout.innerHTML = "";
        logs.forEach(line => {
            const div = document.createElement("div");
            div.className = "terminal-line";
            if (line.includes("[Compiler Error]") || line.includes("Error")) {
                div.className = "terminal-line terminal-err";
            }
            div.innerText = line;
            terminalStdout.appendChild(div);
        });
    }

    // ----------------------------------------------------
    // Direct Coding Shell Flow
    // ----------------------------------------------------
    const rawSutraInput = document.getElementById("raw-sutra-input");
    const rawRunBtn = document.getElementById("raw-run-btn");

    rawRunBtn.addEventListener("click", async () => {
        const rawCode = rawSutraInput.value.trim();
        if (!rawCode) return;

        rawRunBtn.disabled = true;
        rawRunBtn.innerText = "Executing...";

        try {
            const response = await fetch("/api/run", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ prompt: rawCode, mode: "raw" })
            });

            const data = await response.json();
            
            rawRunBtn.disabled = false;
            rawRunBtn.innerText = "Execute Program";

            // Switch right pane active tab to VM Console to inspect output
            const consoleTab = document.querySelector('[data-target="vm-console-panel"]');
            if (consoleTab) consoleTab.click();

            if (data.success) {
                translatedCodeBox.innerText = rawCode;
                astJsonBox.innerText = JSON.stringify(data.ast, null, 2);
                
                // VM logs
                const lines = data.stdout.split("\n");
                updateVMConsole(lines);
            } else {
                translatedCodeBox.innerText = rawCode;
                astJsonBox.innerText = "// Compilation failed.";
                updateVMConsole([`Error: ${data.error}`]);
            }

        } catch (err) {
            rawRunBtn.disabled = false;
            rawRunBtn.innerText = "Execute Program";
            updateVMConsole(["Network Error: Could not connect to Sutra Server."]);
            console.error(err);
        }
    });


    // ----------------------------------------------------
    // SutraOS Simulator Logic
    // ----------------------------------------------------
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
            
            // Switch tab to show VM console
            const consoleTab = document.querySelector('[data-target="vm-console-panel"]');
            if (consoleTab) consoleTab.click();

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
