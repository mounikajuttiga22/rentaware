import requests
import json
import time

API_URL = "http://127.0.0.1:8000"
TEST_FILE = "./sample_agreement.txt"

print("=" * 60)
print("Testing Full Upload and Retrieval Workflow")
print("=" * 60)

try:
    # Step 1: Upload file
    print("\n1. Uploading file...")
    with open(TEST_FILE, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{API_URL}/upload/", files=files, timeout=10)
    
    print(f"   Upload Status: {response.status_code}")
    data = response.json()
    doc_id = data['id']
    print(f"   Document ID: {doc_id}")
    print(f"   Initial Status: {data['status']}")
    
    # Step 2: Poll for completion
    print("\n2. Waiting for processing...")
    for i in range(30):
        time.sleep(1)
        response = requests.get(f"{API_URL}/documents/{doc_id}")
        
        if response.status_code != 200:
            print(f"   Error retrieving document: {response.status_code}")
            print(f"   Response: {response.text}")
            break
        
        doc = response.json()
        status = doc['status']
        print(f"   [{i+1}] Status: {status}")
        
        if status == "completed":
            print("\n3. Document Processing Completed!")
            print(f"\n   Clauses Found: {len(doc['clauses'])}")
            for clause in doc['clauses']:
                if clause['detected']:
                    print(f"     ✓ {clause['name']}")
            
            if doc['risk_scores']:
                risk = doc['risk_scores'][0]
                print(f"\n   Risk Score:")
                print(f"     - Category: {risk['category']}")
                print(f"     - Financial Risk: {risk['financial_risk']}")
                print(f"     - Legal Risk: {risk['legal_risk']}")
                print(f"     - Reason: {risk['reason']}")
            
            print(f"\n   Alerts: {len(doc['alerts'])}")
            
            print("\n✓ WORKFLOW COMPLETE!")
            break
        elif status == "error":
            print("   Document processing failed!")
            break

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
