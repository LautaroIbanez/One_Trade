#!/usr/bin/env pwsh
# Script para iniciar One Trade Decision App

Write-Host "Iniciando One Trade Decision App" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

Write-Host ""
Write-Host "Instrucciones:" -ForegroundColor Yellow
Write-Host "1. Ejecuta este script"
Write-Host "2. Se abrirán 2 ventanas de terminal"
Write-Host "3. Espera a que ambos servicios se inicien"
Write-Host "4. Ve a http://localhost:3000 para el frontend"
Write-Host "5. Ve a http://127.0.0.1:8000/docs para la API"
Write-Host ""

Write-Host "Iniciando servicios..." -ForegroundColor Cyan
Write-Host ""

# Obtener el directorio del script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Iniciar Backend
Write-Host "Iniciando Backend..." -ForegroundColor Blue
$backendPath = Join-Path $scriptDir "backend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; venv\Scripts\Activate.ps1; python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000"

# Esperar un poco
Start-Sleep -Seconds 3

# Iniciar Frontend
Write-Host "Iniciando Frontend..." -ForegroundColor Blue
$frontendPath = Join-Path $scriptDir "frontend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; npm run dev"

Write-Host ""
Write-Host "Servicios iniciados!" -ForegroundColor Green
Write-Host ""
Write-Host "URLs disponibles:" -ForegroundColor Yellow
Write-Host "   • Frontend: http://localhost:3000"
Write-Host "   • Backend API: http://127.0.0.1:8000"
Write-Host "   • API Docs: http://127.0.0.1:8000/docs"
Write-Host ""
Write-Host "Presiona cualquier tecla para cerrar esta ventana..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
