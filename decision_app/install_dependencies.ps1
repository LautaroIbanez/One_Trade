# Script para instalar todas las dependencias necesarias
# One Trade Decision App

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Instalando Dependencias - One Trade Decision App" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que estamos en un entorno virtual
if (-not $env:VIRTUAL_ENV) {
    Write-Host "No estas en un entorno virtual" -ForegroundColor Yellow
    Write-Host "   Activando .venv..." -ForegroundColor Yellow
    Write-Host ""
    
    # Intentar activar .venv del directorio padre
    $venvPath = "..\..\.venv\Scripts\Activate.ps1"
    if (Test-Path $venvPath) {
        & $venvPath
    } else {
        Write-Host "No se encontro el entorno virtual .venv" -ForegroundColor Red
        Write-Host "   Por favor, crea uno con: python -m venv .venv" -ForegroundColor Red
        exit 1
    }
}

Write-Host "Entorno virtual activo: $env:VIRTUAL_ENV" -ForegroundColor Green
Write-Host ""

# Instalar dependencias del backend
Write-Host "Instalando dependencias del backend..." -ForegroundColor Blue
Write-Host ""

$backendDeps = @(
    "fastapi",
    "uvicorn[standard]",
    "pydantic",
    "requests",
    "python-multipart"
)

foreach ($dep in $backendDeps) {
    Write-Host "   Instalando $dep..." -ForegroundColor White
    pip install $dep --quiet
}

Write-Host ""
Write-Host "Dependencias del backend instaladas" -ForegroundColor Green
Write-Host ""

# Verificar instalacion
Write-Host "Verificando instalacion..." -ForegroundColor Blue
Write-Host ""

$installed = pip list | Select-String -Pattern "fastapi|uvicorn|pydantic|requests"
if ($installed) {
    Write-Host "Paquetes instalados correctamente:" -ForegroundColor Green
    pip list | Select-String -Pattern "fastapi|uvicorn|pydantic|requests"
} else {
    Write-Host "Error en la instalacion" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Instalacion completada!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ahora puedes ejecutar:" -ForegroundColor White
Write-Host "  python backend_simple.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "O usar el script de inicio:" -ForegroundColor White
Write-Host '  .\start_dev.ps1' -ForegroundColor Yellow
Write-Host ""
