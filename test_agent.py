import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

def test_agent_endpoint():
    url = "http://localhost:8500/api/v1/agent/run"
    payload = {
        "task": "test_task",
        "parameters": {
            "test_param": "test_value"
        }
    }

    try:
        print("Sending request to agent endpoint...")
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        try:
            response_data = response.json()
            print("Response:")
            print(json.dumps(response_data, indent=2))
            
            # Verify mock response structure
            if os.getenv("ENVIRONMENT") == "test":
                assert response_data.get("status") == "success"
                assert "This is a mock response" in str(response_data)
                print("\n✅ Mock response verified successfully!")
                
        except ValueError:
            print("Response (raw):")
            print(response.text)
            
        return response.status_code, response_data if 'response_data' in locals() else None
        
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None, str(e)

if __name__ == "__main__":
    # Set environment to test if not already set
    if not os.getenv("ENVIRONMENT"):
        os.environ["ENVIRONMENT"] = "test"
        
    status_code, response = test_agent_endpoint()
    if status_code == 200:
        print("\n✅ Success! The agent endpoint is working with mock responses.")
    else:
        print("\n❌ Something went wrong. Check the error message above.")