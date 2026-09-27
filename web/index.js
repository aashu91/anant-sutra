/* index.js — SutraOS Sovereign 3D Telemetry Visualizer & Conversational OS */

(function () {
    'use strict';

    // Global State
    let scene, camera, renderer, controls;
    let coreNodes = {};
    let edgeLines = [];
    let jevNodeMesh, jevRingMesh;
    let particlePool = [];
    
    // 3D Computer Monitor & Screen Canvas
    let monitorGroup, monitorScreenMesh, screenCanvas, screenCtx, screenTexture;
    let lastQueryText = "System Standby";
    let lastResponseText = "SutraOS Conversational Gateway active.";
    let lastSpeechText = "Namaste Ashutosh bhai! SutraOS 3D Telemetry aur Obsidian Second Brain visualizer active hai.";
    let currentTaskType = "EXPANDER_IDLE";

    // 3D Obsidian Second Brain Node Graph
    let obsidianBrainGroup;
    let obsidianNodes = [];
    const OBSIDIAN_NOTE_TITLES = [
        "Smriti Brain Vault",
        "Anant Anaadi Journal",
        "Polymarket Quant Bot",
        "SutraVM Karaka",
        "Turiya Debunk Engine",
        "Chiransh Voice Gateway",
        "Ramanujan 8-Core",
        "Sentinel Shield",
        "Single Brain Mirror",
        "Postiz Publisher",
        "Nyaya Sandbox Matrix",
        "Vyakarana Compiler"
    ];

    let activeTasksCount = 0;
    let lastFrameTime = performance.now();
    let frameCount = 0;

    const SERVER_URL = window.location.origin;

    // Ramanujan 8-Core Hypercube 3D Coordinates (0..7)
    const CORE_POSITIONS = {
        0: new THREE.Vector3(-4, 4, 4),
        1: new THREE.Vector3(4, 4, 4),
        2: new THREE.Vector3(-4, -4, 4),
        3: new THREE.Vector3(4, -4, 4),
        4: new THREE.Vector3(-4, 4, -4),
        5: new THREE.Vector3(4, 4, -4),
        6: new THREE.Vector3(-4, -4, -4),
        7: new THREE.Vector3(4, -4, -4)
    };

    // 3-Regular Hypercube Graph Topology
    const CORE_EDGES = [
        [0, 1], [0, 2], [0, 4],
        [1, 3], [1, 5],
        [2, 3], [2, 6],
        [3, 7],
        [4, 5], [4, 6],
        [5, 7],
        [6, 7]
    ];

    // Initialize Application
    window.addEventListener('load', () => {
        initThreeScene();
        initUI();
        initVoiceGateway();
        startTelemetryPolling();
        startSSEStream();
    });

    /* =========================================================================
       1. Three.js 3D Scene Initialization
       ========================================================================= */
    function initThreeScene() {
        const container = document.getElementById('three-canvas-wrapper');
        const width = container.clientWidth;
        const height = container.clientHeight;

        // Scene
        scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x050C1A, 0.022);

        // Camera
        camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 1000);
        camera.position.set(0, 7, 20);

        // Renderer
        renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(width, height);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        container.appendChild(renderer.domElement);

        // Controls
        controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.maxDistance = 45;
        controls.minDistance = 6;

        // Lights
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
        scene.add(ambientLight);

        const pointLight = new THREE.PointLight(0x00F0FF, 2.2, 50);
        pointLight.position.set(0, 4, 0);
        scene.add(pointLight);

        const goldLight = new THREE.PointLight(0xFF9933, 1.8, 40);
        goldLight.position.set(12, 12, 10);
        scene.add(goldLight);

        // Build Graph Components
        buildFloatingComputerMonitor();
        buildSutraJevHub();
        buildCoreHypercube();
        buildObsidianBrainGraph();
        buildParticlePool();

        // Handle Resize
        window.addEventListener('resize', onWindowResize);

        // Render Loop
        animate();
    }

    /* -------------------------------------------------------------------------
       A. 3D Floating Computer Monitor Mesh & Dynamic Screen Texture
       ------------------------------------------------------------------------- */
    function buildFloatingComputerMonitor() {
        monitorGroup = new THREE.Group();
        monitorGroup.position.set(0, 0.2, 0);

        // Create Offscreen 2D Canvas for Monitor Screen
        screenCanvas = document.createElement('canvas');
        screenCanvas.width = 1024;
        screenCanvas.height = 512;
        screenCtx = screenCanvas.getContext('2d');
        screenTexture = new THREE.CanvasTexture(screenCanvas);

        // Screen Plane Mesh
        const screenGeo = new THREE.PlaneGeometry(6.4, 3.4);
        const screenMat = new THREE.MeshBasicMaterial({ map: screenTexture });
        monitorScreenMesh = new THREE.Mesh(screenGeo, screenMat);
        monitorScreenMesh.position.set(0, 0.2, 0.16);
        monitorGroup.add(monitorScreenMesh);

        // Bezel Outer Metallic Frame
        const bezelGeo = new THREE.BoxGeometry(6.8, 3.8, 0.3);
        const bezelMat = new THREE.MeshPhongMaterial({
            color: 0x0A192F,
            emissive: 0x00F0FF,
            emissiveIntensity: 0.15,
            shininess: 60
        });
        const bezelMesh = new THREE.Mesh(bezelGeo, bezelMat);
        bezelMesh.position.set(0, 0.2, 0);
        monitorGroup.add(bezelMesh);

        // Stand Neck
        const neckGeo = new THREE.CylinderGeometry(0.18, 0.22, 1.2, 16);
        const neckMat = new THREE.MeshPhongMaterial({ color: 0x1A2E4B, shininess: 80 });
        const neckMesh = new THREE.Mesh(neckGeo, neckMat);
        neckMesh.position.set(0, -2.1, -0.1);
        monitorGroup.add(neckMesh);

        // Stand Base
        const baseGeo = new THREE.BoxGeometry(2.4, 0.12, 1.8);
        const baseMat = new THREE.MeshPhongMaterial({ color: 0x0A192F, emissive: 0xFF9933, emissiveIntensity: 0.2 });
        const baseMesh = new THREE.Mesh(baseGeo, baseMat);
        baseMesh.position.set(0, -2.7, 0.2);
        monitorGroup.add(baseMesh);

        // Keyboard Console Deck
        const kbGeo = new THREE.BoxGeometry(4.8, 0.1, 1.6);
        const kbMat = new THREE.MeshPhongMaterial({ color: 0x050C1A, emissive: 0x00F0FF, emissiveIntensity: 0.1 });
        const kbMesh = new THREE.Mesh(kbGeo, kbMat);
        kbMesh.position.set(0, -2.7, 1.8);
        kbMesh.rotation.x = -0.05;
        monitorGroup.add(kbMesh);

        scene.add(monitorGroup);

        // Initial screen draw
        updateMonitorScreenCanvas();
    }

    function updateMonitorScreenCanvas(query = '', response = '', speechText = '', details = {}) {
        if (!screenCtx) return;

        if (query) lastQueryText = query;
        if (response) lastResponseText = response;
        if (speechText) lastSpeechText = speechText;
        if (details.task) currentTaskType = details.task;

        const w = screenCanvas.width;
        const h = screenCanvas.height;

        // Background dark gradient
        const grad = screenCtx.createLinearGradient(0, 0, w, h);
        grad.addColorStop(0, '#050C1A');
        grad.addColorStop(1, '#0A192F');
        screenCtx.fillStyle = grad;
        screenCtx.fillRect(0, 0, w, h);

        // Screen Outer Neon Cyan Glow Border
        screenCtx.strokeStyle = '#00F0FF';
        screenCtx.lineWidth = 6;
        screenCtx.strokeRect(6, 6, w - 12, h - 12);

        // Top Header Display Bar
        screenCtx.fillStyle = 'rgba(0, 240, 255, 0.15)';
        screenCtx.fillRect(10, 10, w - 20, 50);
        screenCtx.font = 'bold 22px "Fira Code", monospace';
        screenCtx.fillStyle = '#FF9933';
        screenCtx.fillText('SUTRAOS SOVEREIGN OS // 3D COMPUTER DISPLAY', 24, 44);

        // System Metrics Bar
        screenCtx.font = '16px "Fira Code", monospace';
        screenCtx.fillStyle = '#00F0FF';
        screenCtx.fillText(`SPECTRAL GAP: 2.000  | JEV: <0.2ms  | SINGLE BRAIN: SYNCED`, 24, 90);

        // Active Command Box
        screenCtx.fillStyle = 'rgba(2, 6, 15, 0.85)';
        screenCtx.fillRect(24, 110, w - 48, 80);
        screenCtx.strokeStyle = 'rgba(255, 153, 51, 0.4)';
        screenCtx.lineWidth = 2;
        screenCtx.strokeRect(24, 110, w - 48, 80);

        screenCtx.font = 'bold 15px "Fira Code", monospace';
        screenCtx.fillStyle = '#FF9933';
        screenCtx.fillText(`> ACTIVE QUERY:`, 36, 136);

        screenCtx.font = '16px "Outfit", sans-serif';
        screenCtx.fillStyle = '#F5F0DC';
        const truncatedQuery = lastQueryText.length > 70 ? lastQueryText.substring(0, 70) + '...' : lastQueryText;
        screenCtx.fillText(`"${truncatedQuery}"`, 36, 166);

        // Hinglish Spoken Speech Response Box
        screenCtx.fillStyle = 'rgba(10, 25, 47, 0.9)';
        screenCtx.fillRect(24, 210, w - 48, 230);
        screenCtx.strokeStyle = '#00FF88';
        screenCtx.lineWidth = 2;
        screenCtx.strokeRect(24, 210, w - 48, 230);

        screenCtx.font = 'bold 16px "Fira Code", monospace';
        screenCtx.fillStyle = '#00FF88';
        screenCtx.fillText(`🗣️ CHIRANSH PANINIAN BHAV SPEECH OUTPUT:`, 36, 242);

        screenCtx.font = '20px "Outfit", sans-serif';
        screenCtx.fillStyle = '#F5F0DC';
        
        // Multi-line wrap for spoken speech text
        const words = lastSpeechText.split(' ');
        let line = '';
        let y = 280;
        for (let i = 0; i < words.length; i++) {
            const testLine = line + words[i] + ' ';
            const metrics = screenCtx.measureText(testLine);
            if (metrics.width > w - 100 && i > 0) {
                screenCtx.fillText(line, 36, y);
                line = words[i] + ' ';
                y += 30;
                if (y > 410) break;
            } else {
                line = testLine;
            }
        }
        if (y <= 410) screenCtx.fillText(line, 36, y);

        // Bottom Status Scanline
        screenCtx.fillStyle = 'rgba(0, 240, 255, 0.2)';
        screenCtx.fillRect(10, h - 30, w - 20, 20);
        screenCtx.font = '13px "Fira Code", monospace';
        screenCtx.fillStyle = '#94A3B8';
        screenCtx.fillText(`SUTRAOS LIVE STREAM // ${new Date().toLocaleTimeString()} // TASK: ${currentTaskType}`, 24, h - 14);

        screenTexture.needsUpdate = true;
    }

    /* -------------------------------------------------------------------------
       B. Orbiting 3D Obsidian Second Brain Node Graph
       ------------------------------------------------------------------------- */
    function buildObsidianBrainGraph() {
        obsidianBrainGroup = new THREE.Group();
        scene.add(obsidianBrainGroup);

        const nodeColors = [0xFF9933, 0x00F0FF, 0x00FF88, 0xA855F7];
        const count = OBSIDIAN_NOTE_TITLES.length;
        const orbitalRadius = 8.5;

        for (let i = 0; i < count; i++) {
            const phi = Math.acos(-1 + (2 * i) / count);
            const theta = Math.sqrt(count * Math.PI) * phi;

            const x = orbitalRadius * Math.cos(theta) * Math.sin(phi);
            const y = orbitalRadius * Math.sin(theta) * Math.sin(phi);
            const z = orbitalRadius * Math.cos(phi);

            const pos = new THREE.Vector3(x, y, z);
            const colorHex = nodeColors[i % nodeColors.length];

            // Node Geometry
            const geo = new THREE.IcosahedronGeometry(0.55, 1);
            const mat = new THREE.MeshPhongMaterial({
                color: colorHex,
                emissive: colorHex,
                emissiveIntensity: 0.75,
                flatShading: true
            });
            const mesh = new THREE.Mesh(geo, mat);
            mesh.position.copy(pos);

            // Wireframe Shell
            const shellGeo = new THREE.SphereGeometry(0.75, 12, 12);
            const shellMat = new THREE.MeshBasicMaterial({ color: colorHex, wireframe: true, transparent: true, opacity: 0.35 });
            const shellMesh = new THREE.Mesh(shellGeo, shellMat);
            mesh.add(shellMesh);

            obsidianBrainGroup.add(mesh);
            obsidianNodes.push({ mesh: mesh, title: OBSIDIAN_NOTE_TITLES[i], color: colorHex, basePos: pos.clone() });
        }

        // Draw Inter-Note Constellation Edges
        for (let i = 0; i < count; i++) {
            const nextIdx = (i + 1) % count;
            const skipIdx = (i + 4) % count;
            createEdgeLineInGroup(obsidianBrainGroup, obsidianNodes[i].basePos, obsidianNodes[nextIdx].basePos, 0xA855F7, 0.35);
            createEdgeLineInGroup(obsidianBrainGroup, obsidianNodes[i].basePos, obsidianNodes[skipIdx].basePos, 0x00F0FF, 0.25);
        }
    }

    function createEdgeLineInGroup(group, p1, p2, colorHex, opacityVal) {
        const points = [p1, p2];
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        const material = new THREE.LineBasicMaterial({ color: colorHex, transparent: true, opacity: opacityVal });
        const line = new THREE.Line(geometry, material);
        group.add(line);
    }

    /* -------------------------------------------------------------------------
       C. SutraJev Hub, Ramanujan Hypercube & Particle Pool
       ------------------------------------------------------------------------- */
    function buildSutraJevHub() {
        const geometry = new THREE.OctahedronGeometry(1.2, 1);
        const material = new THREE.MeshPhongMaterial({
            color: 0xFF9933,
            emissive: 0xFF9933,
            emissiveIntensity: 0.7,
            flatShading: true
        });
        jevNodeMesh = new THREE.Mesh(geometry, material);
        jevNodeMesh.position.set(0, -3.2, 0);
        scene.add(jevNodeMesh);

        const ringGeo = new THREE.RingGeometry(1.8, 2.1, 32);
        const ringMat = new THREE.MeshBasicMaterial({ color: 0xFF9933, side: THREE.DoubleSide, transparent: true, opacity: 0.6 });
        jevRingMesh = new THREE.Mesh(ringGeo, ringMat);
        jevRingMesh.rotation.x = Math.PI / 2;
        jevRingMesh.position.set(0, -3.2, 0);
        scene.add(jevRingMesh);
    }

    function buildCoreHypercube() {
        for (let i = 0; i < 8; i++) {
            const pos = CORE_POSITIONS[i];
            const nodeGroup = new THREE.Group();
            nodeGroup.position.copy(pos);

            const sphereGeo = new THREE.SphereGeometry(0.65, 16, 16);
            const sphereMat = new THREE.MeshPhongMaterial({
                color: 0x00F0FF,
                emissive: 0x00F0FF,
                emissiveIntensity: 0.5
            });
            const sphereMesh = new THREE.Mesh(sphereGeo, sphereMat);
            nodeGroup.add(sphereMesh);

            const cageGeo = new THREE.BoxGeometry(1.4, 1.4, 1.4);
            const cageMat = new THREE.MeshBasicMaterial({ color: 0x00F0FF, wireframe: true, transparent: true, opacity: 0.3 });
            const cageMesh = new THREE.Mesh(cageGeo, cageMat);
            nodeGroup.add(cageMesh);

            scene.add(nodeGroup);
            coreNodes[i] = { group: nodeGroup, sphere: sphereMesh, cage: cageMesh, load: 0 };

            createEdgeLine(new THREE.Vector3(0, -3.2, 0), pos, 0xFF9933, 0.2);
        }

        CORE_EDGES.forEach(([c1, c2]) => {
            createEdgeLine(CORE_POSITIONS[c1], CORE_POSITIONS[c2], 0x00F0FF, 0.35);
        });
    }

    function createEdgeLine(p1, p2, colorHex, opacityVal) {
        const points = [p1, p2];
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        const material = new THREE.LineBasicMaterial({ color: colorHex, transparent: true, opacity: opacityVal });
        const line = new THREE.Line(geometry, material);
        scene.add(line);
        edgeLines.push({ line: line, p1: p1, p2: p2 });
    }

    function buildParticlePool() {
        for (let i = 0; i < 25; i++) {
            const pGeo = new THREE.SphereGeometry(0.14, 8, 8);
            const pMat = new THREE.MeshBasicMaterial({ color: 0x00FF88 });
            const pMesh = new THREE.Mesh(pGeo, pMat);
            pMesh.visible = false;
            scene.add(pMesh);
            particlePool.push({ mesh: pMesh, active: false, progress: 0, p1: null, p2: null, speed: 0.035 });
        }
    }

    function triggerParticlePulse(fromPos, toPos, colorHex = 0x00FF88) {
        const p = particlePool.find(item => !item.active);
        if (p) {
            p.active = true;
            p.progress = 0;
            p.p1 = fromPos;
            p.p2 = toPos;
            p.mesh.material.color.setHex(colorHex);
            p.mesh.position.copy(fromPos);
            p.mesh.visible = true;
        }
    }

    /* -------------------------------------------------------------------------
       D. Animation Loop
       ------------------------------------------------------------------------- */
    function animate() {
        requestAnimationFrame(animate);

        const now = performance.now();
        const elapsedTime = now * 0.001;

        frameCount++;
        if (now - lastFrameTime >= 1000) {
            document.getElementById('fps-counter').textContent = frameCount;
            frameCount = 0;
            lastFrameTime = now;
        }

        // Float 3D Computer Monitor gently
        if (monitorGroup) {
            monitorGroup.position.y = 0.2 + Math.sin(elapsedTime * 1.5) * 0.15;
        }

        // Rotate Orbiting Obsidian Brain Graph
        if (obsidianBrainGroup) {
            obsidianBrainGroup.rotation.y += 0.004;
            obsidianBrainGroup.rotation.x = Math.sin(elapsedTime * 0.5) * 0.1;
        }

        // Rotate Jev Hub
        if (jevNodeMesh) {
            jevNodeMesh.rotation.y += 0.012;
            jevNodeMesh.rotation.x += 0.006;
        }
        if (jevRingMesh) {
            jevRingMesh.rotation.z += 0.018;
        }

        // Rotate Core Cages
        Object.values(coreNodes).forEach(node => {
            node.cage.rotation.x += 0.01;
            node.cage.rotation.y += 0.01;
        });

        // Update Particle Pulses
        particlePool.forEach(p => {
            if (p.active) {
                p.progress += p.speed;
                if (p.progress >= 1.0) {
                    p.active = false;
                    p.mesh.visible = false;
                } else {
                    p.mesh.position.lerpVectors(p.p1, p.p2, p.progress);
                }
            }
        });

        controls.update();
        renderer.render(scene, camera);
    }

    function onWindowResize() {
        const container = document.getElementById('three-canvas-wrapper');
        const width = container.clientWidth;
        const height = container.clientHeight;
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        renderer.setSize(width, height);
    }

    /* =========================================================================
       2. UI & Terminal Interaction
       ========================================================================= */
    function initUI() {
        const tabBtns = document.querySelectorAll('.tab-btn');
        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                tabBtns.forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
                btn.classList.add('active');
                const targetId = btn.getAttribute('data-tab');
                document.getElementById(targetId).classList.add('active');
            });
        });

        const inputEl = document.getElementById('converse-input');
        const sendBtn = document.getElementById('converse-send-btn');

        sendBtn.addEventListener('click', () => {
            sendConverseQuery(inputEl.value);
            inputEl.value = '';
        });

        inputEl.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendConverseQuery(inputEl.value);
                inputEl.value = '';
            }
        });

        const taskCards = document.querySelectorAll('.task-card');
        taskCards.forEach(card => {
            card.addEventListener('click', () => {
                const cmd = card.getAttribute('data-cmd');
                sendConverseQuery(cmd);
            });
        });

        buildCoresGridUI();
    }

    function buildCoresGridUI() {
        const container = document.getElementById('cores-load-grid');
        container.innerHTML = '';
        for (let i = 0; i < 8; i++) {
            const card = document.createElement('div');
            card.className = 'core-card';
            card.id = `core-card-${i}`;
            card.innerHTML = `
                <span class="core-id">CORE ${i}</span>
                <span class="core-tasks-count" id="core-task-val-${i}">0</span>
                <span class="core-tasks-label">TASKS</span>
            `;
            container.appendChild(card);
        }
    }

    function appendTerminalLog(type, text) {
        const container = document.getElementById('terminal-output');
        const entry = document.createElement('div');
        entry.className = `log-entry ${type}`;
        const timeStr = new Date().toLocaleTimeString();
        entry.innerHTML = `<span class="log-time">[${timeStr}]</span> <span class="log-text">${escapeHtml(text)}</span>`;
        container.appendChild(entry);
        container.scrollTop = container.scrollHeight;
    }

    function updateSpeechBubbleOverlay(speechText) {
        const overlay = document.getElementById('speech-bubble-overlay');
        const textEl = document.getElementById('speech-bubble-text');
        const timeEl = document.getElementById('speech-bubble-time');

        if (textEl && speechText) {
            textEl.textContent = `"${speechText}"`;
        }
        if (timeEl) {
            timeEl.textContent = new Date().toLocaleTimeString();
        }
        if (overlay) {
            overlay.classList.remove('pulse');
            void overlay.offsetWidth; // trigger reflow
            overlay.classList.add('pulse');
        }
    }

    function escapeHtml(str) {
        return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    /* =========================================================================
       3. Conversational API Execution
       ========================================================================= */
    function sendConverseQuery(queryText) {
        if (!queryText.trim()) return;

        appendTerminalLog('user', `Query: "${queryText}"`);

        // Trigger 3D Particle Pulses to Monitor & Cores
        triggerParticlePulse(new THREE.Vector3(0, -3.2, 0), monitorGroup.position, 0x00FF88);
        triggerParticlePulse(monitorGroup.position, CORE_POSITIONS[0], 0x00F0FF);

        fetch(`${SERVER_URL}/api/converse`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: queryText, source: 'text' })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const jev = data.jev_decision || {};
                const speechText = data.speech_text || data.response || 'Task executed.';

                appendTerminalLog('system', `[SutraJev Decision] Intent: ${jev.choice} | Conf: ${((jev.confidence || 0)*100).toFixed(1)}% | Safety: ${jev.safety_score}/10`);
                appendTerminalLog('bot', speechText);

                // Update 3D Floating Monitor Screen Canvas & Floating Speech Bubble Overlay
                updateMonitorScreenCanvas(queryText, data.response, speechText, { task: jev.choice });
                updateSpeechBubbleOverlay(speechText);

                // Trigger 3D Pulses across Obsidian Brain Nodes & Core Nodes
                const coreId = data.telemetry ? data.telemetry.core_assigned : 0;
                const corePos = CORE_POSITIONS[coreId] || CORE_POSITIONS[0];
                triggerParticlePulse(monitorGroup.position, corePos, 0xFF9933);

                if (obsidianNodes.length > 0) {
                    const randomObsNode = obsidianNodes[Math.floor(Math.random() * obsidianNodes.length)];
                    triggerParticlePulse(corePos, randomObsNode.basePos, 0xA855F7);
                }
            } else {
                const errSpeech = data.speech_text || data.response || data.error || 'Execution failed.';
                appendTerminalLog('error', errSpeech);
                updateMonitorScreenCanvas(queryText, data.error, errSpeech, { task: 'ERROR' });
                updateSpeechBubbleOverlay(errSpeech);
            }
        })
        .catch(err => {
            const connErr = `Connection error: ${err.message}`;
            appendTerminalLog('error', connErr);
            updateMonitorScreenCanvas(queryText, connErr, connErr, { task: 'NETWORK_ERROR' });
        });
    }

    /* =========================================================================
       4. Chiransh Voice Gateway
       ========================================================================= */
    function initVoiceGateway() {
        const voiceBtn = document.getElementById('voice-btn');
        const voiceStatus = document.getElementById('voice-status');

        let recognition = null;
        let isListening = false;

        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRec();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';

            recognition.onstart = () => {
                isListening = true;
                voiceBtn.classList.add('listening');
                voiceStatus.textContent = 'Listening...';
            };

            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                voiceStatus.textContent = 'Processing...';
                sendConverseQuery(transcript);
            };

            recognition.onerror = () => {
                voiceStatus.textContent = 'Voice Error';
                stopListening();
            };

            recognition.onend = () => {
                stopListening();
            };
        } else {
            voiceStatus.textContent = 'Push-to-Talk (Simulated)';
        }

        function stopListening() {
            isListening = false;
            voiceBtn.classList.remove('listening');
            voiceStatus.textContent = 'Standby';
        }

        voiceBtn.addEventListener('click', () => {
            if (recognition) {
                if (isListening) {
                    recognition.stop();
                } else {
                    recognition.start();
                }
            } else {
                const sampleVoiceCmd = "check polymarket misprice signals";
                voiceStatus.textContent = "Spoken: " + sampleVoiceCmd;
                sendConverseQuery(sampleVoiceCmd);
                setTimeout(stopListening, 2000);
            }
        });
    }

    /* =========================================================================
       5. Telemetry & Sentinel Polling
       ========================================================================= */
    function startTelemetryPolling() {
        setInterval(fetchTelemetry, 3000);
        fetchTelemetry();
    }

    function startSSEStream() {
        if ('EventSource' in window) {
            try {
                const es = new EventSource(`${SERVER_URL}/api/telemetry/stream`);
                es.onmessage = (e) => {
                    try {
                        const data = JSON.parse(e.data);
                        updateTelemetryUI(data);
                    } catch (err) {}
                };
            } catch (err) {}
        }
    }

    function fetchTelemetry() {
        fetch(`${SERVER_URL}/api/telemetry`)
            .then(res => res.json())
            .then(data => {
                updateTelemetryUI(data);
            })
            .catch(() => {});
    }

    function updateTelemetryUI(data) {
        if (!data) return;

        const sched = data.scheduler || {};
        const load = sched.load || {};

        let totalTasks = 0;
        for (let i = 0; i < 8; i++) {
            const tasks = load[i] || [];
            totalTasks += tasks.length;

            const el = document.getElementById(`core-task-val-${i}`);
            if (el) el.textContent = tasks.length;

            if (coreNodes[i]) {
                coreNodes[i].load = tasks.length;
                if (tasks.length > 2) {
                    coreNodes[i].sphere.material.color.setHex(0xFF4757);
                } else if (tasks.length > 0) {
                    coreNodes[i].sphere.material.color.setHex(0xFF9933);
                } else {
                    coreNodes[i].sphere.material.color.setHex(0x00F0FF);
                }
            }
        }

        activeTasksCount = totalTasks;
        const activeTasksEl = document.getElementById('active-tasks-val');
        if (activeTasksEl) activeTasksEl.textContent = totalTasks;

        const sg = data.spectral_gap || {};
        if (sg.spectral_gap !== undefined) {
            const sgEl = document.getElementById('spectral-gap-val');
            if (sgEl) sgEl.textContent = sg.spectral_gap.toFixed(3);
        }

        const allocs = data.allocations || {};
        const caps = data.capabilities || {};
        const tbody = document.getElementById('nyaya-table-body');
        if (tbody) {
            tbody.innerHTML = '';
            Object.keys(allocs).forEach(proc => {
                const tr = document.createElement('tr');
                const capList = (caps[proc] || []).join(', ');
                tr.innerHTML = `
                    <td>${escapeHtml(proc)}</td>
                    <td>${allocs[proc]} Bytes</td>
                    <td>${escapeHtml(capList)}</td>
                    <td><span class="badge-symbolic">SANDBOX_APPROVED</span></td>
                `;
                tbody.appendChild(tr);
            });
        }

        const events = data.events || [];
        const latestSentinel = events.slice().reverse().find(e => e.type === 'SENTINEL_HEARTBEAT');
        if (latestSentinel && latestSentinel.details) {
            const det = latestSentinel.details;
            if (det.battery && document.getElementById('sentinel-batt')) {
                document.getElementById('sentinel-batt').textContent = `${det.battery.percentage}%`;
            }
            if (det.thermal && document.getElementById('sentinel-temp')) {
                document.getElementById('sentinel-temp').textContent = `${det.thermal.cpu_temp_c}°C`;
            }
            if (det.poly_signal && document.getElementById('sentinel-poly')) {
                document.getElementById('sentinel-poly').textContent = det.poly_signal.signal || 'ACTIVE';
            }
        }
    }

})();
