#!/usr/bin/env python3
"""
Test script for the Backtesting Engine
"""

import requests
import time
from datetime import datetime, timedelta

# URLs
BACKEND_URL = "http://127.0.0.1:8000"

def test_backtest_quick():
    """Test quick backtest functionality."""
    print("\n1. 🚀 Testing Quick Backtest...")
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/v1/backtests/quick-test/BTCUSDT",
            params={
                "strategy": "RSI Strategy",
                "days": 30,
                "initial_capital": 10000
            }
        )
        response.raise_for_status()
        result = response.json()
        
        print("   ✅ Quick backtest completed successfully")
        print(f"   📊 Symbol: {result['symbol']}")
        print(f"   🎯 Strategy: {result['strategy']}")
        print(f"   📅 Period: {result['period']}")
        print(f"   💰 Initial Capital: ${result['initial_capital']:,.2f}")
        print(f"   💰 Final Capital: ${result['final_capital']:,.2f}")
        print(f"   📈 Total Return: {result['total_return']}")
        print(f"   📊 Annualized Return: {result['annualized_return']}")
        print(f"   ⚖️  Sharpe Ratio: {result['sharpe_ratio']}")
        print(f"   📉 Max Drawdown: {result['max_drawdown']}")
        print(f"   🎯 Win Rate: {result['win_rate']}")
        print(f"   🔢 Total Trades: {result['total_trades']}")
        print(f"   ⏱️  Avg Trade Duration: {result['avg_trade_duration']}")
        print(f"   🏆 Best Trade: {result['best_trade']}")
        print(f"   💔 Worst Trade: {result['worst_trade']}")
        print(f"   💎 Profit Factor: {result['profit_factor']}")
        print(f"   📊 Calmar Ratio: {result['calmar_ratio']}")
        print(f"   📈 Sortino Ratio: {result['sortino_ratio']}")
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error: {e}")
        return False

def test_backtest_compare():
    """Test strategy comparison functionality."""
    print("\n2. 🔄 Testing Strategy Comparison...")
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/v1/backtests/compare/BTCUSDT",
            params={
                "days": 30,
                "initial_capital": 10000
            }
        )
        response.raise_for_status()
        result = response.json()
        
        print("   ✅ Strategy comparison completed successfully")
        print(f"   📊 Symbol: {result['symbol']}")
        print(f"   📅 Period: {result['period']}")
        print(f"   💰 Initial Capital: ${result['initial_capital']:,.2f}")
        print(f"   🎯 Strategies compared: {len(result['strategies'])}")
        
        print("\n   📋 Strategy Results:")
        for strategy_name, strategy_result in result['strategies'].items():
            if 'error' in strategy_result:
                print(f"      • {strategy_name}: Error - {strategy_result['error']}")
            else:
                print(f"      • {strategy_name}:")
                print(f"        - Total Return: {strategy_result['total_return']}")
                print(f"        - Sharpe Ratio: {strategy_result['sharpe_ratio']}")
                print(f"        - Max Drawdown: {strategy_result['max_drawdown']}")
                print(f"        - Win Rate: {strategy_result['win_rate']}")
                print(f"        - Total Trades: {strategy_result['total_trades']}")
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error: {e}")
        return False

def test_available_strategies():
    """Test getting available strategies."""
    print("\n3. 📋 Testing Available Strategies...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/backtests/strategies")
        response.raise_for_status()
        strategies = response.json()
        
        print("   ✅ Available strategies retrieved successfully")
        print(f"   🎯 Found {len(strategies)} strategies:")
        for strategy in strategies:
            print(f"      • {strategy}")
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error: {e}")
        return False

def test_available_symbols():
    """Test getting available symbols."""
    print("\n4. 🔍 Testing Available Symbols...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/backtests/symbols")
        response.raise_for_status()
        symbols = response.json()
        
        print("   ✅ Available symbols retrieved successfully")
        print(f"   📊 Found {len(symbols)} symbols:")
        for symbol in symbols:
            print(f"      • {symbol}")
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error: {e}")
        return False

def test_multiple_symbols():
    """Test backtesting multiple symbols."""
    print("\n5. 🌐 Testing Multiple Symbols...")
    symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
    results = {}
    
    for symbol in symbols:
        try:
            response = requests.get(
                f"{BACKEND_URL}/api/v1/backtests/quick-test/{symbol}",
                params={
                    "strategy": "RSI Strategy",
                    "days": 14,  # Shorter period for faster testing
                    "initial_capital": 5000
                }
            )
            response.raise_for_status()
            result = response.json()
            results[symbol] = result
            
            print(f"   ✅ {symbol}: {result['total_return']} return, {result['total_trades']} trades")
            
        except requests.exceptions.RequestException as e:
            print(f"   ❌ {symbol}: Error - {e}")
            results[symbol] = {"error": str(e)}
    
    # Summary
    print("\n   📊 Summary:")
    for symbol, result in results.items():
        if "error" in result:
            print(f"      • {symbol}: Failed")
        else:
            print(f"      • {symbol}: {result['total_return']} return, Sharpe: {result['sharpe_ratio']}")
    
    return len([r for r in results.values() if "error" not in r]) > 0

def run_backtesting_tests():
    """Run all backtesting tests."""
    print("🧪 TESTING BACKTESTING ENGINE")
    print("=" * 50)
    
    # Ensure backend is running
    try:
        requests.get(f"{BACKEND_URL}/health").raise_for_status()
        print("✅ Backend is healthy. Proceeding with backtesting tests.")
    except requests.exceptions.RequestException:
        print("❌ Backend is not running or not healthy. Please start the backend first.")
        return False
    
    all_tests_passed = True
    tests = [
        test_available_strategies,
        test_available_symbols,
        test_backtest_quick,
        test_backtest_compare,
        test_multiple_symbols,
    ]
    
    for test in tests:
        if not test():
            all_tests_passed = False
    
    print("\n" + "=" * 50)
    print("📊 BACKTESTING ENGINE TEST RESULTS:")
    print(f"   Overall Status: {'✅ ALL TESTS PASSED' if all_tests_passed else '❌ SOME TESTS FAILED'}")
    
    if all_tests_passed:
        print("\n🎉 Backtesting Engine is working perfectly!")
        print("\n💡 Features Tested:")
        print("   1. ✅ Quick backtest functionality")
        print("   2. ✅ Strategy comparison")
        print("   3. ✅ Available strategies retrieval")
        print("   4. ✅ Available symbols retrieval")
        print("   5. ✅ Multiple symbol backtesting")
        
        print("\n🚀 Backtesting Engine Ready!")
        print("   • Quick backtests: /api/v1/backtests/quick-test/{symbol}")
        print("   • Strategy comparison: /api/v1/backtests/compare/{symbol}")
        print("   • Available strategies: /api/v1/backtests/strategies")
        print("   • Available symbols: /api/v1/backtests/symbols")
    else:
        print("\n⚠️  Some backtesting tests failed.")
    
    return all_tests_passed

if __name__ == "__main__":
    run_backtesting_tests()
