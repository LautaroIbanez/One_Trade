# Script para arrancar backend y frontend automáticamente

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Arrancando Backend y Frontend - One Trade Decision App" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "backend_simple.py")) {
    Write-Host "Error: No se encontro backend_simple.py" -ForegroundColor Red
    Write-Host "Asegurate de estar en el directorio decision_app" -ForegroundColor Red
    exit 1
}

# Verificar que el frontend existe
if (-not (Test-Path "frontend")) {
    Write-Host "Error: No se encontro la carpeta frontend" -ForegroundColor Red
    exit 1
}

Write-Host "Verificando dependencias..." -ForegroundColor Yellow

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

# Verificar dependencias del backend
$hasFastAPI = pip list | Select-String -Pattern "fastapi"
if (-not $hasFastAPI) {
    Write-Host "Instalando dependencias del backend..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "Iniciando servicios..." -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend: http://localhost:8000" -ForegroundColor Blue
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Blue
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Blue
Write-Host ""
Write-Host "Presiona Ctrl+C para detener ambos servicios" -ForegroundColor Yellow
Write-Host ""

# Función para limpiar procesos al salir
$cleanup = {
    Write-Host ""
    Write-Host "Deteniendo servicios..." -ForegroundColor Yellow
    Get-Process | Where-Object {$_.ProcessName -eq "node" -or $_.ProcessName -eq "python"} | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "Servicios detenidos" -ForegroundColor Green
}

# Registrar cleanup
Register-EngineEvent PowerShell.Exiting -Action $cleanup

try {
    # Arrancar backend en background
    Write-Host "Arrancando backend..." -ForegroundColor Blue
    $backendJob = Start-Process -FilePath "python" -ArgumentList "backend_simple.py" -WindowStyle Hidden -PassThru
    
    # Esperar un poco para que el backend arranque
    Start-Sleep -Seconds 3
    
    # Verificar que el backend está corriendo
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 5 -ErrorAction Stop
        Write-Host "Backend corriendo correctamente" -ForegroundColor Green
    } catch {
        Write-Host "Backend puede no estar listo todavia" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "Arrancando frontend..." -ForegroundColor Green
    
    # Cambiar al directorio frontend y arrancar
    Set-Location frontend
    
    # Verificar si node_modules existe
    if (-not (Test-Path "node_modules")) {
        Write-Host "Instalando dependencias del frontend..." -ForegroundColor Yellow
        npm install
    }
    
    # Arrancar frontend
    npm run dev
    
} finally {
    # Cleanup
    if ($backendJob) {
        $backendJob.Kill()
    }
    Set-Location ..
    & $cleanup
}
