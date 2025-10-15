#!/usr/bin/env python3
"""
Test de integración para validar CORS y endpoints del backend
"""

import requests
import json
import time
from typing import Dict, Any

# Configuración
BACKEND_URL = "http://localhost:8000"
FRONTEND_ORIGIN = "http://localhost:3000"

def test_health_endpoint():
    """Test del endpoint de health check."""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["cors_enabled"] == True
        print("✅ Health endpoint working correctly")
        return True
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
        return False

def test_cors_headers():
    """Test de headers CORS."""
    print("🔍 Testing CORS headers...")
    try:
        headers = {"Origin": FRONTEND_ORIGIN}
        response = requests.options(f"{BACKEND_URL}/api/v1/enhanced-recommendations/supported-symbols", headers=headers)
        
        # Verificar headers CORS
        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
            "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials")
        }
        
        print(f"📋 CORS Headers: {cors_headers}")
        
        # Verificar que el origen está permitido
        assert cors_headers["Access-Control-Allow-Origin"] == FRONTEND_ORIGIN or cors_headers["Access-Control-Allow-Origin"] == "*"
        assert "GET" in cors_headers["Access-Control-Allow-Methods"]
        assert cors_headers["Access-Control-Allow-Credentials"] == "true"
        
        print("✅ CORS headers configured correctly")
        return True
    except Exception as e:
        print(f"❌ CORS headers test failed: {e}")
        return False

def test_supported_symbols_endpoint():
    """Test del endpoint de símbolos soportados."""
    print("🔍 Testing supported symbols endpoint...")
    try:
        headers = {"Origin": FRONTEND_ORIGIN}
        response = requests.get(f"{BACKEND_URL}/api/v1/enhanced-recommendations/supported-symbols", headers=headers)
        
        assert response.status_code == 200
        symbols = response.json()
        assert isinstance(symbols, list)
        assert len(symbols) > 0
        assert "BTCUSDT" in symbols
        
        print(f"✅ Supported symbols: {symbols}")
        return True
    except Exception as e:
        print(f"❌ Supported symbols endpoint failed: {e}")
        return False

def test_generate_recommendation_endpoint():
    """Test del endpoint de generación de recomendaciones."""
    print("🔍 Testing generate recommendation endpoint...")
    try:
        headers = {"Origin": FRONTEND_ORIGIN}
        response = requests.get(f"{BACKEND_URL}/api/v1/enhanced-recommendations/generate/BTCUSDT?timeframe=1d&days=30", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "symbol" in data
        assert "recommendation" in data
        assert "confidence" in data
        assert "timestamp" in data
        assert data["symbol"] == "BTCUSDT"
        
        print(f"✅ Recommendation generated: {data['recommendation']} (confidence: {data['confidence']})")
        return True
    except Exception as e:
        print(f"❌ Generate recommendation endpoint failed: {e}")
        return False

def test_batch_recommendations_endpoint():
    """Test del endpoint de recomendaciones en lote."""
    print("🔍 Testing batch recommendations endpoint...")
    try:
        headers = {"Origin": FRONTEND_ORIGIN}
        response = requests.get(f"{BACKEND_URL}/api/v1/enhanced-recommendations/batch/BTCUSDT,ETHUSDT,ADAUSDT?timeframe=1d&days=30", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "BTCUSDT" in data
        assert "ETHUSDT" in data
        assert "ADAUSDT" in data
        
        print(f"✅ Batch recommendations generated for {len(data)} symbols")
        return True
    except Exception as e:
        print(f"❌ Batch recommendations endpoint failed: {e}")
        return False

def test_stats_endpoint():
    """Test del endpoint de estadísticas."""
    print("🔍 Testing stats endpoint...")
    try:
        headers = {"Origin": FRONTEND_ORIGIN}
        response = requests.get(f"{BACKEND_URL}/api/v1/stats", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "activeRecommendations" in data
        assert "totalPnL" in data
        assert "winRate" in data
        assert "maxDrawdown" in data
        
        print(f"✅ Stats retrieved: {data['activeRecommendations']} active recommendations")
        return True
    except Exception as e:
        print(f"❌ Stats endpoint failed: {e}")
        return False

def main():
    """Ejecutar todos los tests."""
    print("="*60)
    print("🧪 One Trade Decision App - CORS Integration Tests")
    print("="*60)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Frontend Origin: {FRONTEND_ORIGIN}")
    print("="*60)
    
    # Esperar a que el servidor esté listo
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    tests = [
        test_health_endpoint,
        test_cors_headers,
        test_supported_symbols_endpoint,
        test_generate_recommendation_endpoint,
        test_batch_recommendations_endpoint,
        test_stats_endpoint
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
        print()
    
    # Resumen de resultados
    passed = sum(results)
    total = len(results)
    
    print("="*60)
    print("📊 Test Results Summary")
    print("="*60)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! CORS is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the backend configuration.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
