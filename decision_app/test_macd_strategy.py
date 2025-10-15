"""
Test script for MACD strategy implementation.
"""

import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta

# Backend URL
BACKEND_URL = "http://127.0.0.1:8000"

def generate_trending_data(days: int = 50) -> pd.DataFrame:
    """Generate trending OHLCV data for MACD testing."""
    dates = pd.date_range(start=datetime.now() - timedelta(days=days), periods=days, freq='D')
    
    # Generate trending price data with clear MACD signals
    np.random.seed(42)  # For reproducible results
    base_price = 50000  # Starting price
    
    # Create a clear uptrend followed by downtrend
    prices = []
    for i in range(days):
        if i < days // 3:
            # Uptrend
            trend = 0.02  # 2% daily growth
        elif i < 2 * days // 3:
            # Sideways
            trend = 0.001  # 0.1% daily growth
        else:
            # Downtrend
            trend = -0.015  # -1.5% daily decline
        
        if i == 0:
            prices.append(base_price)
        else:
            change = trend + np.random.normal(0, 0.01)  # Add some noise
            new_price = prices[-1] * (1 + change)
            prices.append(max(new_price, 1000))  # Minimum price of 1000
    
    # Create OHLCV data
    data = []
    for i, (date, close) in enumerate(zip(dates, prices)):
        # Generate realistic OHLC from close price
        volatility = 0.015  # 1.5% intraday volatility
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

def test_macd_strategy():
    """Test the MACD strategy implementation."""
    print("🧪 Testing MACD Strategy Implementation")
    print("=" * 50)
    
    # Generate sample data
    print("📊 Generating trending market data for MACD testing...")
    sample_data = generate_trending_data(50)
    print(f"   Generated {len(sample_data)} data points")
    print(f"   Price range: ${sample_data['close'].min():.2f} - ${sample_data['close'].max():.2f}")
    
    # Test 1: List strategies (should now include MACD)
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
    
    # Test 2: Get MACD strategy info
    print("\n2. 🔍 Testing get MACD strategy info...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/strategies/MACD Strategy")
        response.raise_for_status()
        strategy_info = response.json()
        print(f"   ✅ Strategy: {strategy_info['name']}")
        print(f"   📝 Description: {strategy_info['description']}")
        print(f"   ⚙️  Parameters: {strategy_info['parameters']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 3: Analyze with MACD strategy
    print("\n3. 🎯 Testing MACD strategy analysis...")
    try:
        payload = {
            "data": sample_data.to_dict('records')
        }
        response = requests.post(
            f"{BACKEND_URL}/api/v1/strategies/MACD Strategy/analyze",
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
                if 'macd_value' in signal['metadata']:
                    print(f"          MACD: {signal['metadata']['macd_value']:.4f}, "
                          f"Signal: {signal['metadata']['signal_value']:.4f}")
        else:
            print(f"      • No signals generated (no clear crossovers detected)")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 4: Get MACD strategy performance
    print("\n4. 📈 Testing MACD strategy performance...")
    try:
        payload = {
            "data": sample_data.to_dict('records')
        }
        response = requests.post(
            f"{BACKEND_URL}/api/v1/strategies/MACD Strategy/performance",
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
    
    # Test 5: Analyze with all strategies (RSI + MACD)
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
    
    print("\n🎉 All MACD tests completed successfully!")
    print("\n💡 Next steps:")
    print("   1. Check the API documentation at http://127.0.0.1:8000/docs")
    print("   2. Test both RSI and MACD strategies together")
    print("   3. Implement Bollinger Bands strategy")

if __name__ == "__main__":
    test_macd_strategy()
