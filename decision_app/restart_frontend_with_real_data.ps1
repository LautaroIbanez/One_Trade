#!/usr/bin/env pwsh
# Script para reiniciar el frontend con datos reales

Write-Host "🔄 Reiniciando Frontend con Datos Reales" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green

# Obtener el directorio del script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$frontendPath = Join-Path $scriptDir "frontend"

Write-Host ""
Write-Host "📋 Cambios implementados:" -ForegroundColor Yellow
Write-Host "   ✅ Dashboard: Estadísticas en tiempo real" -ForegroundColor White
Write-Host "   ✅ Recommendations: Datos reales de Binance" -ForegroundColor White
Write-Host "   ✅ Eliminados todos los datos dummy" -ForegroundColor White
Write-Host "   ✅ Componentes con datos dinámicos" -ForegroundColor White
Write-Host ""

# Detener procesos existentes
Write-Host "🛑 Deteniendo procesos de frontend existentes..." -ForegroundColor Yellow
Get-Process | Where-Object { $_.Path -like "*npm*" -and $_.CommandLine -like "*run dev*" } | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process | Where-Object { $_.Path -like "*node*" -and $_.CommandLine -like "*vite*" } | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Iniciar Frontend
Write-Host "🚀 Iniciando Frontend con datos reales..." -ForegroundColor Blue
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; Write-Host 'Frontend iniciando con datos reales...' -ForegroundColor Green; npm run dev"

Write-Host ""
Write-Host "✅ Frontend reiniciado exitosamente!" -ForegroundColor Green
Write-Host ""
Write-Host "🎯 Nuevas funcionalidades:" -ForegroundColor Yellow
Write-Host "   • Dashboard: Estadísticas calculadas en tiempo real" -ForegroundColor White
Write-Host "   • Recommendations: Precios y señales reales de Binance" -ForegroundColor White
Write-Host "   • Multi-Symbol: Análisis comparativo dinámico" -ForegroundColor White
Write-Host "   • Settings: Configuración de estrategias y símbolos" -ForegroundColor White
Write-Host ""
Write-Host "🌐 URLs disponibles:" -ForegroundColor Yellow
Write-Host "   • Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   • Backend API: http://127.0.0.1:8000" -ForegroundColor White
Write-Host "   • API Docs: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "💡 Asegúrate de que el backend esté corriendo para ver los datos reales" -ForegroundColor Cyan
Write-Host ""
Write-Host "Presiona cualquier tecla para cerrar esta ventana..." -ForegroundColor Cyan
Read-Host "Presiona Enter para continuar"
