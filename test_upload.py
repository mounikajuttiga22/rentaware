#!/usr/bin/env python3
import requests
import json
import sys

# Test configuration
API_URL = "http://127.0.0.1:8000"
TEST_FILE = "./sample_agreement.txt"

def test_upload():
    """Test file upload endpoint"""
    print("=" * 60)
    print("Testing RentAware File Upload")
    print("=" * 60)
    
    try:
        with open(TEST_FILE, 'rb') as f:
            files = {'file': f}
            print(f"\n1. Uploading file: {TEST_FILE}")
            
            response = requests.post(f"{API_URL}/upload/", files=files)
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"   Error: {response.text}")
                return False
            
            upload_response = response.json()
            print(f"   Response: {json.dumps(upload_response, indent=2, default=str)}")
            
            doc_id = upload_response.get('id')
            print(f"\n2. Document created with ID: {doc_id}")
            print(f"   Status: {upload_response.get('status')}")
            print(f"   Filename: {upload_response.get('filename')}")
            
            # Test GET endpoint
            print(f"\n3. Fetching document details...")
            get_response = requests.get(f"{API_URL}/documents/{doc_id}")
            
            print(f"   Status Code: {get_response.status_code}")
            
            if get_response.status_code != 200:
                print(f"   Error: {get_response.text}")
                return False
            
            doc_data = get_response.json()
            print(f"\n   Document Status: {doc_data.get('status')}")
            print(f"   Clauses Found: {len(doc_data.get('clauses', []))}")
            print(f"   Risk Scores: {len(doc_data.get('risk_scores', []))}")
            print(f"   Alerts: {len(doc_data.get('alerts', []))}")
            
            if doc_data.get('status') == 'completed':
                print("\n✓ Upload and processing completed successfully!")
                
                # Print clauses
                if doc_data.get('clauses'):
                    print("\n   Clauses:")
                    for clause in doc_data['clauses']:
                        print(f"     - {clause.get('name')}: {clause.get('detected')}")
                
                # Print risk score
                if doc_data.get('risk_scores'):
                    risk = doc_data['risk_scores'][0]
                    print(f"\n   Risk Score:")
                    print(f"     - Financial Risk: {risk.get('financial_risk')}")
                    print(f"     - Legal Risk: {risk.get('legal_risk')}")
                    print(f"     - Category: {risk.get('category')}")
                    print(f"     - Reason: {risk.get('reason')}")
                
                return True
            else:
                print(f"\n⚠ Document processing still in progress or failed")
                print(f"  Current status: {doc_data.get('status')}")
                return False
                
    except FileNotFoundError:
        print(f"Error: Test file not found: {TEST_FILE}")
        return False
    except requests.exceptions.ConnectionError:
        print(f"Error: Cannot connect to API at {API_URL}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_upload()
    sys.exit(0 if success else 1)
