document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('query-form');
    const input = document.getElementById('query-input');
    const chatHistory = document.getElementById('chat-history');
    const stepsContainer = document.getElementById('steps-container');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const query = input.value.trim();
        if (!query) return;

        // Add User Message
        addMessage(query, 'user');
        input.value = '';
        
        // Clear previous steps
        stepsContainer.innerHTML = '';
        
        // Start Event Stream
        const eventSource = new EventSource(`/stream_query?q=${encodeURIComponent(query)}`);
        
        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.step === 'complete') {
                eventSource.close();
                addMessage(data.final_response.answer, 'system');
            } else if (data.step === 'error') {
                eventSource.close();
                addMessage(`Error: ${data.message}`, 'system');
            } else {
                addStep(data);
            }
        };

        eventSource.onerror = () => {
            eventSource.close();
        };
    });

    function addMessage(text, role) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role}`;
        
        const avatar = role === 'user' ? '👤' : '🤖';
        
        msgDiv.innerHTML = `
            <div class="avatar">${avatar}</div>
            <div class="content">${text}</div>
        `;
        
        chatHistory.appendChild(msgDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function addStep(data) {
        const stepDiv = document.createElement('div');
        stepDiv.className = `step-card ${data.step}`;
        
        let extraContent = '';
        if (data.data) {
            extraContent = `<div class="agent-data">${JSON.stringify(data.data, null, 2)}</div>`;
        }

        stepDiv.innerHTML = `
            <div class="step-header">
                <span>${data.step.replace('_', ' ')}</span>
                <span>${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'})}</span>
            </div>
            <div class="step-msg">${data.message}</div>
            ${extraContent}
        `;
        
        stepsContainer.appendChild(stepDiv);
        stepsContainer.scrollTop = stepsContainer.scrollHeight;
    }
});
