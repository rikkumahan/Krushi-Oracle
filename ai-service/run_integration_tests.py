
import requests
import json
import time
import os
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

# Colors for output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(title):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}\n")

def print_result(label, success, elapsed=None):
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if success else f"{Colors.RED}✗ FAIL{Colors.END}"
    time_str = f" ({elapsed:.0f}ms)" if elapsed is not None else ""
    print(f"{status} {Colors.BOLD}{label}{Colors.END}{time_str}")

def test_health():
    print_header("TEST 1: Health Check")
    start = time.time()
    try:
        response = requests.get(f"{BASE_URL}/health")
        elapsed = (time.time() - start) * 1000
        success = response.status_code == 200
        print_result("Root Health", success, elapsed)
        
        response = requests.get(f"{BASE_URL}/api/v2/health")
        success = response.status_code == 200
        print_result("Scoring V2 Health", success)
    except Exception as e:
        print_result(f"Health Check Exception: {e}", False)

def test_scoring_v2():
    print_header("TEST 2: Deterministic Scoring (V2)")
    with open('test_integration_payload.json', 'r') as f:
        payload = json.load(f)
    
    start = time.time()
    try:
        response = requests.post(f"{BASE_URL}/api/v2/score-idea", json=payload)
        elapsed = (time.time() - start) * 1000
        if response.status_code == 200:
            result = response.json()
            print_result(f"Scoring Complete: {result.get('idea_name', payload['idea_name'])}", True, elapsed)
            print(f"  MVS Score: {Colors.CYAN}{result['mvs_score']}/100{Colors.END} (Grade: {result['mvs_grade']})")
            print(f"  Verdict: {result['validation_class']}")
            return True
        else:
            print_result(f"Scoring Failed ({response.status_code})", False)
            print(f"  Error: {response.text}")
            return False
    except Exception as e:
        print_result(f"Scoring Exception: {e}", False)
        return False

def test_strategic_audit():
    print_header("TEST 3: Strategic Audit Agent")
    # Must match test_integration_payload.json idea_name
    payload = {
        "idea_name": "AI-Powered Smart Home Energy Optimization", 
        "question": "Give me a high-level VC perspective on this idea."
    }
    start = time.time()
    try:
        response = requests.post(f"{BASE_URL}/api/v2/explain-score", json=payload)
        elapsed = (time.time() - start) * 1000
        if response.status_code == 200:
            print_result("Audit Q&A Successful", True, elapsed)
            print(f"  Agent Snippet: {response.json()['answer'][:150]}...")
        else:
            print_result(f"Audit Failed ({response.status_code})", False)
            print(f"  Detail: {response.text}")
    except Exception as e:
        print_result(f"Audit Exception: {e}", False)

def test_universal_validation():
    print_header("TEST 4: Universal Validation")
    payload = {
        "idea_name": "Drone Crop Monitor",
        "idea_description": "Using drones to monitor crop health with multispectral imaging.",
        "keywords": ["precision agriculture", "drone farming"],
        "sector": "agriculture"
    }
    start = time.time()
    try:
        response = requests.post(f"{BASE_URL}/api/v2/validation/validate", json=payload)
        elapsed = (time.time() - start) * 1000
        if response.status_code == 200:
            result = response.json()
            print_result("Validation Complete", True, elapsed)
            print(f"  Confidence: {result['overall_confidence']}/100")
            print(f"  Verdict: {result['verdict']}")
        else:
            print_result(f"Validation Failed ({response.status_code})", False)
            print(f"  Error: {response.text}")
    except Exception as e:
        print_result(f"Validation Exception: {e}", False)

def test_comparison():
    print_header("TEST 5: Smart Comparison Search")
    payload = {
        "idea_name": "AI Crypto Wallet", 
        "idea_description": "Wallet that predicts price movements",
        "target_market": "Crypto traders"
    }
    start = time.time()
    try:
        response = requests.post(f"{BASE_URL}/api/v2/comparison/find-similar", json=payload)
        elapsed = (time.time() - start) * 1000
        if response.status_code == 200:
            print_result("Comparison Search Complete", True, elapsed)
        elif response.status_code == 403:
            print_result("Comparison (Forbidden - Missing Token)", True)
        else:
            print_result(f"Comparison Failed ({response.status_code})", False)
            print(f"  Error: {response.text}")
    except Exception as e:
        print_result(f"Comparison Exception: {e}", False)

def test_assets():
    print_header("TEST 6: Asset Generation")
    idea = {
        "id": "test-id", 
        "name": "Test Startup", 
        "tagline": "Just testing tagging",
        "description": "A startup for testing purposes and documentation.", 
        "target_customer": "Testers",
        "problem_solved": "Lack of tests in modern engineering.", 
        "mvp_features": [],
        "business_model": {
            "revenue_streams": ["Subscription"], 
            "key_partners": [], 
            "cost_structure": [], 
            "value_proposition": "test", 
            "customer_segments": ["Devs"], 
            "channels": []
        },
        "moonshot_channel": "Viral", 
        "estimated_initial_cost": 1000
    }
    
    # Check Lean Canvas
    start = time.time()
    response = requests.post(f"{BASE_URL}/api/v2/assets/lean-canvas", json=idea)
    print_result("Asset: lean-canvas", response.status_code == 200, (time.time() - start) * 1000)
    
    # Check Pitch Deck
    start = time.time()
    response = requests.post(f"{BASE_URL}/api/v2/assets/pitch-deck", json=idea)
    print_result("Asset: pitch-deck", response.status_code == 200, (time.time() - start) * 1000)

    # Check Landing Page
    start = time.time()
    lp_payload = {
        "idea_name": "Test Startup",
        "tagline": "The best testing tool",
        "description": "Building a tool for the future of QA.",
        "target_audience": "QA Engineers",
        "features": ["Automated reports"]
    }
    response = requests.post(f"{BASE_URL}/api/v2/assets/landing-page", json=lp_payload)
    print_result("Asset: landing-page", response.status_code == 200, (time.time() - start) * 1000)

if __name__ == "__main__":
    print_header("NOVA AI SERVICE V2 INTEGRATION SUITE")
    print(f"Testing against base URL: {BASE_URL}")
    print(f"Start Time: {datetime.now().strftime('%H:%M:%S')}")
    
    test_health()
    scored = test_scoring_v2()
    if scored:
        test_strategic_audit()
    else:
        print_result("Skipping Strategic Audit (No context)", False)
        
    test_universal_validation()
    test_comparison()
    test_assets()
    
    print_header("ALL TESTS COMPLETE")
