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
    if file_path.endswith('.pdf'):
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += (page.extract_text() or "") + "\n"
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

    # 🔥 1. Ollama AI Extraction
    # try:
    #     prompt = f"""
    #     You are a legal rental agreement analyzer.

    #     Extract these clauses clearly:
    #     - Security Deposit
    #     - Notice Period
    #     - Lock-in Period
    #     - Late Fee
    #     - Maintenance
    #     - Renewal

    #     Return strictly in this format:

    #     Security Deposit: ...
    #     Notice Period: ...
    #     Lock-in Period: ...
    #     Late Fee: ...
    #     Maintenance: ...
    #     Renewal: ...

    #     Agreement Text:
    #     {text[:4000]}
    #     """

    #     response = requests.post(
    #         OLLAMA_URL,
    #         json={
    #             "model": MODEL_NAME,
    #             "prompt": prompt,
    #             "stream": False
    #         }
    #     )

    #     result = response.json()
    #     ai_text = result.get("response", "")
    #     ai_clauses = parse_ai_response(ai_text)

    #     if ai_clauses:
    #         return {"text": text, "clauses": ai_clauses}

    # except Exception as e:
    #     print(f"Ollama Error: {e}")
    # Ollama disabled for deployment
    print("Ollama disabled — using regex extraction")

    # 🔁 2. Regex fallback
    clauses = {
        "Security Deposit": extract_clause_regex(text, [r"security deposit", r"deposit amount"]),
        "Notice Period": extract_clause_regex(text, [r"notice period", r"termination notice"]),
        "Lock-in Period": extract_clause_regex(text, [r"lock-in period", r"minimum stay"]),
        "Late Fee": extract_clause_regex(text, [r"late fee", r"penalty for delay"]),
        "Maintenance": extract_clause_regex(text, [r"maintenance charges", r"upkeep"]),
        "Renewal": extract_clause_regex(text, [r"renewal", r"extension"])
    }

    return {"text": text, "clauses": clauses}


def parse_ai_response(response_text: str) -> Dict[str, str]:
    clauses = {}
    lines = response_text.strip().split('\n')

    for line in lines:
        if ':' in line:
            name, content = line.split(':', 1)
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
        if name == "Notice Period":
            match = re.search(r"(\d+)\s+(month|day|week)", content, re.IGNORECASE)
            if match:
                deadline = datetime.datetime.now() + datetime.timedelta(days=330)
                alerts.append({
                    "type": "Notice Period",
                    "deadline": deadline
                })

    return alerts