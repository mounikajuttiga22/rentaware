const API = "http://127.0.0.1:8000";


let currentDocId = null;

const uploadBtn = document.getElementById("uploadBtn");
const fileInput = document.getElementById("fileInput");

const ctx = document.getElementById("riskChart").getContext("2d");

const riskChart = new Chart(ctx, {
    type: "doughnut",
    data: {
        datasets: [{
            data: [0, 100],
            backgroundColor: ["#22c55e", "#e5e7eb"]
        }]
    },
    options: {
        cutout: "75%",
        plugins: { legend: { display: false } }
    }
});

uploadBtn.onclick = () => fileInput.click();

fileInput.onchange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    uploadBtn.innerText = "Uploading...";
    uploadBtn.disabled = true;

    document.getElementById("clausesList").innerHTML =
        "<div>Processing document...</div>";

    try {

        const formData = new FormData();
        formData.append("file", file);

        const res = await fetch(API + "/upload/", {
            method: "POST",
            body: formData
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || `Server error: ${res.status}`);
        }

        const data = await res.json();
        currentDocId = data.id;

        const result = await fetch(API + "/documents/" + currentDocId);
        const finalData = await result.json();

        updateUI(finalData);

    } catch (err) {

        console.error("Upload failed:", err);

        document.getElementById("clausesList").innerHTML =
            `<div style="color:red;">Upload failed: ${err.message}</div>`;

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

        let color = "#22c55e";

        if (score > 60) color = "#ef4444";
        else if (score > 30) color = "#f59e0b";

        riskChart.data.datasets[0].backgroundColor = [color, "#e5e7eb"];
        riskChart.data.datasets[0].data = [score, 100 - score];
        riskChart.update();

        const riskLevel = document.getElementById("riskLevel");
        const riskReason = document.getElementById("riskReason");

        if (riskLevel) riskLevel.innerText = r.category;
        if (riskReason) riskReason.innerText = r.reason;
    }


    /* ---------- Clauses (UPDATED) ---------- */

    if (data.clauses && data.clauses.length) {

        document.getElementById("clausesList").innerHTML =
            data.clauses.map(c => `

        <div class="clause-card">

            <div class="clause-header">
                <strong>${c.name}</strong>

                <span class="${c.detected ? "badge-ok" : "badge-missing"}">
                    ${c.detected ? "Detected" : "Missing"}
                </span>
            </div>

            <div class="clause-text">
                ${c.detected ? c.content : "Clause not mentioned in agreement"}
            </div>

        </div>

        `).join("");

    } else {

        document.getElementById("clausesList").innerHTML =
            "<div>No clauses detected.</div>";
    }


    /* ---------- Alerts ---------- */

    if (data.alerts && data.alerts.length) {

        document.getElementById("alertsList").innerHTML =
            data.alerts.map(a =>
                `<div>${a.type} - ${new Date(a.deadline).toLocaleDateString()}</div>`
            ).join("");

    } else {

        document.getElementById("alertsList").innerHTML =
            "<div>No alerts.</div>";
    }


    /* ---------- Chatbot ---------- */

    const chatInput = document.getElementById("chatInput");
    if (chatInput)
        chatInput.placeholder = "Ask about your agreement...";
}


/* ---------- Chatbot ---------- */

document.getElementById("sendBtn").onclick = async () => {

    const input = document.getElementById("chatInput");

    if (!input.value || !currentDocId) {

        if (!currentDocId)
            addMessage("Please upload a document first.", "bot");

        return;
    }

    const query = input.value;

    addMessage(query, "user");
    input.value = "";

    addMessage("Thinking...", "bot-typing");

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

        addMessage("Error: " + err.message, "bot");
    }
};


function addMessage(text, type) {

    const div = document.createElement("div");

    div.className = `msg ${type}`;
    div.innerText = text;

    document.getElementById("chatContainer").appendChild(div);

    div.scrollIntoView({ behavior: "smooth" });
}