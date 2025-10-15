# 📚 Índice de Documentación - One Trade Decision App

## 🎯 Documentación Principal

### 📖 [README_COMPLETO.md](./README_COMPLETO.md)
**Descripción:** README principal del proyecto  
**Para:** Todos los usuarios  
**Contiene:**
- Descripción general del proyecto
- Quick start
- Arquitectura
- API endpoints
- Configuración
- Troubleshooting
- Roadmap

---

### 🛠️ [GUIA_DESARROLLO.md](./GUIA_DESARROLLO.md)
**Descripción:** Guía completa para desarrolladores  
**Para:** Desarrolladores  
**Contiene:**
- Prerequisitos del sistema
- Configuración inicial paso a paso
- Arranque coordinado backend/frontend
- Verificación de CORS
- Pruebas de integración
- Solución de problemas comunes
- Scripts de desarrollo
- Documentación de endpoints
- Guía de seguridad
- Monitoreo y logging
- Procedimientos de despliegue

---

### ✅ [PLAN_TAREAS_IMPLEMENTADO.md](./PLAN_TAREAS_IMPLEMENTADO.md)
**Descripción:** Plan de tareas completo con estado de implementación  
**Para:** Project managers, desarrolladores  
**Contiene:**
- Resumen ejecutivo (9/10 tareas completadas - 90%)
- Detalles de cada tarea implementada
- Estadísticas de implementación
- Endpoints del backend
- Cómo ejecutar y verificar
- Soluciones a problemas conocidos
- Próximos pasos
- Lecciones aprendidas
- Logros

---

### 🔍 [VERIFICACION_BACKEND.md](./VERIFICACION_BACKEND.md)
**Descripción:** Checklist detallado para verificar el backend  
**Para:** DevOps, QA, desarrolladores  
**Contiene:**
- Quick check (test automatizado)
- Checklist detallado paso a paso
- Verificación de endpoints individuales
- Verificación de CORS headers
- Troubleshooting específico
- Criterios de éxito
- Métricas de salud
- Procedimiento de reinicio
- Log de verificación

---

## 📂 Archivos de Configuración

### ⚙️ [env.example](./env.example)
**Descripción:** Ejemplo de variables de entorno  
**Contiene:**
- Configuración de backend (host, port, URL)
- Configuración de frontend
- CORS configuration
- Database configuration (futuro)
- Redis configuration (futuro)
- RabbitMQ configuration (futuro)
- API configuration
- Logging configuration
- Security configuration
- External APIs (Binance)
- Trading configuration
- Mock mode settings

### 📦 [package.json](./package.json)
**Descripción:** Configuración de NPM y scripts  
**Contiene:**
- Scripts de desarrollo:
  - `npm run dev:backend` - Solo backend
  - `npm run dev:frontend` - Solo frontend
  - `npm run dev:full` - Ambos servicios
  - `npm run test:cors` - Tests de integración
  - `npm start` - Alias para dev:full

---

## 🐍 Archivos Python

### 🚀 [backend_simple.py](./backend_simple.py)
**Descripción:** Backend FastAPI completo  
**Líneas:** ~200  
**Características:**
- FastAPI application con CORS configurado
- Endpoints:
  - `GET /` - Root endpoint con info
  - `GET /health` - Health check
  - `GET /api/v1/enhanced-recommendations/supported-symbols`
  - `GET /api/v1/enhanced-recommendations/generate/{symbol}`
  - `GET /api/v1/enhanced-recommendations/batch/{symbols}`
  - `GET /api/v1/stats`
  - `OPTIONS /{path:path}` - CORS preflight
- Mock data para desarrollo
- Logging configurado
- Documentación interactiva (Swagger)

### 🧪 [test_cors.py](./test_cors.py)
**Descripción:** Tests de integración para CORS  
**Líneas:** ~150  
**Tests incluidos:**
1. `test_health_endpoint()` - Verifica health check
2. `test_cors_headers()` - Verifica headers CORS
3. `test_supported_symbols_endpoint()` - Verifica símbolos soportados
4. `test_generate_recommendation_endpoint()` - Verifica generación de recomendación
5. `test_batch_recommendations_endpoint()` - Verifica recomendaciones en lote
6. `test_stats_endpoint()` - Verifica estadísticas

---

## ⚛️ Archivos Frontend (TypeScript/React)

### 🎣 Hooks

#### [frontend/src/hooks/useApiWithRetry.ts](./frontend/src/hooks/useApiWithRetry.ts)
**Descripción:** Hook para requests con retry automático  
**Líneas:** ~100  
**Exports:**
- `useApiWithRetry<T>` - Hook principal con retry
- `createFetchFn<T>` - Helper para crear funciones de fetch
- `useApiGet<T>` - Hook simplificado para GET requests

**Configuración:**
- `maxRetries`: Número máximo de reintentos (default: 3)
- `retryDelay`: Delay inicial entre reintentos (default: 1000ms)
- `backoffMultiplier`: Multiplicador para backoff exponencial (default: 2)

#### [frontend/src/hooks/useMockData.ts](./frontend/src/hooks/useMockData.ts)
**Descripción:** Hook para datos mock en desarrollo  
**Líneas:** ~150  
**Datos mock:**
- Stats (activeRecommendations, totalPnL, winRate, maxDrawdown)
- Supported symbols (BTCUSDT, ETHUSDT, etc.)
- Recommendations con detalles completos

