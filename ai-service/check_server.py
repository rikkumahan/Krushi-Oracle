"""
Quick Server Diagnostic & Restart Guide

ISSUE: Server not responding after router changes
CAUSE: Uvicorn auto-reload sometimes fails on __init__.py changes
"""

print("=" * 80)
print("SERVER DIAGNOSTIC".center(80))
print("=" * 80)

import requests
import sys

def test_endpoint(url, name):
    """Test if an endpoint is accessible"""
    try:
        response = requests.get(url, timeout=2)
        print(f"✅ {name}: OK (Status: {response.status_code})")
        return True
    except requests.exceptions.ConnectionError:
        print(f"❌ {name}: CONNECTION REFUSED - Server not running")
        return False
    except Exception as e:
        print(f"❌ {name}: ERROR - {e}")
        return False

# Test endpoints
base_url = "http://localhost:8000"
endpoints = [
    (f"{base_url}/", "Root endpoint"),
    (f"{base_url}/health", "Health check"),
    (f"{base_url}/api/v2/health", "V2 Health check"),
]

print("\nTesting endpoints:")
print("-" * 80)

all_ok = True
for url, name in endpoints:
    if not test_endpoint(url, name):
        all_ok = False

print("-" * 80)

if not all_ok:
    print("\n🔧 SOLUTION:")
    print("=" * 80)
    print("""
The server needs to be restarted. Here's what to do:

STEP 1: Stop the current server
    - Find the terminal running: python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
    - Press: Ctrl + C
    
STEP 2: Restart the server
    - Run: python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
    - Wait for: "Application startup complete"
    
STEP 3: Run integration tests
    - Run: python run_integration_tests.py
    
ALTERNATIVELY (Quick Fix):
    cd ai-service
    python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
    
Then in another terminal:
    python run_integration_tests.py
""")
else:
    print("\n✅ Server is running correctly!")
    print("\nNext step: Run integration tests")
    print("    python run_integration_tests.py")

print("=" * 80)
