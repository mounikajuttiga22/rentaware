document.addEventListener('DOMContentLoaded', () => {
    const uploadBtn = document.getElementById('uploadBtn');
    const fileInput = document.getElementById('fileInput');
    const uploadModal = document.getElementById('uploadModal');
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const chatContainer = document.getElementById('chatContainer');

    let currentDocId = null;

    // Chart Initialization
    const ctx = document.getElementById('riskChart').getContext('2d');
    const riskChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [0, 100],
                backgroundColor: ['#E5E7EB', '#E5E7EB'],
                borderWidth: 0
            }]
        },
        options: {
            cutout: '80%',
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false }, tooltip: { enabled: false } }
        }
    });

    // Handle Upload
    uploadBtn.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        uploadModal.style.display = 'block';

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('http://localhost:8000/upload/', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                currentDocId = data.id;
                await pollForCompletion(currentDocId);
            } else {
                alert('Upload failed. Please try again.');
                uploadModal.style.display = 'none';
            }
        } catch (error) {
            console.error('Error:', error);
            uploadModal.style.display = 'none';
        }
    });

    async function pollForCompletion(docId) {
        const interval = setInterval(async () => {
            const response = await fetch(`http://localhost:8000/documents/${docId}`);
            const data = await response.json();

            if (data.status === 'completed') {
                clearInterval(interval);
                updateUI(data);
                uploadModal.style.display = 'none';
            }
        }, 2000);
    }

    function updateUI(data) {
        // Update Risk Score
        const riskScore = data.risk_scores[0];
        const totalRisk = (riskScore.financial_risk + riskScore.legal_risk) / 2;

        let color = '#10B981'; // Success (Low)
        if (totalRisk > 60) color = '#EF4444'; // Danger (High)
        else if (totalRisk > 30) color = '#F59E0B'; // Warning (Medium)

        riskChart.data.datasets[0].data = [totalRisk, 100 - totalRisk];
        riskChart.data.datasets[0].backgroundColor = [color, '#E5E7EB'];
        riskChart.update();

        document.getElementById('riskLevel').innerText = riskScore.category;
        document.getElementById('riskLevel').style.color = color;
        document.getElementById('riskReason').innerText = riskScore.reason;

        // Update Clauses
        const clausesList = document.getElementById('clausesList');
        clausesList.innerHTML = '';
        data.clauses.forEach(clause => {
            const item = document.createElement('div');
            item.className = 'clause-item';

            // Add a "view" button for detected clauses
            const actionBtn = clause.detected
                ? `<button class="btn-text" onclick="showClauseDetail('${clause.name}', '${clause.content.replace(/'/g, "\\'")}')">View Details</button>`
                : '';

            item.innerHTML = `
                <div class="clause-info">
                    <span class="clause-name">${clause.name}</span>
                    <span class="status ${clause.detected ? 'detected' : 'missing'}">
                        ${clause.detected ? '✔️ Detected' : '❌ Not Found'}
                    </span>
                </div>
                ${actionBtn}
            `;
            clausesList.appendChild(item);
        });

        // Update Alerts
        const alertsList = document.getElementById('alertsList');
        alertsList.innerHTML = '';
        data.alerts.forEach(alert => {
            const date = new Date(alert.deadline).toLocaleDateString();
            const item = document.createElement('div');
            item.className = 'alert-item';
            item.innerHTML = `
                <div class="alert-icon">🔔</div>
                <div class="alert-content">
                    <strong>${alert.type}</strong>
                    <span>Due on ${date}</span>
                </div>
            `;
            alertsList.appendChild(item);
        });
    }

    // Global function for clause detail (added to window for inline onclick)
    window.showClauseDetail = (name, content) => {
        const modal = document.getElementById('detailModal');
        document.getElementById('detailTitle').innerText = name;
        document.getElementById('detailContent').innerText = content;
        modal.style.display = 'block';
    };

    window.closeModal = (id) => {
        document.getElementById(id).style.display = 'none';
    };

    // Handle Chat
    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    async function sendMessage() {
        const text = chatInput.value.trim();
        if (!text || !currentDocId) return;

        // Add user message
        addChatMessage(text, 'user');
        chatInput.value = '';

        // Add typing indicator
        const typingId = 'typing-' + Date.now();
        addChatMessage('AI is thinking...', 'system', typingId);

        try {
            const response = await fetch(`http://localhost:8000/chatbot/${currentDocId}?query=${encodeURIComponent(text)}`, {
                method: 'POST'
            });
            const data = await response.json();

            // Remove typing indicator and add response
            const typingMsg = document.getElementById(typingId);
            if (typingMsg) typingMsg.remove();

            addChatMessage(data.response, 'system');
        } catch (error) {
            console.error('Error:', error);
            const typingMsg = document.getElementById(typingId);
            if (typingMsg) typingMsg.remove();
            addChatMessage('Error connecting to AI. Please try again.', 'system');
        }
    }

    function addChatMessage(text, sender, id = null) {
        const msg = document.createElement('div');
        msg.className = `chat-msg ${sender}`;
        if (id) msg.id = id;
        msg.innerText = text;
        chatContainer.appendChild(msg);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
});
