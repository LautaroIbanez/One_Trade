#!/usr/bin/env python3
"""
Test completo del sistema One Trade Decision App
Incluye todas las funcionalidades implementadas
"""

import requests
import time
import json
from typing import Dict, List, Any

# URLs
BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://localhost:3000"

def test_health_check():
    """Test 1: Health Check del Backend"""
    print("\n1. 🏥 Testing Backend Health Check...")
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        response.raise_for_status()
        health_data = response.json()
        print("   ✅ Backend is healthy")
        print(f"   📊 Status: {health_data['status']}")
        print(f"   🔧 Version: {health_data['version']}")
        print(f"   🌍 Environment: {health_data['environment']}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error: {e}")
        return False

def test_supported_symbols():
    """Test 2: Símbolos Soportados"""
    print("\n2. 🔍 Testing Supported Symbols...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/enhanced-recommendations/supported-symbols")
        response.raise_for_status()
        symbols = response.json()
        print(f"   ✅ Found {len(symbols)} supported symbols:")
        for symbol in symbols:
            print(f"      • {symbol}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error: {e}")
        return False

def test_strategy_weights():
    """Test 3: Pesos de Estrategias"""
    print("\n3. ⚖️  Testing Strategy Weights...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/enhanced-recommendations/strategy-weights")
        response.raise_for_status()
        weights = response.json()
        print("   ✅ Current strategy weights:")
        total_weight = 0
        for strategy, weight in weights.items():
            print(f"      • {strategy}: {weight:.1%}")
            total_weight += weight
        print(f"   📊 Total weight: {total_weight:.1%}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error: {e}")
        return False

def test_single_recommendation(symbol: str = "BTCUSDT"):
    """Test 4: Recomendación Individual"""
    print(f"\n4. 🎯 Testing Single Recommendation for {symbol}...")
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/v1/enhanced-recommendations/generate/{symbol}",
            params={"timeframe": "1d", "days": 30}
        )
        response.raise_for_status()
        recommendation = response.json()
        
        print("   ✅ Recommendation generated successfully")
        print(f"   📊 Symbol: {recommendation['symbol']}")
        print(f"   💰 Current Price: ${recommendation['current_price']:.2f}")
        print(f"   🎯 Recommendation: {recommendation['recommendation']}")
        print(f"   🎲 Confidence: {recommendation['confidence']:.1%}")
        print(f"   ⚠️  Risk Level: {recommendation['risk_assessment']['level']}")
        print(f"   📈 Market Trend: {recommendation['market_context']['trend']}")
        
        print("\n   📋 Strategy Signals:")
        for signal in recommendation['strategy_signals']:
            print(f"      • {signal['strategy']}: {signal['signal']} ({signal['confidence']:.1%} confidence)")
            print(f"        {signal['reasoning']}")
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error: {e}")
        return False

def test_recommendation_summary(symbol: str = "BTCUSDT"):
    """Test 5: Resumen de Recomendación"""
    print(f"\n5. 📋 Testing Recommendation Summary for {symbol}...")
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/v1/enhanced-recommendations/summary/{symbol}",
            params={"timeframe": "1d", "days": 30}
        )
        response.raise_for_status()
        summary = response.json()
        
        print("   ✅ Summary generated successfully")
        print(f"   📊 {summary['symbol']}: {summary['recommendation']} ({summary['confidence']:.1%} confidence)")
        print(f"   ⚠️  Risk: {summary['risk_level']} | Trend: {summary['trend']}")
        print(f"   💰 Price: ${summary['current_price']:.2f}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error: {e}")
        return False

def test_update_strategy_weights():
    """Test 6: Actualizar Pesos de Estrategias"""
    print("\n6. 🔧 Testing Strategy Weights Update...")
    try:
        # Test with different weights
        new_weights = {
            "RSI Strategy": 0.5,
            "MACD Strategy": 0.3,
            "Bollinger Bands Strategy": 0.2,
        }
        
        response = requests.put(
            f"{BACKEND_URL}/api/v1/enhanced-recommendations/strategy-weights",
            json={"weights": new_weights}
        )
        response.raise_for_status()
        updated_info = response.json()
        
        print(f"   ✅ {updated_info['message']}")
        print("   📊 New weights:")
        for strategy, weight in updated_info['weights'].items():
            print(f"      • {strategy}: {weight:.1%}")
        
        # Test recommendation with new weights
        print("\n   🎯 Testing recommendation with updated weights...")
        rec_response = requests.get(
            f"{BACKEND_URL}/api/v1/enhanced-recommendations/generate/BTCUSDT",
            params={"timeframe": "1d", "days": 30}
        )
        rec_response.raise_for_status()
        recommendation = rec_response.json()
        
        print(f"   📊 New recommendation: {recommendation['recommendation']} ({recommendation['confidence']:.1%} confidence)")
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error: {e}")
        return False

