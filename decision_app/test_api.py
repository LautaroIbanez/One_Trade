#!/usr/bin/env python3
"""
Script para probar las APIs del backend de One Trade Decision App
"""

import requests
import json
import time
import sys

def test_backend_apis():
    """Probar las APIs del backend"""
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Probando APIs del Backend One Trade Decision App")
    print("=" * 60)
    
    # Test 1: Health Check
    print("\n1. 🔍 Probando Health Check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health Check: OK")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health Check: Error {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health Check: No se pudo conectar - {e}")
        return False
    
    # Test 2: API Documentation
    print("\n2. 📚 Probando documentación de API...")
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API Docs: Disponible en http://127.0.0.1:8000/docs")
        else:
            print(f"❌ API Docs: Error {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ API Docs: Error - {e}")
    
    # Test 3: Recommendations API
    print("\n3. 💡 Probando API de Recomendaciones...")
    try:
        # Probar endpoint de recomendaciones activas
        response = requests.get(f"{base_url}/api/v1/recommendations/latest/active", timeout=5)
        if response.status_code == 200:
            print("✅ Recommendations API: OK")
            data = response.json()
            print(f"   Recomendaciones activas: {len(data)}")
        else:
            print(f"❌ Recommendations API: Error {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Recommendations API: Error - {e}")
    
    # Test 4: Market Data API
    print("\n4. 📊 Probando API de Market Data...")
    try:
        response = requests.get(f"{base_url}/api/v1/market-data/symbols", timeout=5)
        if response.status_code == 200:
            print("✅ Market Data API: OK")
            data = response.json()
            print(f"   Símbolos disponibles: {len(data)}")
        else:
            print(f"❌ Market Data API: Error {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Market Data API: Error - {e}")
    
    # Test 5: Backtests API
    print("\n5. 🔬 Probando API de Backtests...")
    try:
        response = requests.get(f"{base_url}/api/v1/backtests/", timeout=5)
        if response.status_code == 200:
            print("✅ Backtests API: OK")
            data = response.json()
            print(f"   Backtests disponibles: {len(data)}")
        else:
            print(f"❌ Backtests API: Error {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Backtests API: Error - {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Pruebas de API completadas!")
    print("\n📋 URLs importantes:")
    print(f"   • Backend API: {base_url}")
    print(f"   • API Docs: {base_url}/docs")
    print(f"   • Frontend: http://localhost:3000")
    
    return True

def test_frontend():
    """Probar si el frontend está ejecutándose"""
    print("\n🌐 Probando Frontend...")
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend: Ejecutándose en http://localhost:3000")
            return True
        else:
            print(f"❌ Frontend: Error {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Frontend: No se pudo conectar - {e}")
        print("   💡 Asegúrate de ejecutar: cd frontend && npm run dev")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando validación del sistema One Trade Decision App")
    print("   Asegúrate de que el backend esté ejecutándose en puerto 8000")
    print("   Asegúrate de que el frontend esté ejecutándose en puerto 3000")
    
    # Esperar un momento para que los servicios se inicien
    print("\n⏳ Esperando 3 segundos para que los servicios se inicien...")
    time.sleep(3)
    
    # Probar backend
    backend_ok = test_backend_apis()
    
    # Probar frontend
    frontend_ok = test_frontend()
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VALIDACIÓN:")
    print(f"   Backend: {'✅ OK' if backend_ok else '❌ Error'}")
    print(f"   Frontend: {'✅ OK' if frontend_ok else '❌ Error'}")
    
    if backend_ok and frontend_ok:
        print("\n🎉 ¡Sistema completamente funcional!")
        print("   Puedes acceder a:")
        print("   • Frontend: http://localhost:3000")
        print("   • Backend API: http://127.0.0.1:8000/docs")
    else:
        print("\n⚠️  Hay problemas que resolver:")
        if not backend_ok:
            print("   • Backend: Ejecuta 'cd backend && python -m uvicorn main:app --reload'")
        if not frontend_ok:
            print("   • Frontend: Ejecuta 'cd frontend && npm run dev'")
    
    sys.exit(0 if (backend_ok and frontend_ok) else 1)
