"""
Test script for enhanced recommendation engine.
"""

import requests
import json
from datetime import datetime

# Backend URL
BACKEND_URL = "http://127.0.0.1:8000"

def test_enhanced_recommendations():
    """Test the enhanced recommendation engine."""
    print("🧪 Testing Enhanced Recommendation Engine")
    print("=" * 60)
    
    # Test 1: Generate enhanced recommendation for BTCUSDT
    print("\n1. 🎯 Testing enhanced recommendation for BTCUSDT...")
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/v1/enhanced-recommendations/generate/BTCUSDT",
            params={"timeframe": "1d", "days": 30}
        )
        response.raise_for_status()
        recommendation = response.json()
        
        print(f"   ✅ Recommendation generated successfully")
        print(f"   📊 Symbol: {recommendation['symbol']}")
        print(f"   💰 Current Price: ${recommendation['current_price']:.2f}")
        print(f"   🎯 Recommendation: {recommendation['recommendation']}")
        print(f"   🎲 Confidence: {recommendation['confidence']:.1%}")
        print(f"   ⚠️  Risk Level: {recommendation['risk_assessment']['level']}")
        print(f"   📈 Market Trend: {recommendation['market_context']['trend']}")
        
        print(f"\n   📋 Strategy Signals:")
        for signal in recommendation['strategy_signals']:
            print(f"      • {signal['strategy']}: {signal['signal']} "
                  f"({signal['confidence']:.1%} confidence)")
            print(f"        {signal['reasoning']}")
        
        print(f"\n   📊 Signal Scores:")
        scores = recommendation['scores']
        print(f"      • BUY Score: {scores['buy_score']:.3f}")
        print(f"      • SELL Score: {scores['sell_score']:.3f}")
        print(f"      • HOLD Score: {scores['hold_score']:.3f}")
        
        print(f"\n   💭 Reasoning:")
        print(f"      {recommendation['reasoning']}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 2: Get recommendation summary
    print("\n2. 📋 Testing recommendation summary...")
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/v1/enhanced-recommendations/summary/BTCUSDT"
        )
        response.raise_for_status()
        summary = response.json()
        
        print(f"   ✅ Summary generated successfully")
        print(f"   📊 {summary['symbol']}: {summary['recommendation']} "
              f"({summary['confidence']:.1%} confidence)")
        print(f"   ⚠️  Risk: {summary['risk_level']} | Trend: {summary['trend']}")
        print(f"   💰 Price: ${summary['current_price']:.2f}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 3: Get supported symbols
    print("\n3. 🔍 Testing supported symbols...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/enhanced-recommendations/supported-symbols")
        response.raise_for_status()
        symbols = response.json()
        
        print(f"   ✅ Found {len(symbols)} supported symbols:")
        for symbol in symbols:
            print(f"      • {symbol}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 4: Get strategy weights
    print("\n4. ⚖️  Testing strategy weights...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/enhanced-recommendations/strategy-weights")
        response.raise_for_status()
        weights = response.json()
        
        print(f"   ✅ Current strategy weights:")
        for strategy, weight in weights.items():
            print(f"      • {strategy}: {weight:.1%}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 5: Update strategy weights
    print("\n5. 🔧 Testing strategy weights update...")
    try:
        new_weights = {
            "RSI Strategy": 0.5,
            "MACD Strategy": 0.3,
            "Bollinger Bands Strategy": 0.2
        }
        
        response = requests.put(
            f"{BACKEND_URL}/api/v1/enhanced-recommendations/strategy-weights",
            json={"weights": new_weights}
        )
        response.raise_for_status()
        result = response.json()
        
        print(f"   ✅ Strategy weights updated successfully")
        print(f"   📊 New weights:")
        for strategy, weight in result['weights'].items():
            print(f"      • {strategy}: {weight:.1%}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 6: Generate recommendation with new weights
    print("\n6. 🎯 Testing recommendation with updated weights...")
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/v1/enhanced-recommendations/generate/BTCUSDT"
        )
        response.raise_for_status()
        recommendation = response.json()
        
        print(f"   ✅ Recommendation with updated weights:")
        print(f"   🎯 {recommendation['recommendation']} "
              f"({recommendation['confidence']:.1%} confidence)")
        
        print(f"\n   📊 Updated Signal Scores:")
        scores = recommendation['scores']
        print(f"      • BUY Score: {scores['buy_score']:.3f}")
        print(f"      • SELL Score: {scores['sell_score']:.3f}")
        print(f"      • HOLD Score: {scores['hold_score']:.3f}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    print("\n🎉 All enhanced recommendation tests completed successfully!")
    print("\n💡 Key Features Tested:")
    print("   1. ✅ Multi-strategy signal consolidation")
    print("   2. ✅ Weighted scoring system")
    print("   3. ✅ Risk assessment")
    print("   4. ✅ Market context analysis")
    print("   5. ✅ Dynamic strategy weights")
    print("   6. ✅ Comprehensive reasoning")

def test_batch_recommendations():
    """Test batch recommendations for multiple symbols."""
    print("\n" + "=" * 60)
    print("🔄 Testing Batch Recommendations")
    print("=" * 60)
    
    try:
        symbols = "BTCUSDT,ETHUSDT,ADAUSDT"
        response = requests.get(
            f"{BACKEND_URL}/api/v1/enhanced-recommendations/batch/{symbols}",
            params={"timeframe": "1d", "days": 30}
        )
        response.raise_for_status()
        batch_results = response.json()
        
        print(f"   ✅ Batch recommendations generated for {len(batch_results)} symbols:")
        
        for symbol, result in batch_results.items():
            if "error" in result:
                print(f"      • {symbol}: ❌ Error - {result['error']}")
            else:
                print(f"      • {symbol}: {result['recommendation']} "
                      f"({result['confidence']:.1%} confidence)")
                print(f"        Risk: {result['risk_assessment']['level']} | "
                      f"Trend: {result['market_context']['trend']}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_enhanced_recommendations()
    test_batch_recommendations()
