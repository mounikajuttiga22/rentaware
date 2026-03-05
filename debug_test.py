import requests
import json

API_URL = "http://127.0.0.1:8000"
TEST_FILE = "./sample_agreement.txt"

try:
    with open(TEST_FILE, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{API_URL}/upload/", files=files, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")
        try:
            print(f"Response JSON: {json.dumps(response.json(), indent=2)}")
        except:
            print("Could not parse as JSON")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
