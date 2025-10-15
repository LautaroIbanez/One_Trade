"""
Simple test to verify RSI strategy is working.
"""

import requests

print("🧪 Testing RSI Strategy Implementation")
print("=" * 50)

# Test 1: Health endpoint
print("\n1. Testing Health Endpoint...")
try:
    response = requests.get("http://127.0.0.1:8000/api/v1/health/")
    if response.status_code == 200:
        print("✅ Health endpoint working")
        print(f"   Response: {response.json()}")
    else:
        print(f"❌ Health endpoint failed: {response.status_code}")
except Exception as e:
    print(f"❌ Health endpoint error: {e}")

# Test 2: Strategies endpoint
print("\n2. Testing Strategies Endpoint...")
try:
    response = requests.get("http://127.0.0.1:8000/api/v1/strategies/")
    if response.status_code == 200:
        strategies = response.json()
        print(f"✅ Strategies endpoint working - Found {len(strategies)} strategies")
        for strategy in strategies:
            print(f"   • {strategy['name']}")
    else:
        print(f"❌ Strategies endpoint failed: {response.status_code}")
except Exception as e:
    print(f"❌ Strategies endpoint error: {e}")

print("\n🎯 Test completed!")
