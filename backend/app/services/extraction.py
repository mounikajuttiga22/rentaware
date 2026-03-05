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
    clauses = {
        "Security Deposit": extract_clause_regex(text, [r"security deposit", r"deposit amount"]),
        "Notice Period": extract_clause_regex(text, [r"notice period", r"termination notice"]),
        "Lock-in Period": extract_clause_regex(text, [r"lock-in period", r"minimum stay"]),
        "Late Fee": extract_clause_regex(text, [r"late fee", r"penalty for delay"]),
        "Maintenance": extract_clause_regex(text, [r"maintenance charges", r"upkeep"]),
        "Renewal": extract_clause_regex(text, [r"renewal", r"extension"])
    }

    # Detect alerts
    alerts = extract_alerts(clauses)

    return {
        "text": text,
        "clauses": clauses,
        "alerts": alerts
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

        if name == "Notice Period":

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
                    "deadline": deadline
                })

    return alerts