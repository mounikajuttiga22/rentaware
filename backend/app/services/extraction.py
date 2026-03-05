import pdfplumber
import re
from typing import Dict, List, Any
import datetime
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"


def extract_and_detect(file_path: str) -> Dict[str, Any]:
    text = ""

    # Support PDF and TXT
    if file_path.endswith(".pdf"):
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += (page.extract_text() or "") + "\n"
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

    # Ollama disabled for deployment
    print("Ollama disabled — using regex extraction")

    # Regex clause extraction
    clause_patterns = {
        "Security Deposit": [r"security deposit", r"deposit amount"],
        "Notice Period": [r"notice period", r"termination notice"],
        "Lock-in Period": [r"lock-in period", r"minimum stay"],
        "Late Fee": [r"late fee", r"penalty for delay"],
        "Maintenance": [r"maintenance charges", r"upkeep"],
        "Renewal": [r"renewal", r"extension"]
    }
    
    clauses_list = []
    clause_content_map = {}
    
    for clause_name, keywords in clause_patterns.items():
        content = extract_clause_regex(text, keywords)
        clause_content_map[clause_name] = content
        clauses_list.append({
            "name": clause_name,
            "content": content,
            "detected": bool(content)
        })

    # Detect alerts
    alerts = extract_alerts(clause_content_map)

    # Calculate risk scores
    risk_scores = calculate_risk_scores(clause_content_map, text)

    return {
        "text": text,
        "clauses": clauses_list,
        "alerts": alerts,
        "risk_scores": risk_scores
    }


def parse_ai_response(response_text: str) -> Dict[str, str]:
    clauses = {}
    lines = response_text.strip().split("\n")

    for line in lines:
        if ":" in line:
            name, content = line.split(":", 1)
            clauses[name.strip()] = content.strip()

    return clauses


def extract_clause_regex(text: str, keywords: List[str]) -> str:
    for keyword in keywords:

        match = re.search(
            rf"{keyword}.*?(\.|\n\n)",
            text,
            re.IGNORECASE | re.DOTALL
        )

        if match:
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 150)

            return text[start:end].strip()

    return ""


def extract_alerts(clauses: Dict[str, str]) -> List[Dict[str, Any]]:

    alerts = []

    for name, content in clauses.items():

        if name == "Notice Period" and content:

            match = re.search(r"(\d+)\s+(month|day|week)", content, re.IGNORECASE)

            if match:

                value = int(match.group(1))
                unit = match.group(2).lower()

                today = datetime.datetime.now()

                if "day" in unit:
                    deadline = today + datetime.timedelta(days=value)

                elif "week" in unit:
                    deadline = today + datetime.timedelta(weeks=value)

                elif "month" in unit:
                    deadline = today + datetime.timedelta(days=value * 30)

                alerts.append({
                    "type": "Notice Period",
                    "deadline": deadline.isoformat()
                })
        
        if name == "Renewal" and content:
            today = datetime.datetime.now()
            deadline = today + datetime.timedelta(days=365)
            alerts.append({
                "type": "Renewal",
                "deadline": deadline.isoformat()
            })

    return alerts


def calculate_risk_scores(clauses: Dict[str, str], text: str) -> List[Dict[str, Any]]:
    """Calculate financial and legal risk scores based on clauses"""
    
    financial_risk = 0
    legal_risk = 0
    reasons = []
    
    # Check for concerning keywords
    if "late fee" in text.lower() and clauses.get("Late Fee"):
        financial_risk += 20
        reasons.append("Late fees clause detected")
    
    if "penalty" in text.lower():
        financial_risk += 15
        reasons.append("Penalty clauses found")
    
    if "lock-in" in text.lower() and clauses.get("Lock-in Period"):
        legal_risk += 25
        reasons.append("Lock-in period restricts flexibility")
    
    if "maintenance" in text.lower() and clauses.get("Maintenance"):
        financial_risk += 20
        reasons.append("Additional maintenance charges")
    
    if "security deposit" not in text.lower():
        legal_risk += 15
        reasons.append("Security deposit clause missing")
    
    if "notice" not in text.lower():
        legal_risk += 20
        reasons.append("Notice period not specified")
    
    financial_risk = min(100, financial_risk)
    legal_risk = min(100, legal_risk)
    avg_risk = (financial_risk + legal_risk) // 2
    
    if avg_risk >= 60:
        category = "High"
    elif avg_risk >= 35:
        category = "Medium"
    else:
        category = "Low"
    
    return [{
        "financial_risk": financial_risk,
        "legal_risk": legal_risk,
        "category": category,
        "reason": "; ".join(reasons) if reasons else "No significant risks detected"
    }]