@echo off
echo 🚀 Iniciando One Trade Decision App
echo =====================================

echo.
echo 📋 Instrucciones:
echo 1. Ejecuta este script
echo 2. Se abrirán 3 ventanas de terminal
echo 3. Espera a que ambos servicios se inicien
echo 4. Ve a http://localhost:3000 para el frontend
echo 5. Ve a http://127.0.0.1:8000/docs para la API
echo.

echo ⏳ Iniciando servicios...
echo.

REM Iniciar Backend
echo 🔧 Iniciando Backend...
start "Backend - One Trade" cmd /k "cd /d %~dp0backend && venv\Scripts\activate && python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000"

REM Esperar un poco
timeout /t 3 /nobreak > nul

REM Iniciar Frontend
echo 🌐 Iniciando Frontend...
start "Frontend - One Trade" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ✅ Servicios iniciados!
echo.
echo 📋 URLs disponibles:
echo    • Frontend: http://localhost:3000
echo    • Backend API: http://127.0.0.1:8000
echo    • API Docs: http://127.0.0.1:8000/docs
echo.
echo 💡 Presiona cualquier tecla para cerrar esta ventana...
pause > nul
