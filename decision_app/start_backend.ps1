# Script simple para arrancar el backend

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Arrancando Backend - One Trade Decision App" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python no esta instalado" -ForegroundColor Red
    exit 1
}

# Verificar que las dependencias esten instaladas
Write-Host "Verificando dependencias..." -ForegroundColor Yellow
$hasFastAPI = pip list | Select-String -Pattern "fastapi"
if (-not $hasFastAPI) {
    Write-Host ""
    Write-Host "FastAPI no esta instalado. Instalando dependencias..." -ForegroundColor Yellow
    Write-Host ""
    pip install -r requirements.txt
}

Write-Host ""
Write-Host "Arrancando backend en http://localhost:8000" -ForegroundColor Green
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Presiona Ctrl+C para detener" -ForegroundColor Yellow
Write-Host ""

# Arrancar backend
python backend_simple.py

