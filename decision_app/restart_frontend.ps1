#!/usr/bin/env pwsh
# Script para reiniciar solo el frontend

Write-Host "Reiniciando Frontend One Trade Decision App" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

Write-Host ""
Write-Host "Deteniendo procesos del frontend..." -ForegroundColor Yellow

# Detener procesos de Node.js que puedan estar corriendo
Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "Iniciando frontend..." -ForegroundColor Cyan

# Obtener el directorio del script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$frontendPath = Join-Path $scriptDir "frontend"

# Iniciar Frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; npm run dev"

Write-Host ""
Write-Host "Frontend reiniciado!" -ForegroundColor Green
Write-Host ""
Write-Host "URLs disponibles:" -ForegroundColor Yellow
Write-Host "   • Frontend: http://localhost:3000"
Write-Host "   • Backend API: http://127.0.0.1:8000"
Write-Host "   • API Docs: http://127.0.0.1:8000/docs"
Write-Host ""
Write-Host "Presiona cualquier tecla para cerrar esta ventana..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
