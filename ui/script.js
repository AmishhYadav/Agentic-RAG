/* ═══════════════════════════════════════════════
   Agentic RAG — UI Controller
   ═══════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
    // ─── Element References ───
    const form = document.getElementById('query-form');
    const input = document.getElementById('query-input');
    const sendBtn = document.getElementById('send-btn');
    const chatHistory = document.getElementById('chat-history');
    const stepsContainer = document.getElementById('steps-container');
    const clearChatBtn = document.getElementById('clear-chat-btn');
    const toggleReasoningBtn = document.getElementById('toggle-reasoning-btn');
    const reasoningPanel = document.getElementById('reasoning-panel');

    // Sidebar elements
    const sidebar = document.getElementById('sidebar');
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const navItems = document.querySelectorAll('.menu-item[data-panel]');

    // Document upload elements
    const uploadZone = document.getElementById('upload-zone');
    const fileInput = document.getElementById('file-input');
    const docList = document.getElementById('doc-list');
    const docCount = document.getElementById('doc-count');

    // Settings elements
    const tempSlider = document.getElementById('setting-temperature');
    const tempValue = document.getElementById('temp-value');
    const kSlider = document.getElementById('setting-k');
    const kValue = document.getElementById('k-value');

    // Suggestion chips
    const chips = document.querySelectorAll('.chip');

    let isProcessing = false;
    let documents = [];

    // ═══════════════════════════════════════════════
    //  NAVIGATION
    // ═══════════════════════════════════════════════

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const panelId = item.dataset.panel;

            // Update active menu item
            navItems.forEach(n => n.classList.remove('active'));
            item.classList.add('active');

            // Show target panel
            document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
            const targetPanel = document.getElementById(`panel-${panelId}`);
            if (targetPanel) targetPanel.classList.add('active');

            // Close mobile sidebar
            sidebar.classList.remove('open');
        });
    });

    // Mobile menu toggle
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
    }

    // Close sidebar on outside click (mobile)
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 768 && sidebar.classList.contains('open')) {
            if (!sidebar.contains(e.target) && !mobileMenuBtn.contains(e.target)) {
                sidebar.classList.remove('open');
            }
        }
    });


    // ═══════════════════════════════════════════════
    //  CHAT FUNCTIONALITY
    // ═══════════════════════════════════════════════

    // Enable/disable send button based on input
    input.addEventListener('input', () => {
        sendBtn.disabled = !input.value.trim() || isProcessing;
    });

    // Suggestion chips
    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            const query = chip.dataset.query;
            input.value = query;
            sendBtn.disabled = false;
            input.focus();
            // Auto-submit
            form.dispatchEvent(new Event('submit'));
        });
    });

    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const query = input.value.trim();
        if (!query || isProcessing) return;

        isProcessing = true;
        sendBtn.disabled = true;

        // Remove welcome card if present
        const welcomeCard = chatHistory.querySelector('.welcome-card');
        if (welcomeCard) welcomeCard.remove();

        // Add user message
        addMessage(query, 'user');
        input.value = '';

        // Clear previous steps
        stepsContainer.innerHTML = '';

        // Show typing indicator
        const typingEl = showTypingIndicator();

        // Collected data for source attribution
        let collectedSources = [];
        let verificationResult = null;

        // Start Event Stream
        const eventSource = new EventSource(`/stream_query?q=${encodeURIComponent(query)}`);

        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);

            if (data.step === 'complete') {
                eventSource.close();
                removeTypingIndicator(typingEl);

                // Add answer with source attribution and verification
                addMessage(
                    data.final_response.answer,
                    'system',
                    collectedSources,
                    data.final_response.verification
                );

                isProcessing = false;
                sendBtn.disabled = !input.value.trim();
            } else if (data.step === 'error') {
                eventSource.close();
                removeTypingIndicator(typingEl);
                addMessage(`⚠️ Error: ${data.message}`, 'system');
                isProcessing = false;
                sendBtn.disabled = !input.value.trim();
            } else {
                // Collect source information from retrieval agent
                if (data.step === 'retrieval_agent' && data.data) {
                    if (Array.isArray(data.data)) {
                        collectedSources = data.data.map(d => d.source).filter(Boolean);
                    }
                }
                // Collect verification info
                if (data.step === 'verifier_agent' && data.data) {
                    verificationResult = data.data;
                }
                addStep(data);
            }
        };

        eventSource.onerror = () => {
            eventSource.close();
            removeTypingIndicator(typingEl);
            addMessage('⚠️ Connection lost. Please try again.', 'system');
            isProcessing = false;
            sendBtn.disabled = !input.value.trim();
        };
    });


    // ─── Message Rendering ───
    function addMessage(text, role, sources = [], verification = null) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role === 'user' ? 'user-msg' : 'system-msg'}`;

        const avatar = role === 'user' ? '👤' : '🤖';
        const name = role === 'user' ? 'You' : 'Agent';

        let sourcesHTML = '';
        if (sources && sources.length > 0) {
            const uniqueSources = [...new Set(sources)];
            sourcesHTML = `
                <div class="msg-sources">
                    ${uniqueSources.map(s => `<span class="source-tag">📄 ${s}</span>`).join('')}
                </div>
            `;
        }

        let verificationHTML = '';
        if (verification) {
            const isValid = verification.is_valid;
            verificationHTML = `
                <div class="verification-badge ${isValid ? 'verified' : 'unverified'}">
                    ${isValid ? '✅ Verified' : '⚠️ Unverified'} — ${verification.reasoning || ''}
                </div>
            `;
        }

        msgDiv.innerHTML = `
            <div class="msg-avatar">${avatar}</div>
            <div class="msg-body">
                <span class="msg-name">${name}</span>
                <div class="msg-bubble">
                    ${escapeHtml(text)}
                    ${sourcesHTML}
                    ${verificationHTML}
                </div>
            </div>
        `;

        chatHistory.appendChild(msgDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }


    // ─── Typing Indicator ───
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message system-msg typing-msg';
        typingDiv.innerHTML = `
            <div class="msg-avatar">🤖</div>
            <div class="msg-body">
                <span class="msg-name">Agent</span>
                <div class="msg-bubble">
                    <div class="typing-indicator">
                        <span></span><span></span><span></span>
                    </div>
                </div>
            </div>
        `;
        chatHistory.appendChild(typingDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
        return typingDiv;
    }

    function removeTypingIndicator(el) {
        if (el && el.parentNode) el.parentNode.removeChild(el);
    }


    // ─── Step Rendering ───
    function addStep(data) {
        const stepDiv = document.createElement('div');
        stepDiv.className = `step-card ${data.step}`;

        const agentNames = {
            'start': '🚀 Start',
            'router': '🔀 Router',
            'query_agent': '🔍 Query Agent',
            'retrieval_agent': '📚 Retrieval Agent',
            'synthesis_agent': '✨ Synthesis Agent',
            'verifier_agent': '🛡️ Verifier Agent',
        };

        const label = agentNames[data.step] || data.step.replace(/_/g, ' ');
        const time = new Date().toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });

        let dataHTML = '';
        if (data.data) {
            dataHTML = `<div class="step-data">${JSON.stringify(data.data, null, 2)}</div>`;
        }

        stepDiv.innerHTML = `
            <div class="step-header">
                <span class="step-label">${label}</span>
                <span class="step-time">${time}</span>
            </div>
            <div class="step-msg">${data.message}</div>
            ${dataHTML}
        `;

        stepsContainer.appendChild(stepDiv);
        stepsContainer.scrollTop = stepsContainer.scrollHeight;
    }


    // ─── Clear Chat ───
    if (clearChatBtn) {
        clearChatBtn.addEventListener('click', () => {
            chatHistory.innerHTML = '';
            stepsContainer.innerHTML = `
                <div class="stream-empty">
                    <div class="empty-brain">🧠</div>
                    <p>Agent cognition will appear here when you submit a query.</p>
                </div>
            `;

            // Re-add welcome card
            const welcomeHTML = `
                <div class="welcome-card">
                    <div class="welcome-icon">
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="url(#welcomeGrad2)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                            <defs><linearGradient id="welcomeGrad2" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#3d8bff"/><stop offset="100%" stop-color="#9d5cff"/></linearGradient></defs>
                            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                        </svg>
                    </div>
                    <h3>Welcome to Agentic RAG</h3>
                    <p>I'm an autonomous AI assistant. Ask me anything about your knowledge base.</p>
                    <div class="suggestion-chips">
                        <button class="chip" data-query="What is Amazon Bedrock?">What is Amazon Bedrock?</button>
                        <button class="chip" data-query="Explain IAM security best practices">IAM Security</button>
                        <button class="chip" data-query="How does RAG architecture work?">How does RAG work?</button>
                    </div>
                </div>
            `;
            chatHistory.innerHTML = welcomeHTML;

            // Re-bind chip events
            chatHistory.querySelectorAll('.chip').forEach(chip => {
                chip.addEventListener('click', () => {
                    input.value = chip.dataset.query;
                    sendBtn.disabled = false;
                    input.focus();
                    form.dispatchEvent(new Event('submit'));
                });
            });
        });
    }


    // ─── Toggle Reasoning Panel ───
    if (toggleReasoningBtn) {
        toggleReasoningBtn.addEventListener('click', () => {
            reasoningPanel.classList.toggle('collapsed');
        });
    }


    // ═══════════════════════════════════════════════
    //  DOCUMENT UPLOAD
    // ═══════════════════════════════════════════════

    if (uploadZone && fileInput) {
        uploadZone.addEventListener('click', () => fileInput.click());

        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('drag-over');
        });

        uploadZone.addEventListener('dragleave', () => {
            uploadZone.classList.remove('drag-over');
        });

        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('drag-over');
            handleFiles(e.dataTransfer.files);
        });

        fileInput.addEventListener('change', () => {
            handleFiles(fileInput.files);
            fileInput.value = '';
        });
    }

    function handleFiles(files) {
        Array.from(files).forEach(file => {
            const ext = file.name.split('.').pop().toLowerCase();
            if (!['txt', 'md', 'pdf'].includes(ext)) return;

            const doc = {
                name: file.name,
                size: formatFileSize(file.size),
                date: new Date().toLocaleDateString(),
                id: Date.now() + Math.random()
            };
            documents.push(doc);
            renderDocList();

            // Upload to server
            const formData = new FormData();
            formData.append('file', file);
            fetch('/upload_document', {
                method: 'POST',
                body: formData
            }).catch(() => {
                // Silently handle if endpoint doesn't exist yet
            });
        });
    }

    function renderDocList() {
        if (!docList) return;
        docCount.textContent = documents.length;
        docList.innerHTML = documents.map(doc => `
            <div class="doc-item" data-id="${doc.id}">
                <div class="doc-info">
                    <span class="doc-icon">📄</span>
                    <div>
                        <div class="doc-name">${doc.name}</div>
                        <div class="doc-meta">${doc.size} · ${doc.date}</div>
                    </div>
                </div>
                <div class="doc-actions">
                    <button class="doc-action-btn" onclick="removeDoc(${doc.id})">🗑️</button>
                </div>
            </div>
        `).join('');
    }

    // Expose for inline onclick
    window.removeDoc = function (id) {
        documents = documents.filter(d => d.id !== id);
        renderDocList();
    };


    // ═══════════════════════════════════════════════
    //  SETTINGS
    // ═══════════════════════════════════════════════

    if (tempSlider && tempValue) {
        tempSlider.addEventListener('input', () => {
            tempValue.textContent = tempSlider.value;
        });
    }

    if (kSlider && kValue) {
        kSlider.addEventListener('input', () => {
            kValue.textContent = kSlider.value;
        });
    }


    // ═══════════════════════════════════════════════
    //  SYSTEM STATUS
    // ═══════════════════════════════════════════════

    async function checkSystemStatus() {
        try {
            const resp = await fetch('/health');
            if (resp.ok) {
                const data = await resp.json();
                const dot = document.getElementById('status-dot');
                const label = document.getElementById('status-label');
                const badge = document.getElementById('provider-badge');

                if (dot) dot.className = 'status-dot online';
                if (label) label.textContent = 'System Ready';
                if (badge && data.provider) {
                    badge.querySelector('span').textContent = data.provider.toUpperCase();
                }
            }
        } catch {
            // Server not reachable, keep default state
        }
    }

    checkSystemStatus();


    // ═══════════════════════════════════════════════
    //  UTILITIES
    // ═══════════════════════════════════════════════

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        const kb = bytes / 1024;
        if (kb < 1024) return kb.toFixed(1) + ' KB';
        return (kb / 1024).toFixed(1) + ' MB';
    }

    // Keyboard shortcut: Enter to submit
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!sendBtn.disabled) {
                form.dispatchEvent(new Event('submit'));
            }
        }
    });
});
