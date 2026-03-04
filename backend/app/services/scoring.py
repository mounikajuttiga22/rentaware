from typing import Dict

def calculate_risk(clauses: Dict[str, str]):
    financial_risk = 0
    legal_risk = 0
    reason = []

    # Security Deposit check
    deposit_text = clauses.get("Security Deposit", "")
    if "11 months" in deposit_text.lower():
        financial_risk += 40
        reason.append("Security deposit is unusually high.")

    # Notice Period check
    notice_text = clauses.get("Notice Period", "")
    if "1 month" in notice_text.lower():
        legal_risk += 10

    # Late Fee check
    late_fee_text = clauses.get("Late Fee", "")
    if "penalty" in late_fee_text.lower():
        financial_risk += 15

    total_risk = financial_risk + legal_risk

    if total_risk > 60:
        category = "High"
    elif total_risk > 30:
        category = "Medium"
    else:
        category = "Low"

    return {
        "financial_risk": financial_risk,
        "legal_risk": legal_risk,
        "category": category,
        "reason": ", ".join(reason) if reason else "No major risks detected."
    }