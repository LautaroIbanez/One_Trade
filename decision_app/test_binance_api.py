"""
Test script for Binance API integration.
"""

import requests
import json
from datetime import datetime

# Backend URL
BACKEND_URL = "http://127.0.0.1:8000"

def test_binance_endpoints():
    """Test all Binance API endpoints."""
    print("🧪 Testing Binance API Integration")
    print("=" * 50)
    
    # Test 1: Server Time
    print("\n1. 🕐 Testing Binance server time...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/market-data/binance/time")
        response.raise_for_status()
        server_time = response.json()
        print(f"   ✅ Server time: {server_time['serverTime']}")
        print(f"   📅 Local time: {datetime.now().isoformat()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 2: Exchange Info
    print("\n2. 📊 Testing Binance exchange info...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/market-data/binance/exchange-info")
        response.raise_for_status()
        exchange_info = response.json()
        print(f"   ✅ Exchange info retrieved")
        print(f"   📈 Symbols available: {len(exchange_info.get('symbols', []))}")
        print(f"   ⏰ Server time: {exchange_info.get('serverTime')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 3: Get Symbols
    print("\n3. 🔍 Testing available symbols...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/market-data/binance/symbols")
        response.raise_for_status()
        symbols = response.json()
        print(f"   ✅ Found {len(symbols)} trading symbols")
        
        # Show some popular symbols
        popular_symbols = [s for s in symbols if any(coin in s for coin in ['BTC', 'ETH', 'ADA', 'SOL', 'DOT'])]
        print(f"   📋 Popular symbols: {popular_symbols[:10]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 4: Get Klines for BTCUSDT
    print("\n4. 📈 Testing klines for BTCUSDT...")
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/v1/market-data/binance/klines",
            params={
                "symbol": "BTCUSDT",
                "interval": "1d",
                "days": 7
            }
        )
        response.raise_for_status()
        klines_data = response.json()
        
        print(f"   ✅ Retrieved {klines_data['data_points']} data points")
        print(f"   📊 Symbol: {klines_data['symbol']}")
        print(f"   ⏱️  Interval: {klines_data['interval']}")
        
        if klines_data['data']:
            latest = klines_data['data'][-1]
            print(f"   💰 Latest price: ${latest['close']:.2f}")
            print(f"   📅 Latest timestamp: {latest['timestamp']}")
            
            # Show price range
            prices = [d['close'] for d in klines_data['data']]
            print(f"   📊 Price range: ${min(prices):.2f} - ${max(prices):.2f}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 5: Get 24hr Ticker
    print("\n5. 📊 Testing 24hr ticker for BTCUSDT...")
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/v1/market-data/binance/ticker",
            params={"symbol": "BTCUSDT"}
        )
        response.raise_for_status()
        tickers = response.json()
        
        if tickers:
            ticker = tickers[0]
            print(f"   ✅ Ticker data retrieved")
            print(f"   💰 Last price: ${ticker['last_price']:.2f}")
            print(f"   📈 24h change: {ticker['price_change_percent']:.2f}%")
            print(f"   📊 24h volume: {ticker['volume']:.2f} BTC")
            print(f"   🔄 24h trades: {ticker['count']:,}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    print("\n🎉 All Binance API tests completed successfully!")
    print("\n💡 Next steps:")
    print("   1. Test strategies with real Binance data")
    print("   2. Implement real-time data streaming")
    print("   3. Add more trading pairs")

def test_strategies_with_real_data():
    """Test strategies with real Binance data."""
    print("\n" + "=" * 50)
    print("🎯 Testing Strategies with Real Binance Data")
    print("=" * 50)
    
    # Get real data from Binance
    print("\n📊 Fetching real BTCUSDT data...")
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/v1/market-data/binance/klines",
            params={
                "symbol": "BTCUSDT",
                "interval": "1d",
                "days": 30
            }
        )
        response.raise_for_status()
        market_data = response.json()
        
        print(f"   ✅ Retrieved {market_data['data_points']} real data points")
        
        # Test with RSI Strategy
        print("\n🔍 Testing RSI Strategy with real data...")
        rsi_response = requests.post(
            f"{BACKEND_URL}/api/v1/strategies/RSI Strategy/analyze",
            json={"data": market_data['data']}
        )
        rsi_response.raise_for_status()
        rsi_analysis = rsi_response.json()
        
        print(f"   ✅ RSI Strategy: {rsi_analysis['total_signals']} signals")
        if rsi_analysis['signals']:
            latest_signal = rsi_analysis['signals'][-1]
            print(f"   📊 Latest signal: {latest_signal['signal']} at ${latest_signal['price']:.2f}")
            print(f"   🎯 Confidence: {latest_signal['confidence']:.2f}")
            print(f"   💭 Reasoning: {latest_signal['reasoning']}")
        
        # Test with MACD Strategy
        print("\n🔍 Testing MACD Strategy with real data...")
        macd_response = requests.post(
            f"{BACKEND_URL}/api/v1/strategies/MACD Strategy/analyze",
            json={"data": market_data['data']}
        )
        macd_response.raise_for_status()
        macd_analysis = macd_response.json()
        
        print(f"   ✅ MACD Strategy: {macd_analysis['total_signals']} signals")
        if macd_analysis['signals']:
            latest_signal = macd_analysis['signals'][-1]
            print(f"   📊 Latest signal: {latest_signal['signal']} at ${latest_signal['price']:.2f}")
            print(f"   🎯 Confidence: {latest_signal['confidence']:.2f}")
            print(f"   💭 Reasoning: {latest_signal['reasoning']}")
        
        # Test with Bollinger Bands Strategy
        print("\n🔍 Testing Bollinger Bands Strategy with real data...")
        bb_response = requests.post(
            f"{BACKEND_URL}/api/v1/strategies/Bollinger Bands Strategy/analyze",
            json={"data": market_data['data']}
        )
        bb_response.raise_for_status()
        bb_analysis = bb_response.json()
        
        print(f"   ✅ Bollinger Bands Strategy: {bb_analysis['total_signals']} signals")
        if bb_analysis['signals']:
            latest_signal = bb_analysis['signals'][-1]
            print(f"   📊 Latest signal: {latest_signal['signal']} at ${latest_signal['price']:.2f}")
            print(f"   🎯 Confidence: {latest_signal['confidence']:.2f}")
            print(f"   💭 Reasoning: {latest_signal['reasoning']}")
        
        print("\n🎉 Real data strategy testing completed!")
        
    except Exception as e:
        print(f"   ❌ Error testing strategies with real data: {e}")

if __name__ == "__main__":
    test_binance_endpoints()
    test_strategies_with_real_data()