def test_batch_recommendations():
    """Test 7: Recomendaciones en Lote"""
    print("\n7. 🔄 Testing Batch Recommendations...")
    try:
        symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
        symbols_str = ",".join(symbols)
        
        response = requests.get(
            f"{BACKEND_URL}/api/v1/enhanced-recommendations/batch/{symbols_str}",
            params={"timeframe": "1d", "days": 30}
        )
        response.raise_for_status()
        batch_results = response.json()
        
        print(f"   ✅ Batch recommendations generated for {len(batch_results)} symbols:")
        for symbol, rec in batch_results.items():
            if "error" in rec:
                print(f"      • {symbol}: Error - {rec['error']}")
            else:
                print(f"      • {symbol}: {rec['recommendation']} ({rec['confidence']:.1%} confidence)")
                print(f"        Risk: {rec['risk_assessment']['level']} | Trend: {rec['market_context']['trend']}")
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error: {e}")
        return False

def test_add_remove_symbol():
    """Test 8: Agregar y Remover Símbolos"""
    print("\n8. 🔧 Testing Add/Remove Symbols...")
    try:
        test_symbol = "SOLUSDT"
        
        # Add symbol
        print(f"   ➕ Adding symbol: {test_symbol}")
        add_response = requests.post(
            f"{BACKEND_URL}/api/v1/enhanced-recommendations/supported-symbols/{test_symbol}"
        )
        add_response.raise_for_status()
        add_result = add_response.json()
        print(f"   ✅ {add_result['message']}")
        
        # Verify symbol was added
        symbols_response = requests.get(f"{BACKEND_URL}/api/v1/enhanced-recommendations/supported-symbols")
        symbols_response.raise_for_status()
        symbols = symbols_response.json()
        
        if test_symbol in symbols:
            print(f"   ✅ Symbol {test_symbol} successfully added")
        else:
            print(f"   ❌ Symbol {test_symbol} not found in supported symbols")
            return False
        
        # Test recommendation for new symbol
        print(f"   🎯 Testing recommendation for {test_symbol}...")
        rec_response = requests.get(
            f"{BACKEND_URL}/api/v1/enhanced-recommendations/generate/{test_symbol}",
            params={"timeframe": "1d", "days": 30}
        )
        rec_response.raise_for_status()
        recommendation = rec_response.json()
        print(f"   ✅ {test_symbol}: {recommendation['recommendation']} ({recommendation['confidence']:.1%} confidence)")
        
        # Remove symbol
        print(f"   ➖ Removing symbol: {test_symbol}")
        remove_response = requests.delete(
            f"{BACKEND_URL}/api/v1/enhanced-recommendations/supported-symbols/{test_symbol}"
        )
        remove_response.raise_for_status()
        remove_result = remove_response.json()
        print(f"   ✅ {remove_result['message']}")
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error: {e}")
        return False

def test_frontend_access():
    """Test 9: Acceso al Frontend"""
    print("\n9. 🌐 Testing Frontend Access...")
    try:
        response = requests.get(FRONTEND_URL)
        response.raise_for_status()
        print(f"   ✅ Frontend accessible at {FRONTEND_URL}")
        return True
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ Frontend not accessible - {e}")
        print(f"   💡 Make sure to run: cd frontend && npm run dev")
        return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Frontend error - {e}")
        return False

def run_complete_test():
    """Ejecutar todos los tests"""
    print("🧪 COMPLETE SYSTEM TEST - One Trade Decision App")
    print("=" * 60)
    
    # Ensure backend is running
    try:
        requests.get(f"{BACKEND_URL}/health").raise_for_status()
        print("✅ Backend is healthy. Proceeding with tests.")
    except requests.exceptions.RequestException:
        print("❌ Backend is not running or not healthy. Please start the backend first.")
        return False
    
    all_tests_passed = True
    tests = [
        test_health_check,
        test_supported_symbols,
        test_strategy_weights,
        test_single_recommendation,
        test_recommendation_summary,
        test_update_strategy_weights,
        test_batch_recommendations,
        test_add_remove_symbol,
        test_frontend_access,
    ]
    
    for test in tests:
        if not test():
            all_tests_passed = False
    
    print("\n" + "=" * 60)
    print("📊 FINAL TEST RESULTS:")
    print(f"   Overall Status: {'✅ ALL TESTS PASSED' if all_tests_passed else '❌ SOME TESTS FAILED'}")
    
    if all_tests_passed:
        print("\n🎉 ¡Sistema completo funcionando perfectamente!")
        print("\n💡 Funcionalidades Verificadas:")
        print("   1. ✅ Health Check del Backend")
        print("   2. ✅ Gestión de Símbolos Soportados")
        print("   3. ✅ Pesos de Estrategias Dinámicos")
        print("   4. ✅ Recomendaciones Individuales")
        print("   5. ✅ Resúmenes de Recomendaciones")
        print("   6. ✅ Actualización de Pesos en Tiempo Real")
        print("   7. ✅ Recomendaciones en Lote")
        print("   8. ✅ Agregar/Remover Símbolos")
        print("   9. ✅ Acceso al Frontend")
        
        print("\n🚀 Sistema Listo para Producción!")
        print("   • Backend: http://127.0.0.1:8000")
        print("   • Frontend: http://localhost:3000")
        print("   • API Docs: http://127.0.0.1:8000/docs")
    else:
        print("\n⚠️  Hay problemas que resolver antes de continuar.")
    
    return all_tests_passed

if __name__ == "__main__":
    run_complete_test()
