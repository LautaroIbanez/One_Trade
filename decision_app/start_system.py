#!/usr/bin/env python3
"""
Script para iniciar el sistema completo de One Trade Decision App
"""

import subprocess
import time
import sys
import os
import signal
import threading
from pathlib import Path

def start_backend():
    """Iniciar el backend FastAPI"""
    print("🚀 Iniciando Backend FastAPI...")
    backend_dir = Path(__file__).parent / "backend"
    
    try:
        # Cambiar al directorio del backend
        os.chdir(backend_dir)
        
        # Iniciar el servidor
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "main:app", "--reload", 
            "--host", "127.0.0.1", 
            "--port", "8000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        print("✅ Backend iniciado en http://127.0.0.1:8000")
        return process
        
    except Exception as e:
        print(f"❌ Error iniciando backend: {e}")
        return None

def start_frontend():
    """Iniciar el frontend React"""
    print("🌐 Iniciando Frontend React...")
    frontend_dir = Path(__file__).parent / "frontend"
    
    try:
        # Cambiar al directorio del frontend
        os.chdir(frontend_dir)
        
        # Iniciar el servidor de desarrollo
        process = subprocess.Popen([
            "npm", "run", "dev"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        print("✅ Frontend iniciado en http://localhost:3000")
        return process
        
    except Exception as e:
        print(f"❌ Error iniciando frontend: {e}")
        return None

def monitor_process(process, name):
    """Monitorear un proceso y mostrar su output"""
    try:
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(f"[{name}] {output.strip()}")
    except:
        pass

def main():
    """Función principal"""
    print("🎯 One Trade Decision App - Sistema Completo")
    print("=" * 50)
    
    # Iniciar backend
    backend_process = start_backend()
    if not backend_process:
        print("❌ No se pudo iniciar el backend")
        return 1
    
    # Esperar un poco para que el backend se inicie
    print("⏳ Esperando que el backend se inicie...")
    time.sleep(5)
    
    # Iniciar frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("❌ No se pudo iniciar el frontend")
        backend_process.terminate()
        return 1
    
    # Esperar un poco para que el frontend se inicie
    print("⏳ Esperando que el frontend se inicie...")
    time.sleep(5)
    
    print("\n🎉 Sistema iniciado correctamente!")
    print("📋 URLs disponibles:")
    print("   • Frontend: http://localhost:3000")
    print("   • Backend API: http://127.0.0.1:8000")
    print("   • API Docs: http://127.0.0.1:8000/docs")
    print("\n💡 Presiona Ctrl+C para detener el sistema")
    
    # Función para manejar la señal de interrupción
    def signal_handler(sig, frame):
        print("\n🛑 Deteniendo sistema...")
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        print("✅ Sistema detenido")
        sys.exit(0)
    
    # Registrar el manejador de señales
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Monitorear los procesos
        backend_thread = threading.Thread(target=monitor_process, args=(backend_process, "BACKEND"))
        frontend_thread = threading.Thread(target=monitor_process, args=(frontend_process, "FRONTEND"))
        
        backend_thread.daemon = True
        frontend_thread.daemon = True
        
        backend_thread.start()
        frontend_thread.start()
        
        # Mantener el script ejecutándose
        while True:
            time.sleep(1)
            
            # Verificar si los procesos siguen ejecutándose
            if backend_process.poll() is not None:
                print("❌ Backend se detuvo inesperadamente")
                break
            if frontend_process.poll() is not None:
                print("❌ Frontend se detuvo inesperadamente")
                break
                
    except KeyboardInterrupt:
        signal_handler(None, None)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
