import urllib.request
import json
import traceback

def check_health():
    url = "http://127.0.0.1:8000/health"
    try:
        with urllib.request.urlopen(url) as response:
            status_code = response.getcode()
            data = response.read().decode('utf-8')
            print(f"Status Code: {status_code}")
            print(f"Response: {data}")
            if status_code == 200:
                print("HEALTH CHECK PASSED")
            else:
                print("HEALTH CHECK FAILED")
    except Exception as e:
        print(f"Error accessing {url}: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    check_health()
