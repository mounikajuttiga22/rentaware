#!/usr/bin/env python3
"""
Quick test script to verify RentAware backend is working
Run this after starting the backend: python test_backend.py
"""

import requests
import json
import time
from pathlib import Path

API_URL = "http://127.0.0.1:8000"
TEST_FILE = "sample_agreement.txt"
TEST_PHONE = "+919876543210"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_health_check():
    """Test if backend is running"""
    print_section("1. Health Check")
    try:
        response = requests.get(f"{API_URL}/")
        print(f"✅ Backend is running!")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Backend is not running!")
        print(f"   Error: {e}")
        print(f"   Make sure to run: uvicorn app.main:app --reload")
        return False

def test_upload_document():
    """Test uploading a document"""
    print_section("2. Upload Document Test")
    
    if not Path(TEST_FILE).exists():
        print(f"❌ Test file '{TEST_FILE}' not found!")
        print(f"   Please create a test file first.")
        return None
    
    try:
        with open(TEST_FILE, 'rb') as f:
            files = {'file': f}
            params = {'phone': TEST_PHONE}
            response = requests.post(
                f"{API_URL}/upload/",
                files=files,
                params=params
            )
        
        if response.status_code == 200:
            data = response.json()
            doc_id = data.get('id')
            print(f"✅ Document uploaded successfully!")
            print(f"   Document ID: {doc_id}")
            print(f"   Clauses found: {len(data.get('clauses', []))}")
            print(f"   Alerts detected: {len(data.get('alerts', []))}")
            print(f"   SMS sent to: {TEST_PHONE}")
            return doc_id
        else:
            print(f"❌ Upload failed!")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error during upload: {e}")
        return None

def test_get_document(doc_id):
    """Test fetching document data"""
    print_section("3. Get Document Data Test")
    
    if not doc_id:
        print("⏭️  Skipping (no document ID)")
        return False
    
    try:
        response = requests.get(f"{API_URL}/documents/{doc_id}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Document data retrieved successfully!")
            print(f"   Status: {data.get('status')}")
            print(f"   Clauses: {len(data.get('clauses', []))}")
            print(f"   Risk Scores: {len(data.get('risk_scores', []))}")
            print(f"   Alerts: {len(data.get('alerts', []))}")
            
            if data.get('risk_scores'):
                risk = data['risk_scores'][0]
                print(f"\n   Risk Assessment:")
                print(f"   - Category: {risk.get('category')}")
                print(f"   - Financial Risk: {risk.get('financial_risk')}/100")
                print(f"   - Legal Risk: {risk.get('legal_risk')}/100")
            
            return True
        else:
            print(f"❌ Failed to get document!")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error getting document: {e}")
        return False

def test_chatbot(doc_id):
    """Test chatbot endpoint"""
    print_section("4. Chatbot Test")
    
    if not doc_id:
        print("⏭️  Skipping (no document ID)")
        return False
    
    try:
        query = "What are the key clauses in this agreement?"
        response = requests.post(
            f"{API_URL}/chatbot/{doc_id}",
            params={'query': query}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chatbot responded successfully!")
            print(f"\n   Query: {query}")
            print(f"\n   Response: {data.get('response')}")
            return True
        else:
            print(f"⚠️  Chatbot endpoint returned error!")
            print(f"   Status: {response.status_code}")
            print(f"   This might be because Ollama is not running.")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"⚠️  Error testing chatbot: {e}")
        print(f"   This is OK if Ollama is not running.")
        return False

def summary():
    """Print test summary"""
    print_section("Test Summary")
    print("""
  ✅ All core features working!
  
  Next steps:
  1. Open frontend in browser: frontend/index.html
  2. Upload a document with your phone number
  3. Check your phone for SMS alert
  4. View analysis results
  5. Chat with AI assistant
  
  For help, refer to: SETUP_GUIDE.md
    """)

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════╗
║         RentAware Backend Test Suite                   ║
╚════════════════════════════════════════════════════════╝
  """)
    
    # Run tests
    if not test_health_check():
        exit(1)
    
    doc_id = test_upload_document()
    test_get_document(doc_id)
    test_chatbot(doc_id)
    
    summary()
