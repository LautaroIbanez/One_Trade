Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Verificación de Corrección Frontend" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. Verificando estructura de archivos..." -ForegroundColor Yellow
$files = @(
  "src\types\recommendations.ts",
  "src\lib\formatters.ts",
  "src\lib\__tests__\formatters.test.ts",
  "src\components\__tests__\EnhancedRecommendations.test.tsx",
  "docs\frontend-mocks.md",
  "README.md"
)

foreach ($file in $files) {
  if (Test-Path $file) {
    Write-Host "  ✓ $file" -ForegroundColor Green
  } else {
    Write-Host "  ✗ $file (FALTA)" -ForegroundColor Red
  }
}

Write-Host ""
Write-Host "2. Verificando modo mock..." -ForegroundColor Yellow
$mockModeContent = Get-Content "src\hooks\useMockData.ts" -Raw
if ($mockModeContent -match "const MOCK_MODE = true") {
  Write-Host "  ✓ Modo mock activado" -ForegroundColor Green
} else {
  Write-Host "  ⚠ Modo mock desactivado (OK si tienes backend corriendo)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "3. Verificando que npm esté instalado..." -ForegroundColor Yellow
if (Get-Command npm -ErrorAction SilentlyContinue) {
  Write-Host "  ✓ npm disponible" -ForegroundColor Green
  
  Write-Host ""
  Write-Host "4. Instalando dependencias (si es necesario)..." -ForegroundColor Yellow
  npm install --silent
  
  Write-Host ""
  Write-Host "5. Ejecutando tests..." -ForegroundColor Yellow
  npm run test -- --run --silent 2>$null
  
  if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Tests ejecutados" -ForegroundColor Green
  } else {
    Write-Host "  ⚠ Revisar output de tests arriba" -ForegroundColor Yellow
  }
} else {
  Write-Host "  ✗ npm no encontrado. Instalar Node.js primero." -ForegroundColor Red
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Verificación Completa" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para iniciar el frontend:" -ForegroundColor White
Write-Host "  npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "Para ver documentación de mocks:" -ForegroundColor White
Write-Host "  Get-Content docs\frontend-mocks.md" -ForegroundColor Gray

