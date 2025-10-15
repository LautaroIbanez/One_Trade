"""
Test script for RSI strategy implementation.
"""

import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta

# Backend URL
BACKEND_URL = "http://127.0.0.1:8000"

def generate_sample_data(days: int = 30) -> pd.DataFrame:
    """Generate sample OHLCV data for testing."""
    dates = pd.date_range(start=datetime.now() - timedelta(days=days), periods=days, freq='D')
    
    # Generate realistic price data with some volatility
    np.random.seed(42)  # For reproducible results
    base_price = 50000  # Starting price
    prices = [base_price]
    
    for i in range(1, days):
        # Random walk with slight upward bias
        change = np.random.normal(0.001, 0.02)  # 0.1% mean return, 2% volatility
        new_price = prices[-1] * (1 + change)
        prices.append(max(new_price, 1000))  # Minimum price of 1000
    
    # Create OHLCV data
    data = []
    for i, (date, close) in enumerate(zip(dates, prices)):
        # Generate realistic OHLC from close price
        volatility = 0.01  # 1% intraday volatility
        high = close * (1 + np.random.uniform(0, volatility))
        low = close * (1 - np.random.uniform(0, volatility))
        open_price = prices[i-1] if i > 0 else close
        volume = np.random.uniform(1000, 10000)
        
        data.append({
            'timestamp': date.isoformat(),
            'open': round(open_price, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(close, 2),
            'volume': round(volume, 0)
        })
    
    return pd.DataFrame(data)

def test_strategy_endpoints():
    """Test the strategy API endpoints."""
    print("🧪 Testing RSI Strategy Implementation")
    print("=" * 50)
    
    # Generate sample data
    print("📊 Generating sample market data...")
    sample_data = generate_sample_data(30)
    print(f"   Generated {len(sample_data)} data points")
    print(f"   Price range: ${sample_data['close'].min():.2f} - ${sample_data['close'].max():.2f}")
    
    # Test 1: List strategies
    print("\n1. 📋 Testing list strategies endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/strategies/")
        response.raise_for_status()
        strategies = response.json()
        print(f"   ✅ Found {len(strategies)} strategies:")
        for strategy in strategies:
            print(f"      • {strategy['name']}: {strategy['description']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 2: Get RSI strategy info
    print("\n2. 🔍 Testing get RSI strategy info...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/strategies/RSI Strategy")
        response.raise_for_status()
        strategy_info = response.json()
        print(f"   ✅ Strategy: {strategy_info['name']}")
        print(f"   📝 Description: {strategy_info['description']}")
        print(f"   ⚙️  Parameters: {strategy_info['parameters']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 3: Analyze with RSI strategy
    print("\n3. 🎯 Testing RSI strategy analysis...")
    try:
        payload = {
            "data": sample_data.to_dict('records')
        }
        response = requests.post(
            f"{BACKEND_URL}/api/v1/strategies/RSI Strategy/analyze",
            json=payload
        )
        response.raise_for_status()
        analysis = response.json()
        
        print(f"   ✅ Analysis completed:")
        print(f"      • Total signals: {analysis['total_signals']}")
        
        if analysis['signals']:
            print(f"      • Latest signals:")
            for signal in analysis['signals'][-3:]:  # Show last 3 signals
                print(f"        - {signal['signal']} at ${signal['price']:.2f} "
                      f"(confidence: {signal['confidence']:.2f})")
                print(f"          Reasoning: {signal['reasoning']}")
        else:
            print(f"      • No signals generated (RSI may be in neutral zone)")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 4: Get strategy performance
    print("\n4. 📈 Testing strategy performance...")
    try:
        payload = {
            "data": sample_data.to_dict('records')
        }
        response = requests.post(
            f"{BACKEND_URL}/api/v1/strategies/RSI Strategy/performance",
            json=payload
        )
        response.raise_for_status()
        performance = response.json()
        
        print(f"   ✅ Performance metrics:")
        print(f"      • Total signals: {performance['total_signals']}")
        print(f"      • BUY signals: {performance['buy_signals']}")
        print(f"      • SELL signals: {performance['sell_signals']}")
        print(f"      • HOLD signals: {performance['hold_signals']}")
        print(f"      • Average confidence: {performance['avg_confidence']:.3f}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 5: Analyze with all strategies
    print("\n5. 🔄 Testing analyze with all strategies...")
    try:
        payload = {
            "data": sample_data.to_dict('records')
        }
        response = requests.post(
            f"{BACKEND_URL}/api/v1/strategies/analyze-all",
            json=payload
        )
        response.raise_for_status()
        all_analysis = response.json()
        
        print(f"   ✅ Analysis with all strategies:")
        for strategy_name, analysis in all_analysis.items():
            print(f"      • {strategy_name}: {analysis['total_signals']} signals")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    print("\n🎉 All tests completed successfully!")
    print("\n💡 Next steps:")
    print("   1. Check the API documentation at http://127.0.0.1:8000/docs")
    print("   2. Test the frontend integration")
    print("   3. Implement MACD and Bollinger Bands strategies")

if __name__ == "__main__":
    test_strategy_endpoints()
