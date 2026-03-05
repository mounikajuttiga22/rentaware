import requests
import json

API_URL = "http://127.0.0.1:8000"
TEST_FILE = "./sample_agreement.txt"

print("Testing upload endpoint...")
try:
    with open(TEST_FILE, 'rb') as f:
        files = {'file': f}
        print("Sending POST request...")
        response = requests.post(f"{API_URL}/upload/", files=files, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, default=str)}")
except requests.exceptions.Timeout:
    print("ERROR: Request timed out!")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
