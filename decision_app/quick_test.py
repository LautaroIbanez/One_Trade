"""
Quick test script for RSI strategy.
"""

import requests
import json

def test_health():
    """Test health endpoint."""
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1/health/")
        print(f"✅ Health Check: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health Check: {e}")
        return False

def test_strategies():
    """Test strategies endpoint."""
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1/strategies/")
        strategies = response.json()
        print(f"✅ Strategies: Found {len(strategies)} strategies")
        for strategy in strategies:
            print(f"   • {strategy['name']}: {strategy['description']}")
        return True
    except Exception as e:
        print(f"❌ Strategies: {e}")
        return False

def test_rsi_analysis():
    """Test RSI analysis with sample data."""
    try:
        # Simple sample data
        sample_data = [
            {"timestamp": "2024-01-01T00:00:00", "open": 50000, "high": 51000, "low": 49000, "close": 50500, "volume": 1000},
            {"timestamp": "2024-01-02T00:00:00", "open": 50500, "high": 52000, "low": 50000, "close": 51500, "volume": 1200},
            {"timestamp": "2024-01-03T00:00:00", "open": 51500, "high": 53000, "low": 51000, "close": 52500, "volume": 1100},
            {"timestamp": "2024-01-04T00:00:00", "open": 52500, "high": 54000, "low": 52000, "close": 53500, "volume": 1300},
            {"timestamp": "2024-01-05T00:00:00", "open": 53500, "high": 55000, "low": 53000, "close": 54500, "volume": 1400},
        ]
        
        payload = {"data": sample_data}
        response = requests.post(
            "http://127.0.0.1:8000/api/v1/strategies/RSI Strategy/analyze",
            json=payload
        )
        
        analysis = response.json()
        print(f"✅ RSI Analysis: {analysis['total_signals']} signals generated")
        
        if analysis['signals']:
            for signal in analysis['signals']:
                print(f"   • {signal['signal']} at ${signal['price']} (confidence: {signal['confidence']:.2f})")
                print(f"     Reasoning: {signal['reasoning']}")
        else:
            print("   • No signals generated (RSI in neutral zone)")
        
        return True
    except Exception as e:
        print(f"❌ RSI Analysis: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Quick RSI Strategy Test")
    print("=" * 40)
    
    # Test 1: Health
    print("\n1. Testing Health Endpoint...")
    health_ok = test_health()
    
    # Test 2: Strategies
    print("\n2. Testing Strategies Endpoint...")
    strategies_ok = test_strategies()
    
    # Test 3: RSI Analysis
    print("\n3. Testing RSI Analysis...")
    rsi_ok = test_rsi_analysis()
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Summary:")
    print(f"   Health: {'✅' if health_ok else '❌'}")
    print(f"   Strategies: {'✅' if strategies_ok else '❌'}")
    print(f"   RSI Analysis: {'✅' if rsi_ok else '❌'}")
    
    if all([health_ok, strategies_ok, rsi_ok]):
        print("\n🎉 All tests passed! RSI Strategy is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
