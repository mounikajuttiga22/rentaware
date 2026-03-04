import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the backend app to the path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services import extraction, scoring, chatbot

async def run_tests():
    load_dotenv(dotenv_path='backend/.env')
    print("--- Testing RentAware Intelligence ---")
    
    # 1. Test Extraction
    print("\n[1] Testing Extraction...")
    sample_text = """
    SECURITY DEPOSIT: The Tenant shall pay a security deposit of 50,000 INR (equivalent to 2 months rent).
    NOTICE PERIOD: Either party may terminate this agreement by giving 1 month written notice.
    LATE FEE: A penalty of 500 INR shall be charged for every day of delay in rent payment.
    """
    # Create a dummy file for testing
    with open('test_agreement.txt', 'w') as f:
        f.write(sample_text)
    
    result = extraction.extract_and_detect('test_agreement.txt')
    print(f"Detected Clauses: {list(result['clauses'].keys())}")
    for k, v in result['clauses'].items():
        if v:
            print(f" - {k}: {v[:50]}...")
        else:
            print(f" - {k}: Not Detected")

    # 2. Test Scoring
    print("\n[2] Testing Scoring...")
    risk_info = scoring.calculate_risk(result['clauses'])
    print(f"Risk Score: {risk_info.get('financial_risk')} (Financial), {risk_info.get('legal_risk')} (Legal)")
    print(f"Category: {risk_info.get('category')}")
    print(f"Reason: {risk_info.get('reason')}")

    # 3. Test Chatbot
    print("\n[3] Testing Chatbot...")
    context = "\n".join([f"{k}: {v}" for k, v in result['clauses'].items()])
    query = "What is the penalty for late rent?"
    response = await chatbot.get_response(query, context)
    print(f"Query: {query}")
    print(f"Response: {response}")

    # Cleanup
    if os.path.exists('test_agreement.txt'):
        os.remove('test_agreement.txt')

if __name__ == "__main__":
    asyncio.run(run_tests())
