# 📘 Guía de Desarrollo - One Trade Decision App

## 🎯 Índice

1. [Prerequisitos](#prerequisitos)
2. [Configuración Inicial](#configuración-inicial)
3. [Arranque Coordinado Backend/Frontend](#arranque-coordinado-backendfrontend)
4. [Verificación de CORS](#verificación-de-cors)
5. [Pruebas de Integración](#pruebas-de-integración)
6. [Solución de Problemas Comunes](#solución-de-problemas-comunes)
7. [Scripts de Desarrollo](#scripts-de-desarrollo)

---

## 📋 Prerequisitos

### Software Requerido
- **Python 3.11+** con pip y virtualenv
- **Node.js 18+** con npm
- **Git** para control de versiones
- **Docker Desktop** (opcional, para servicios completos)

### Verificar Instalaciones
```bash
# Verificar Python
python --version

# Verificar Node.js
node --version

# Verificar npm
npm --version

# Verificar Docker (opcional)
docker --version
```

---

## ⚙️ Configuración Inicial

### 1. Clonar el Repositorio
```bash
git clone <repository-url>
cd decision_app
```

### 2. Configurar Variables de Entorno

**Backend:**
```bash
# Copiar archivo de ejemplo
cp env.example .env

# Editar .env con tus valores
# Los valores por defecto funcionan para desarrollo local
```

**Frontend:**
```bash
cd frontend
cp .env.example .env

# Configurar URL del backend
VITE_API_URL=http://localhost:8000
```

### 3. Instalar Dependencias

**Backend:**
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install fastapi uvicorn pydantic requests
```

**Frontend:**
```bash
cd frontend
npm install
```

---

## 🚀 Arranque Coordinado Backend/Frontend

### Opción 1: Arranque Manual (Recomendado para Desarrollo)

**Terminal 1 - Backend:**
```bash
cd decision_app
python backend_simple.py
```

Deberías ver:
```
============================================================
🚀 One Trade Decision App - Simple Backend
============================================================

📡 API Documentation: http://localhost:8000/docs
🔗 API Base URL: http://localhost:8000
📊 Health Check: http://localhost:8000/health
📋 Supported Symbols: BTCUSDT, ETHUSDT, ADAUSDT, SOLUSDT, BNBUSDT, XRPUSDT

🌐 CORS Enabled for:
   - http://localhost:3000 (Frontend)
   - http://localhost:5173 (Vite)

⚡ Press Ctrl+C to stop the server
============================================================
```

**Terminal 2 - Frontend:**
```bash
cd decision_app/frontend
npm run dev
```

Deberías ver:
```
  VITE v4.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

### Opción 2: Arranque Automático (Futuro)

```bash
# Instalar concurrently (primera vez)
npm install -g concurrently

# Arrancar ambos servicios
npm run dev:full
```

---

## 🔍 Verificación de CORS

### 1. Verificar Health Check del Backend
```bash
curl http://localhost:8000/health
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-15T...",
  "cors_enabled": true,
  "endpoints_available": true
}
```

### 2. Verificar Headers CORS
```bash
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     http://localhost:8000/api/v1/enhanced-recommendations/supported-symbols
```

**Headers esperados en la respuesta:**
- `Access-Control-Allow-Origin: http://localhost:3000`
- `Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS`
- `Access-Control-Allow-Credentials: true`

### 3. Ejecutar Tests de Integración
```bash
cd decision_app
python test_cors.py
```

**Salida esperada:**
```
============================================================
🧪 One Trade Decision App - CORS Integration Tests
============================================================
✅ Health endpoint working correctly
✅ CORS headers configured correctly
✅ Supported symbols: ['BTCUSDT', 'ETHUSDT', ...]
✅ Recommendation generated: BUY (confidence: 0.75)
✅ Batch recommendations generated for 3 symbols
✅ Stats retrieved: 6 active recommendations

============================================================
📊 Test Results Summary
============================================================
✅ Passed: 6/6
🎉 All tests passed! CORS is working correctly.
```

---

## 🧪 Pruebas de Integración

### Pruebas Backend
```bash
cd decision_app
python test_cors.py
```

### Pruebas Frontend (Futuro)
```bash
cd frontend
npm run test
```

### Pruebas E2E (Futuro)
```bash
npm run test:e2e
```

---

## 🛠️ Solución de Problemas Comunes

### Problema 1: Error CORS en el Frontend

**Síntomas:**
- `TypeError: Failed to fetch`
- `No 'Access-Control-Allow-Origin' header is present`

**Solución:**
1. Verificar que el backend está corriendo: `curl http://localhost:8000/health`
2. Verificar CORS headers: `python test_cors.py`
3. Verificar que el origen del frontend está en la lista de `ALLOWED_ORIGINS`
4. Reiniciar ambos servicios

### Problema 2: Backend no Responde

**Síntomas:**
- `Connection refused`
- `ECONNREFUSED`

**Solución:**
1. Verificar que el backend está corriendo: `netstat -an | findstr 8000`
2. Verificar que no hay otro proceso usando el puerto 8000
3. Revisar logs del backend para errores
4. Probar con otro puerto si es necesario

### Problema 3: Puerto 8000 Bloqueado (Windows)

**Síntomas:**
- Backend se cierra inmediatamente
- No hay proceso escuchando en puerto 8000

**Solución:**
1. Verificar procesos que usan el puerto:
   ```powershell
   netstat -ano | findstr :8000
   ```
2. Si hay un proceso, identificarlo:
   ```powershell
   tasklist /FI "PID eq <PID>"
   ```
3. Cambiar el puerto en `backend_simple.py`:
   ```python
   uvicorn.run(app, host="127.0.0.1", port=8001)
   ```
4. Actualizar frontend para usar el nuevo puerto

### Problema 4: Recursos Estáticos Ausentes (vite.svg)

**Síntomas:**
- `404 Not Found` para `/vite.svg`

**Solución:**
1. Crear carpeta `public/` en frontend
2. Añadir `vite.svg` en `public/vite.svg`
3. Reiniciar Vite dev server

### Problema 5: Warnings de React Router v7

**Síntomas:**
- Warnings sobre `v7_startTransition` y `v7_relativeSplatPath`

**Solución:**
Los warnings son informativos. Para eliminarlos:
```typescript
// En tu configuración de router
const router = createBrowserRouter(routes, {
  future: {
    v7_startTransition: true,
    v7_relativeSplatPath: true
  }
});
```

---

## 📜 Scripts de Desarrollo

### Backend Scripts

**Arrancar servidor de desarrollo:**
```bash
python backend_simple.py
```

**Ejecutar tests:**
```bash
python test_cors.py
```

**Ver documentación API:**
```bash
# Arrancar backend y abrir en navegador
open http://localhost:8000/docs
```

### Frontend Scripts

**Arrancar servidor de desarrollo:**
```bash
npm run dev
```

**Build para producción:**
```bash
npm run build
```

**Preview build de producción:**
```bash
npm run preview
```

**Ejecutar tests:**
```bash
npm run test
```

**Linting:**
```bash
npm run lint
```

**Formatear código:**
```bash
npm run format
```

---

## 📊 Endpoints del Backend

### Health Check
```
GET /health
Response: { "status": "healthy", ... }
```

### Supported Symbols
```
GET /api/v1/enhanced-recommendations/supported-symbols
Response: ["BTCUSDT", "ETHUSDT", ...]
```

### Generate Recommendation
```
GET /api/v1/enhanced-recommendations/generate/{symbol}?timeframe=1d&days=30
Response: {
  "symbol": "BTCUSDT",
  "recommendation": "BUY",
  "confidence": 0.75,
  "timestamp": "...",
  "details": {...}
}
```

### Batch Recommendations
```
GET /api/v1/enhanced-recommendations/batch/BTCUSDT,ETHUSDT?timeframe=1d&days=30
Response: {
  "BTCUSDT": {...},
  "ETHUSDT": {...}
}
```

### Stats
```
GET /api/v1/stats
Response: {
  "activeRecommendations": 6,
  "totalPnL": 15.2,
  "winRate": 68.0,
  "maxDrawdown": -8.0,
  "lastUpdate": "..."
}
```

---

## 🔐 Seguridad

### CORS Configuration
- Por defecto, solo se permiten orígenes específicos
- En producción, configurar `ALLOWED_ORIGINS` con dominios específicos
- Nunca usar `*` en producción

### Variables de Entorno
- **Nunca** commitear archivos `.env` con credenciales reales
- Usar `.env.example` para documentar variables necesarias
- En producción, usar variables de entorno del sistema o secrets manager

---

## 📈 Monitoreo y Logging

### Backend Logging
El backend registra:
- Requests entrantes (método, path, origen)
- Errores y excepciones
- Tiempo de respuesta
- Headers CORS aplicados

### Frontend Error Handling
El frontend debe:
- Mostrar mensajes amigables al usuario
- Registrar errores en consola (desarrollo)
- Enviar errores a servicio de monitoreo (producción)
- Implementar retry logic para requests fallidos

---

## 🚢 Despliegue

### Backend
```bash
# Build Docker image
docker build -t onetrade-backend -f backend/Dockerfile .

# Run container
docker run -p 8000:8000 --env-file .env onetrade-backend
```

### Frontend
```bash
# Build para producción
npm run build

# Servir estáticos (ejemplo con nginx)
docker build -t onetrade-frontend -f frontend/Dockerfile .
docker run -p 3000:80 onetrade-frontend
```

---

## 📚 Recursos Adicionales

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vite Documentation](https://vitejs.dev/)
- [React Documentation](https://react.dev/)
- [CORS Explained](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)

---

## 🆘 Soporte

Si encuentras problemas:
1. Revisar esta guía
2. Verificar logs del backend y frontend
3. Ejecutar `python test_cors.py`
4. Consultar la documentación de APIs en `/docs`
5. Reportar issue con logs completos

---

**Última actualización:** 2025-10-15
**Versión:** 1.0.0