### 🧩 Componentes

#### [frontend/src/components/ErrorDisplay.tsx](./frontend/src/components/ErrorDisplay.tsx)
**Descripción:** Componentes para mostrar errores y estados  
**Líneas:** ~100  
**Componentes:**
- `ErrorDisplay` - Muestra errores con botón de reintentar
- `LoadingDisplay` - Muestra estado de carga
- `EmptyDisplay` - Muestra cuando no hay datos

#### [frontend/src/components/RealTimeStatsImproved.tsx](./frontend/src/components/RealTimeStatsImproved.tsx)
**Descripción:** Componente mejorado de estadísticas en tiempo real  
**Líneas:** ~120  
**Características:**
- Usa `useApiWithRetry` para requests
- Manejo de errores robusto
- Actualización automática cada 30 segundos
- Muestra: Active Recommendations, P&L, Win Rate, Max Drawdown

#### [frontend/src/components/EnhancedRecommendationsImproved.tsx](./frontend/src/components/EnhancedRecommendationsImproved.tsx)
**Descripción:** Componente mejorado de recomendaciones  
**Líneas:** ~200  
**Características:**
- Carga símbolos y recomendaciones
- Manejo de errores con retry
- Botón de refresh
- Muestra detalles: símbolo, recomendación, confianza, estrategia, indicadores

### ⚙️ Configuración

#### [frontend/src/router-config.ts](./frontend/src/router-config.ts)
**Descripción:** Configuración de React Router con future flags  
**Líneas:** ~40  
**Future flags:**
- `v7_startTransition: true`
- `v7_relativeSplatPath: true`

#### [frontend/public/vite.svg](./frontend/public/vite.svg)
**Descripción:** Logo de Vite  
**Formato:** SVG

---

## 🖥️ Scripts de Desarrollo

### 🐧 [start_dev.sh](./start_dev.sh)
**Descripción:** Script de inicio para Linux/Mac  
**Uso:**
```bash
chmod +x start_dev.sh
./start_dev.sh
```

### 🪟 [start_dev.ps1](./start_dev.ps1)
**Descripción:** Script de inicio para Windows PowerShell  
**Uso:**
```powershell
.\start_dev.ps1
```

---

## 🌐 Demo y Recursos

### 🎨 [demo.html](./demo.html)
**Descripción:** Demo standalone sin backend  
**Características:**
- HTML/CSS/JavaScript puro
- Tailwind CSS via CDN
- Font Awesome icons
- Mock data para demostración
- Responsive design

---

## 📊 Estadísticas de Documentación

### Total de Archivos Documentados: 20+

#### Por Categoría:
- 📖 Documentación: 4 archivos
- 🐍 Backend Python: 2 archivos
- ⚛️ Frontend TypeScript: 6 archivos
- ⚙️ Configuración: 2 archivos
- 🖥️ Scripts: 2 archivos
- 🌐 Demo: 1 archivo
- 📂 Otros: 3+ archivos

#### Por Líneas de Código:
- Backend Python: ~350 líneas
- Frontend TypeScript: ~570 líneas
- Tests: ~150 líneas
- Scripts: ~100 líneas
- Documentación: ~2,500+ líneas
- **Total:** ~3,670+ líneas

---

## 🗺️ Mapa de Navegación

### Para comenzar rápido:
1. Leer [README_COMPLETO.md](./README_COMPLETO.md)
2. Seguir Quick Start
3. Verificar con [VERIFICACION_BACKEND.md](./VERIFICACION_BACKEND.md)

### Para desarrollo:
1. Leer [GUIA_DESARROLLO.md](./GUIA_DESARROLLO.md)
2. Configurar entorno según [env.example](./env.example)
3. Ejecutar scripts de inicio
4. Ejecutar tests con [test_cors.py](./test_cors.py)

### Para troubleshooting:
1. Consultar sección de Troubleshooting en [README_COMPLETO.md](./README_COMPLETO.md)
2. Revisar [VERIFICACION_BACKEND.md](./VERIFICACION_BACKEND.md)
3. Consultar [GUIA_DESARROLLO.md](./GUIA_DESARROLLO.md) sección "Solución de Problemas"

### Para entender la implementación:
1. Leer [PLAN_TAREAS_IMPLEMENTADO.md](./PLAN_TAREAS_IMPLEMENTADO.md)
2. Revisar código fuente documentado
3. Consultar comentarios inline en archivos

---

## 🔄 Mantenimiento de Documentación

### Actualizar cuando:
- ✅ Se añaden nuevos endpoints
- ✅ Se cambia la configuración
- ✅ Se implementan nuevas características
- ✅ Se encuentran nuevos problemas y soluciones
- ✅ Se actualizan dependencias
- ✅ Se cambia la arquitectura

### Proceso de actualización:
1. Identificar documentos afectados
2. Actualizar contenido
3. Verificar links internos
4. Actualizar fecha de "Última actualización"
5. Actualizar este índice si es necesario

---

## 📞 Contacto

Para preguntas sobre la documentación:
- Issues: [GitHub Issues](link-to-issues)
- Email: docs@onetrade.com

---

**Última actualización:** 15 de Octubre de 2025  
**Versión:** 1.0.0  
**Mantenido por:** AI Assistant + Usuario
