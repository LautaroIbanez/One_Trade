# Script de PowerShell para arrancar backend y frontend en desarrollo

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "One Trade Decision App - Development Startup" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python no esta instalado" -ForegroundColor Red
    exit 1
}

# Verificar Node
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "Node.js no esta instalado" -ForegroundColor Red
    exit 1
}

Write-Host "Prerequisitos verificados" -ForegroundColor Green
Write-Host ""

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "URLs Disponibles:" -ForegroundColor Cyan
Write-Host "   Backend API:  http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs:     http://localhost:8000/docs" -ForegroundColor White
Write-Host "   Frontend:     http://localhost:3000" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "NOTA: Ejecuta el backend y frontend en terminales separadas" -ForegroundColor Yellow
Write-Host ""
Write-Host "Terminal 1 - Backend:" -ForegroundColor Blue
Write-Host "  python backend_simple.py" -ForegroundColor White
Write-Host ""
Write-Host "Terminal 2 - Frontend:" -ForegroundColor Green
Write-Host "  cd frontend" -ForegroundColor White
Write-Host "  npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "O ejecuta solo el backend ahora:" -ForegroundColor Yellow
Write-Host "  python backend_simple.py" -ForegroundColor White
Write-Host ""

# Preguntar si quiere arrancar el backend ahora
$response = Read-Host "Arrancar el backend ahora? (s/n)"
if ($response -eq "s" -or $response -eq "S" -or $response -eq "y" -or $response -eq "Y") {
    Write-Host ""
    Write-Host "Arrancando backend..." -ForegroundColor Blue
    Write-Host "Presiona Ctrl+C para detener" -ForegroundColor Yellow
    Write-Host ""
    python backend_simple.py
}
