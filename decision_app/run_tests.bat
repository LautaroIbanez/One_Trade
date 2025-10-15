@echo off
echo 🧪 Ejecutando pruebas de RSI Strategy
echo =====================================

echo.
echo ⏳ Esperando 3 segundos para que el backend se inicie...
timeout /t 3 /nobreak > nul

echo.
echo 🔍 Probando endpoints...

REM Test Health
echo.
echo 1. Probando Health Endpoint...
curl -s http://127.0.0.1:8000/api/v1/health/ > nul
if %errorlevel% == 0 (
    echo ✅ Health endpoint funcionando
) else (
    echo ❌ Health endpoint no disponible
)

REM Test Strategies
echo.
echo 2. Probando Strategies Endpoint...
curl -s http://127.0.0.1:8000/api/v1/strategies/ > nul
if %errorlevel% == 0 (
    echo ✅ Strategies endpoint funcionando
) else (
    echo ❌ Strategies endpoint no disponible
)

echo.
echo 🎯 Pruebas completadas!
echo.
echo 💡 Para pruebas más detalladas, ejecuta:
echo    python quick_test.py
echo.
pause
