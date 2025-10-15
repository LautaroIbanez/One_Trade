# Script para arrancar frontend simplificado

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Arrancando Frontend Simplificado" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "frontend")) {
    Write-Host "ERROR: No se encontro la carpeta frontend" -ForegroundColor Red
    Write-Host "Asegurate de estar en decision_app/" -ForegroundColor Red
    exit 1
}

Set-Location frontend

Write-Host "Verificando Node.js..." -ForegroundColor Yellow
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Node.js no esta instalado" -ForegroundColor Red
    exit 1
}

Write-Host "Node.js: $(node --version)" -ForegroundColor Green
Write-Host "npm: $(npm --version)" -ForegroundColor Green

Write-Host ""
Write-Host "Instalando dependencias minimas..." -ForegroundColor Yellow
npm install --silent

Write-Host ""
Write-Host "Creando version simplificada..." -ForegroundColor Yellow

# Crear copia de respaldo del index.html original
if (Test-Path "index.html") {
    Copy-Item "index.html" "index-backup.html" -Force
    Write-Host "  Respaldo creado: index-backup.html" -ForegroundColor Green
}

# Crear copia de respaldo del main.tsx original
if (Test-Path "src/main.tsx") {
    Copy-Item "src/main.tsx" "src/main-backup.tsx" -Force
    Write-Host "  Respaldo creado: src/main-backup.tsx" -ForegroundColor Green
}

# Usar versiones simplificadas
Copy-Item "index-simple.html" "index.html" -Force
Copy-Item "src/main-simple.tsx" "src/main.tsx" -Force

Write-Host "  Usando versiones simplificadas" -ForegroundColor Green

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "Arrancando frontend simplificado..." -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "URL: http://localhost:3000" -ForegroundColor Blue
Write-Host "Presiona Ctrl+C para detener" -ForegroundColor Yellow
Write-Host ""

# Arrancar frontend
npm run dev
