"""
Test script for Gemini API integration
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_generate_config():
    """Test the generate-config endpoint"""
    url = f"{BASE_URL}/api/generate-config"
    payload = {
        "prompt": "Create a simple line chart showing temperature over time with a dark theme"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS: Generate Config API working!")
            print("Generated config:")
            print(json.dumps(result.get("config"), indent=2))
        else:
            print(f"ERROR: API returned status {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to server. Make sure the backend is running on port 8000")
    except Exception as e:
        print(f"ERROR: {e}")

def test_improve_config():
    """Test the improve-config endpoint"""
    url = f"{BASE_URL}/api/improve-config"
    
    current_config = {
        "app_title": "Test App",
        "theme": "light",
        "figures": [{
            "id": "fig1",
            "x_label": "Time",
            "y_label": "Value",
            "items": []
        }]
    }
    
    payload = {
        "current_config": current_config,
        "improvement_request": "Change to dark theme and add a scatter plot"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            result = response.json()
            print("\nSUCCESS: Improve Config API working!")
            print("Improved config:")
            print(json.dumps(result.get("config"), indent=2))
        else:
            print(f"\nERROR: API returned status {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("\nERROR: Could not connect to server. Make sure the backend is running on port 8000")
    except Exception as e:
        print(f"\nERROR: {e}")

if __name__ == "__main__":
    print("Testing Gemini API Integration...")
    print("=" * 50)
    test_generate_config()
    test_improve_config()