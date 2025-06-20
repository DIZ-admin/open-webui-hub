#!/usr/bin/env python3
"""
Basic Hub Service Test Script
Quick validation of Hub service functionality
"""

import requests
import json
import time
import sys
import os

# Configuration
HUB_API_URL = os.getenv('HUB_API_URL', 'http://localhost:5003')
TIMEOUT = 10

def test_endpoint(endpoint: str, expected_status: int = 200, description: str = ""):
    """Test a single endpoint"""
    url = f"{HUB_API_URL}{endpoint}"
    try:
        print(f"🔍 Testing {endpoint} - {description}")
        start_time = time.time()
        
        response = requests.get(url, timeout=TIMEOUT)
        response_time = time.time() - start_time
        
        if response.status_code == expected_status:
            print(f"  ✅ Status: {response.status_code} ({response_time:.3f}s)")
            
            # Try to parse JSON if it's an API endpoint
            if endpoint.startswith('/api/'):
                try:
                    data = response.json()
                    print(f"  📊 Response keys: {list(data.keys())}")
                    return True, data
                except json.JSONDecodeError:
                    print(f"  ⚠️ Non-JSON response")
                    return True, None
            else:
                print(f"  📄 Content-Type: {response.headers.get('content-type', 'unknown')}")
                return True, None
        else:
            print(f"  ❌ Status: {response.status_code} (expected {expected_status})")
            return False, None
            
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Request failed: {e}")
        return False, None

def main():
    """Run basic Hub service tests"""
    print("🚀 Hub Service Basic Test")
    print(f"Target: {HUB_API_URL}")
    print("=" * 50)
    
    tests = [
        ("/api/health", 200, "Health check"),
        ("/api/services", 200, "Services list"),
        ("/api/architecture", 200, "Architecture data"),
        ("/api/metrics", 200, "System metrics"),
        ("/api/layers", 200, "Architecture layers"),
        ("/api/cache/info", 200, "Cache information"),
        ("/api/discovery", None, "Service discovery (may be disabled)"),
        ("/", 200, "Frontend serving"),
    ]
    
    passed = 0
    failed = 0
    
    for endpoint, expected_status, description in tests:
        if expected_status is None:
            # Special case for endpoints that might be disabled
            success, data = test_endpoint(endpoint, 200, description)
            if not success:
                success, data = test_endpoint(endpoint, 403, f"{description} (disabled)")
        else:
            success, data = test_endpoint(endpoint, expected_status, description)
        
        if success:
            passed += 1
        else:
            failed += 1
        
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Hub service is working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Check the Hub service configuration.")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
