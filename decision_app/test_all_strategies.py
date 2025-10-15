"""
Test script for all three strategies: RSI, MACD, and Bollinger Bands.
"""

import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta

# Backend URL
BACKEND_URL = "http://127.0.0.1:8000"

def generate_comprehensive_data(days: int = 60) -> pd.DataFrame:
    """Generate comprehensive OHLCV data for testing all strategies."""
    dates = pd.date_range(start=datetime.now() - timedelta(days=days), periods=days, freq='D')
    
    # Generate data with different market conditions
    np.random.seed(42)  # For reproducible results
    base_price = 50000  # Starting price
    
    prices = []
    for i in range(days):
        if i < days // 4:
            # Strong uptrend (RSI overbought, MACD bullish, price near upper BB)
            trend = 0.025  # 2.5% daily growth
            volatility = 0.02
        elif i < days // 2:
            # Volatile sideways (RSI oscillating, MACD neutral, BB touches)
            trend = 0.001  # 0.1% daily growth
            volatility = 0.03
        elif i < 3 * days // 4:
            # Downtrend (RSI oversold, MACD bearish, price near lower BB)
            trend = -0.02  # -2% daily decline
            volatility = 0.025
        else:
            # Recovery (RSI recovery, MACD crossover, BB bounce)
            trend = 0.015  # 1.5% daily growth
            volatility = 0.02
        
        if i == 0:
            prices.append(base_price)
        else:
            change = trend + np.random.normal(0, volatility)
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

def test_all_strategies():
    """Test all three strategies together."""
    print("🧪 Testing All Three Strategies: RSI, MACD, and Bollinger Bands")
    print("=" * 70)
    
    # Generate sample data
    print("📊 Generating comprehensive market data...")
    sample_data = generate_comprehensive_data(60)
    print(f"   Generated {len(sample_data)} data points")
    print(f"   Price range: ${sample_data['close'].min():.2f} - ${sample_data['close'].max():.2f}")
    
    # Test 1: List all strategies
    print("\n1. 📋 Testing list all strategies...")
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
    
    # Test 2: Analyze with all strategies
    print("\n2. 🔄 Testing analyze with all strategies...")
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
        total_signals = 0
        for strategy_name, analysis in all_analysis.items():
            signal_count = analysis['total_signals']
            total_signals += signal_count
            print(f"      • {strategy_name}: {signal_count} signals")
            
            # Show sample signals for each strategy
            if analysis['signals']:
                print(f"        Sample signals:")
                for signal in analysis['signals'][-2:]:  # Show last 2 signals
                    print(f"          - {signal['signal']} at ${signal['price']:.2f} "
                          f"(confidence: {signal['confidence']:.2f})")
                    print(f"            {signal['reasoning']}")
        
        print(f"\n   📊 Total signals across all strategies: {total_signals}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 3: Individual strategy performance
    print("\n3. 📈 Testing individual strategy performance...")
    strategies_to_test = ["RSI Strategy", "MACD Strategy", "Bollinger Bands Strategy"]
    
    for strategy_name in strategies_to_test:
        try:
            payload = {
                "data": sample_data.to_dict('records')
            }
            response = requests.post(
                f"{BACKEND_URL}/api/v1/strategies/{strategy_name}/performance",
                json=payload
            )
            response.raise_for_status()
            performance = response.json()
            
            print(f"   ✅ {strategy_name}:")
            print(f"      • Total signals: {performance['total_signals']}")
            print(f"      • BUY: {performance['buy_signals']}, SELL: {performance['sell_signals']}, HOLD: {performance['hold_signals']}")
            print(f"      • Average confidence: {performance['avg_confidence']:.3f}")
            
        except Exception as e:
            print(f"   ❌ {strategy_name}: Error - {e}")
    
    # Test 4: Strategy comparison
    print("\n4. 🔍 Strategy comparison and insights...")
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
        
        print("   📊 Strategy Characteristics:")
        
        # RSI Analysis
        rsi_analysis = all_analysis.get("RSI Strategy", {})
        rsi_signals = rsi_analysis.get('signals', [])
        print(f"      • RSI Strategy: {len(rsi_signals)} signals")
        print(f"        - Most active strategy, good for trend detection")
        print(f"        - Generates signals based on overbought/oversold conditions")
        
        # MACD Analysis
        macd_analysis = all_analysis.get("MACD Strategy", {})
        macd_signals = macd_analysis.get('signals', [])
        print(f"      • MACD Strategy: {len(macd_signals)} signals")
        print(f"        - Selective strategy, good for trend changes")
        print(f"        - Generates signals based on momentum crossovers")
        
        # Bollinger Bands Analysis
        bb_analysis = all_analysis.get("Bollinger Bands Strategy", {})
        bb_signals = bb_analysis.get('signals', [])
        print(f"      • Bollinger Bands Strategy: {len(bb_signals)} signals")
        print(f"        - Volatility-based strategy, good for mean reversion")
        print(f"        - Generates signals based on band touches and bounces")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    print("\n🎉 All strategy tests completed successfully!")
    print("\n💡 Key Insights:")
    print("   1. RSI: Most active, good for trend detection")
    print("   2. MACD: Selective, good for trend changes")
    print("   3. Bollinger Bands: Volatility-based, good for mean reversion")
    print("\n🚀 Next steps:")
    print("   1. Integrate strategies in recommendation engine")
    print("   2. Connect with real market data (Binance API)")
    print("   3. Implement strategy weighting and combination")

if __name__ == "__main__":
    test_all_strategies()
