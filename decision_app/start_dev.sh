#!/bin/bash
# Script para arrancar backend y frontend en desarrollo

set -e

echo "============================================================"
echo "🚀 One Trade Decision App - Development Startup"
echo "============================================================"
echo ""

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar si está instalado concurrently
if ! command -v concurrently &> /dev/null; then
    echo -e "${YELLOW}⚠️  'concurrently' no está instalado${NC}"
    echo "Instalando concurrently..."
    npm install -g concurrently
fi

# Verificar Python
if ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python no está instalado${NC}"
    exit 1
fi

# Verificar Node
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js no está instalado${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisitos verificados${NC}"
echo ""

# Arrancar servicios
echo -e "${BLUE}🔧 Arrancando servicios...${NC}"
echo ""

concurrently \
    --names "BACKEND,FRONTEND" \
    --prefix-colors "blue,green" \
    "python backend_simple.py" \
    "cd frontend && npm run dev"
