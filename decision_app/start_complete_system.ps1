#!/usr/bin/env pwsh
# Script para iniciar el sistema completo One Trade Decision App

Write-Host "🚀 Iniciando Sistema Completo One Trade Decision App" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green

Write-Host ""
Write-Host "Este script iniciará:" -ForegroundColor Yellow
Write-Host "1. Backend (FastAPI) en puerto 8000"
Write-Host "2. Frontend (React) en puerto 3000"
Write-Host "3. Ejecutará tests completos del sistema"
Write-Host ""

# Obtener el directorio del script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Verificar que estamos en el directorio correcto
if (-not (Test-Path (Join-Path $scriptDir "backend"))) {
    Write-Host "❌ Error: No se encontró el directorio 'backend'" -ForegroundColor Red
    Write-Host "   Asegúrate de ejecutar este script desde el directorio decision_app" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path (Join-Path $scriptDir "frontend"))) {
    Write-Host "❌ Error: No se encontró el directorio 'frontend'" -ForegroundColor Red
    Write-Host "   Asegúrate de ejecutar este script desde el directorio decision_app" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Directorios encontrados correctamente" -ForegroundColor Green

# Iniciar Backend
Write-Host ""
Write-Host "🔧 Iniciando Backend..." -ForegroundColor Blue
$backendPath = Join-Path $scriptDir "backend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; Write-Host 'Backend iniciando...' -ForegroundColor Green; venv\Scripts\Activate.ps1; python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000"

# Esperar un poco para que el backend se inicie
Write-Host "⏳ Esperando que el backend se inicie..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Iniciar Frontend
Write-Host "🌐 Iniciando Frontend..." -ForegroundColor Blue
$frontendPath = Join-Path $scriptDir "frontend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; Write-Host 'Frontend iniciando...' -ForegroundColor Green; npm run dev"

# Esperar un poco para que el frontend se inicie
Write-Host "⏳ Esperando que el frontend se inicie..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

# Ejecutar tests completos
Write-Host ""
Write-Host "🧪 Ejecutando tests completos del sistema..." -ForegroundColor Cyan
Write-Host "   Esto puede tomar unos segundos..." -ForegroundColor Yellow

try {
    $testScript = Join-Path $scriptDir "test_complete_system.py"
    if (Test-Path $testScript) {
        python $testScript
    } else {
        Write-Host "⚠️  Script de test no encontrado: $testScript" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Error ejecutando tests: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 Sistema iniciado exitosamente!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 URLs disponibles:" -ForegroundColor Yellow
Write-Host "   • Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   • Backend API: http://127.0.0.1:8000" -ForegroundColor White
Write-Host "   • API Docs: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "💡 Funcionalidades disponibles:" -ForegroundColor Yellow
Write-Host "   • Dashboard con recomendaciones en tiempo real" -ForegroundColor White
Write-Host "   • Configuración de pesos de estrategias" -ForegroundColor White
Write-Host "   • Gestión de símbolos soportados" -ForegroundColor White
Write-Host "   • Análisis multi-símbolo" -ForegroundColor White
Write-Host "   • Recomendaciones con datos reales de Binance" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Para detener el sistema:" -ForegroundColor Yellow
Write-Host "   • Cierra las ventanas de terminal que se abrieron" -ForegroundColor White
Write-Host "   • O presiona Ctrl+C en cada ventana" -ForegroundColor White
Write-Host ""
Write-Host "Presiona cualquier tecla para cerrar esta ventana..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
