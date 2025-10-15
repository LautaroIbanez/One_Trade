# Script para arrancar solo el frontend

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Arrancando Frontend - One Trade Decision App" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Node
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "Node.js no esta instalado" -ForegroundColor Red
    exit 1
}

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "frontend")) {
    Write-Host "Error: No se encontro la carpeta frontend" -ForegroundColor Red
    Write-Host "Asegurate de estar en el directorio decision_app" -ForegroundColor Red
    exit 1
}

# Cambiar al directorio frontend
Set-Location frontend

Write-Host "Verificando dependencias del frontend..." -ForegroundColor Yellow

# Verificar si node_modules existe
if (-not (Test-Path "node_modules")) {
    Write-Host "Instalando dependencias del frontend..." -ForegroundColor Yellow
    Write-Host "Esto puede tomar unos minutos..." -ForegroundColor Yellow
    Write-Host ""
    npm install
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "Arrancando frontend..." -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Blue
Write-Host "Backend: http://localhost:8000 (asegurate de que este corriendo)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Presiona Ctrl+C para detener" -ForegroundColor Yellow
Write-Host ""

# Arrancar frontend
npm run dev
