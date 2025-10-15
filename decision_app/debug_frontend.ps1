# Script para diagnosticar problemas del frontend

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Diagnostico Frontend - One Trade Decision App" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar directorio
Write-Host "Verificando directorio actual..." -ForegroundColor Yellow
Write-Host "Directorio: $(Get-Location)" -ForegroundColor White

# Verificar si estamos en el directorio correcto
if (-not (Test-Path "frontend")) {
    Write-Host "ERROR: No se encontro la carpeta frontend" -ForegroundColor Red
    Write-Host "Asegurate de estar en decision_app/" -ForegroundColor Red
    exit 1
}

Set-Location frontend

Write-Host ""
Write-Host "Verificando archivos del frontend..." -ForegroundColor Yellow

# Verificar archivos principales
$requiredFiles = @("package.json", "index.html", "src/main.tsx", "src/App.tsx")
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file - FALTA" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Verificando Node.js..." -ForegroundColor Yellow
if (Get-Command node -ErrorAction SilentlyContinue) {
    $nodeVersion = node --version
    Write-Host "  ✅ Node.js: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "  ❌ Node.js no instalado" -ForegroundColor Red
    exit 1
}

if (Get-Command npm -ErrorAction SilentlyContinue) {
    $npmVersion = npm --version
    Write-Host "  ✅ npm: $npmVersion" -ForegroundColor Green
} else {
    Write-Host "  ❌ npm no instalado" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Verificando dependencias..." -ForegroundColor Yellow
if (Test-Path "node_modules") {
    Write-Host "  ✅ node_modules existe" -ForegroundColor Green
} else {
    Write-Host "  ❌ node_modules NO existe - Necesita instalacion" -ForegroundColor Red
    Write-Host ""
    Write-Host "Instalando dependencias..." -ForegroundColor Yellow
    npm install
}

Write-Host ""
Write-Host "Verificando package.json..." -ForegroundColor Yellow
$packageJson = Get-Content "package.json" | ConvertFrom-Json
Write-Host "  Nombre: $($packageJson.name)" -ForegroundColor White
Write-Host "  Version: $($packageJson.version)" -ForegroundColor White

Write-Host ""
Write-Host "Intentando arrancar el frontend..." -ForegroundColor Yellow
Write-Host "Presiona Ctrl+C para detener" -ForegroundColor Yellow
Write-Host ""

npm run dev
