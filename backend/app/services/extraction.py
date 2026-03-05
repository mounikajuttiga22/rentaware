import datetime
import os
import re
import shutil
from typing import Any, Dict, List

import pdfplumber

try:
    import pytesseract
except ImportError:
    pytesseract = None

try:
    from pdf2image import convert_from_path
except ImportError:
    convert_from_path = None

try:
    import pypdfium2 as pdfium
except ImportError:
    pdfium = None


def _configure_ocr() -> tuple[bool, str]:
    """Configure OCR binaries from environment and system PATH."""
    if pytesseract is None:
        return False, "OCR dependency missing (install pytesseract, pillow)"

    tesseract_from_env = os.getenv("TESSERACT_CMD", "").strip()
    tesseract_from_path = shutil.which("tesseract")
    windows_default = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    tesseract_cmd = tesseract_from_env or tesseract_from_path

    if not tesseract_cmd and os.path.exists(windows_default):
        tesseract_cmd = windows_default

    if not tesseract_cmd:
        return False, "Tesseract binary not found. Set TESSERACT_CMD or add tesseract to PATH"

    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    return True, "OCR configured"


OCR_READY, OCR_STATUS = _configure_ocr()
POPPLER_PATH = os.getenv("POPPLER_PATH", "").strip() or None


def _convert_pdf_pages_to_images(pdf_path: str):
    """Convert PDF pages to PIL images using Poppler or pypdfium2."""
    if convert_from_path is not None:
        try:
            kwargs = {"poppler_path": POPPLER_PATH} if POPPLER_PATH else {}
            return convert_from_path(pdf_path, **kwargs)
        except Exception as exc:
            print(f"pdf2image conversion failed: {exc}")

    if pdfium is None:
        print("No PDF rasterizer available. Install poppler or pypdfium2")
        return []

    try:
        doc = pdfium.PdfDocument(pdf_path)
        images = []
        for idx in range(len(doc)):
            page = doc[idx]
            pil_image = page.render(scale=2.0).to_pil()
            images.append(pil_image)
            page.close()
        doc.close()
        return images
    except Exception as exc:
        print(f"pypdfium2 conversion failed: {exc}")
        return []


# -------- OCR extraction --------
def ocr_extract(pdf_path):
    if not OCR_READY:
        print(f"OCR unavailable: {OCR_STATUS}")
        return ""

    print("Running OCR extraction...")

    images = _convert_pdf_pages_to_images(pdf_path)
    if not images:
        print("OCR image conversion failed")
        return ""

    text = ""
    for img in images:
        try:
            page_text = pytesseract.image_to_string(img)
            text += page_text + "\n"
        except Exception as exc:
            print(f"OCR page extraction failed: {exc}")

    return text


# -------- Main extraction --------
def extract_and_detect(file_path: str) -> Dict[str, Any]:

    text = ""

    # Support PDF and TXT
    if file_path.endswith(".pdf"):

        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text() or ""
                    text += extracted + "\n"
        except:
            text = ""

        # If no text detected, try OCR fallback
        if len(text.strip()) < 50:
            print("No text detected, using OCR fallback")
            text = ocr_extract(file_path)

    else:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

    print("Ollama disabled — using regex extraction")

    # Clause patterns
    clause_patterns = {
        "Security Deposit": [r"security deposit", r"deposit amount"],
        "Notice Period": [r"notice period", r"termination notice"],
        "Lock-in Period": [r"lock[- ]?in period", r"minimum stay"],
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

    # Alerts
    alerts = extract_alerts(clause_content_map)

    # Risk scores
    risk_scores = calculate_risk_scores(clause_content_map, text)

    return {
        "text": text,
        "clauses": clauses_list,
        "alerts": alerts,
        "risk_scores": risk_scores
    }


# -------- Regex clause detection --------
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


# -------- Alert detection --------
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


# -------- Risk scoring --------
def calculate_risk_scores(clauses: Dict[str, str], text: str) -> List[Dict[str, Any]]:

    financial_risk = 0
    legal_risk = 0
    reasons = []

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