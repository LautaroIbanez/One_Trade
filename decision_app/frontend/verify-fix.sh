#!/bin/bash
echo "======================================"
echo "Verificación de Corrección Frontend"
echo "======================================"
echo ""

echo "1. Verificando estructura de archivos..."
files=(
  "src/types/recommendations.ts"
  "src/lib/formatters.ts"
  "src/lib/__tests__/formatters.test.ts"
  "src/components/__tests__/EnhancedRecommendations.test.tsx"
  "docs/frontend-mocks.md"
  "README.md"
)

for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    echo "  ✓ $file"
  else
    echo "  ✗ $file (FALTA)"
  fi
done

echo ""
echo "2. Verificando modo mock..."
if grep -q "const MOCK_MODE = true" src/hooks/useMockData.ts; then
  echo "  ✓ Modo mock activado"
else
  echo "  ⚠ Modo mock desactivado (OK si tienes backend corriendo)"
fi

echo ""
echo "3. Ejecutando verificación de tipos..."
npm run type-check --silent

if [ $? -eq 0 ]; then
  echo "  ✓ Sin errores de TypeScript"
else
  echo "  ✗ Errores de TypeScript encontrados"
fi

echo ""
echo "4. Ejecutando tests..."
npm run test --silent --run

if [ $? -eq 0 ]; then
  echo "  ✓ Todos los tests pasaron"
else
  echo "  ✗ Algunos tests fallaron"
fi

echo ""
echo "======================================"
echo "Verificación Completa"
echo "======================================"
echo ""
echo "Para iniciar el frontend:"
echo "  npm run dev"
echo ""
echo "Para ver documentación de mocks:"
echo "  cat docs/frontend-mocks.md"

