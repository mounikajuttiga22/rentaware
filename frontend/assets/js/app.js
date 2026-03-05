const API = "http://127.0.0.1:8000";

let currentDocId = null;
let userPhone = null;

const uploadBtn = document.getElementById("uploadBtn");
const fileInput = document.getElementById("fileInput");

const ctx = document.getElementById("riskChart").getContext("2d");

const riskChart = new Chart(ctx, {
    type: "doughnut",
    data: {
        datasets: [{
            data: [0, 100],
            backgroundColor: ["#6366f1", "#e2e8f0"]
        }]
    },
    options: {
        cutout: "75%",
        responsive: true,
        maintainAspectRatio: false,
        plugins: { 
            legend: { display: false },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        return `Risk: ${Math.round(context.parsed)}%`;
                    }
                }
            }
        }
    }
});

uploadBtn.onclick = () => {
    if (!userPhone) {
        userPhone = prompt("Enter your phone number (e.g., +919876543210):");
        if (!userPhone) {
            alert("Phone number is required for SMS alerts");
            return;
        }
    }
    fileInput.click();
};

fileInput.onchange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    uploadBtn.innerText = "Uploading...";
    uploadBtn.disabled = true;

    document.getElementById("clausesList").innerHTML =
        "<div class='empty-state'><i class='fas fa-spinner fa-spin'></i><p>Processing document...</p></div>";

    try {
        const formData = new FormData();
        formData.append("file", file);

        const res = await fetch(API + "/upload/?phone=" + encodeURIComponent(userPhone), {
            method: "POST",
            body: formData
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || `Server error: ${res.status}`);
        }

        const data = await res.json();
        currentDocId = data.id;

        console.log("Upload response:", data);

        const result = await fetch(API + "/documents/" + currentDocId);
        if (!result.ok) throw new Error("Failed to fetch document");
        
        const finalData = await result.json();

        updateUI(finalData);

    } catch (err) {
        console.error("Upload failed:", err);
        document.getElementById("clausesList").innerHTML =
            `<div class='empty-state' style='color:#ef4444;'><i class='fas fa-exclamation-circle'></i><p>Upload failed: ${err.message}</p></div>`;
    } finally {
        uploadBtn.innerText = "Upload Agreement";
        uploadBtn.disabled = false;
        fileInput.value = "";
    }
};

function updateUI(data) {
    /* ---------- Risk ---------- */
    if (data.risk_scores && data.risk_scores.length) {
        const r = data.risk_scores[0];
        const score = (r.financial_risk + r.legal_risk) / 2;

        let color = "#10b981";
        if (score > 60) color = "#ef4444";
        else if (score > 30) color = "#f59e0b";

        riskChart.data.datasets[0].backgroundColor = [color, "#e2e8f0"];
        riskChart.data.datasets[0].data = [score, 100 - score];
        riskChart.update();

        const riskLevel = document.getElementById("riskLevel");
        const riskReason = document.getElementById("riskReason");

        if (riskLevel) riskLevel.innerText = r.category;
        if (riskReason) riskReason.innerText = r.reason;
    }

    /* ---------- Clauses ---------- */
    if (data.clauses && data.clauses.length) {
        document.getElementById("clauseCount").innerText = data.clauses.length;
        const detectedCount = data.clauses.filter(c => c.detected).length;
        
        document.getElementById("clausesList").innerHTML =
            data.clauses.map(c => `
            <div class="clause-card">
                <div class="clause-header">
                    <strong>${c.name}</strong>
                    <span class="${c.detected ? "badge-ok" : "badge-missing"}">
                        ${c.detected ? "✓ Detected" : "✗ Missing"}
                    </span>
                </div>
                <div class="clause-text">
                    ${c.detected ? c.content.substring(0, 150) + "..." : "Clause not mentioned in agreement"}
                </div>
            </div>
            `).join("");
    } else {
        document.getElementById("clausesList").innerHTML =
            "<div class='empty-state'><i class='fas fa-file-alt'></i><p>No clauses detected</p></div>";
    }

    /* ---------- Alerts ---------- */
    if (data.alerts && data.alerts.length) {
        document.getElementById("alertCount").innerText = data.alerts.length;
        
        document.getElementById("alertsList").innerHTML =
            data.alerts.map(a => {
                const date = new Date(a.deadline);
                const now = new Date();
                const daysLeft = Math.ceil((date - now) / (1000 * 60 * 60 * 24));
                
                return `<div>
                    <i class="fas fa-calendar"></i>
                    <strong>${a.type}</strong> - ${date.toLocaleDateString()} 
                    <span style="font-size:11px; color:#f59e0b;">(${daysLeft} days)</span>
                </div>`;
            }).join("");
    } else {
        document.getElementById("alertsList").innerHTML =
            "<div class='empty-state'><i class='fas fa-bell-slash'></i><p>No alerts yet</p></div>";
    }

    /* ---------- Chatbot ---------- */
    const chatInput = document.getElementById("chatInput");
    if (chatInput)
        chatInput.placeholder = "Ask about terms, conditions, deadlines...";
    
    addMessage("📄 Document loaded! Ask me anything about the rental agreement.", "bot");
}

/* ---------- Chatbot ---------- */
document.getElementById("sendBtn").onclick = async () => {
    const input = document.getElementById("chatInput");

    if (!input.value || !currentDocId) {
        if (!currentDocId)
            addMessage("❌ Please upload a document first.", "bot");
        return;
    }

    const query = input.value;
    addMessage(query, "user");
    input.value = "";

    addMessage("⏳ Thinking...", "bot-typing");

    try {
        const res = await fetch(
            API + `/chatbot/${currentDocId}?query=${encodeURIComponent(query)}`,
            { method: "POST" }
        );

        if (!res.ok)
            throw new Error(`Server error: ${res.status}`);

        const data = await res.json();

        const typing = document.querySelector(".bot-typing");
        if (typing) typing.remove();

        addMessage(data.response, "bot");

    } catch (err) {
        const typing = document.querySelector(".bot-typing");
        if (typing) typing.remove();
        addMessage("❌ Error: " + err.message, "bot");
    }
};

function addMessage(text, role) {
    const chat = document.getElementById("chatContainer");
    const msg = document.createElement("div");
    msg.classList.add("msg", role);
    
    if (role === "bot" || role === "bot-typing") {
        msg.innerHTML = `<i class="fas fa-robot"></i><span>${text}</span>`;
    } else {
        msg.innerHTML = `<span>${text}</span>`;
    }
    
    chat.appendChild(msg);
    chat.scrollTop = chat.scrollHeight;
}