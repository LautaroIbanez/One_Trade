# Quick Start Guide - Backend + Frontend

Guía rápida para iniciar el sistema completo de Trading Decision App.

## ⚠️ Corrección Importante

El comando uvicorn en la documentación anterior era **INCORRECTO**. Aquí está el comando correcto:

### ❌ Incorrecto (NO USAR)
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### ✅ Correcto (USAR ESTE)
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🚀 Inicio Rápido

### Terminal 1: Backend

```powershell
# Navegar al directorio backend
cd C:\Users\lauta\OneDrive\Desktop\Trading\One_Trade\decision_app\backend

# Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# Instalar dependencias (solo primera vez o si hay cambios)
pip install -r requirements.txt

# INICIAR BACKEND (comando correcto)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Verificar**: Deberías ver `Uvicorn running on http://0.0.0.0:8000`

### Terminal 2: Frontend

```powershell
# Navegar al directorio frontend (en otra terminal)
cd C:\Users\lauta\OneDrive\Desktop\Trading\One_Trade\decision_app\frontend

# Crear archivo de configuración (solo primera vez)
echo "VITE_API_URL=http://localhost:8000/api/v1" > .env.local

# Instalar dependencias (solo primera vez o si hay cambios)
npm install

# Iniciar frontend
npm run dev
```

**Verificar**: Deberías ver `Local: http://localhost:5173`

## ✅ Verificación del Sistema

### 1. Verificar Backend

Abre en tu navegador:
- **Health Check**: http://localhost:8000/health
- **Documentación API**: http://localhost:8000/docs
- **Test CORS**: http://localhost:8000/test-cors

Deberías ver respuestas JSON exitosas.

### 2. Verificar Frontend

Abre en tu navegador:
- **Aplicación**: http://localhost:5173

Deberías ver la interfaz de la aplicación cargando correctamente.

### 3. Verificar Integración

1. En el frontend, navega a la página de **Backtests**
2. Deberías ver que los dropdowns de Symbol y Strategy se cargan con datos reales
3. Ejecuta un backtest y verifica que funciona sin errores

## 🔧 Solución de Problemas

### Error: "Could not import module 'app.main'"

**Causa**: Comando uvicorn incorrecto
**Solución**: Usar `uvicorn main:app` en lugar de `uvicorn app.main:app`

### Error: "Failed to fetch" en el frontend

**Causa**: Backend no está corriendo o URL incorrecta
**Solución**: 
1. Verificar que el backend esté corriendo en el puerto 8000
2. Verificar que el archivo `.env.local` tenga `VITE_API_URL=http://localhost:8000/api/v1`

### Error: "No symbols available"

**Causa**: Backend no puede acceder a los datos
**Solución**: Verificar que la base de datos esté configurada correctamente

### Puerto ya en uso

**Backend (8000)**:
```powershell
# Encontrar proceso usando el puerto 8000
netstat -ano | findstr :8000

# Matar el proceso (reemplazar PID con el número encontrado)
taskkill /PID <PID> /F
```

**Frontend (5173)**:
```powershell
# Encontrar proceso usando el puerto 5173
netstat -ano | findstr :5173

# Matar el proceso
taskkill /PID <PID> /F
```

## 📋 Checklist de Inicio

Antes de empezar a desarrollar, verifica:

- [ ] Entorno virtual de Python activado
- [ ] Backend corriendo en puerto 8000
- [ ] Frontend corriendo en puerto 5173
- [ ] Archivo `.env.local` creado en frontend
- [ ] Health check del backend responde OK
- [ ] Frontend carga sin errores en consola
- [ ] Integración funciona (backtests se ejecutan)

## 🎯 Endpoints Principales del Backend

Una vez el backend esté corriendo, puedes acceder a:

### Health & Docs
- `GET /health` - Health check
- `GET /docs` - Documentación Swagger
- `GET /redoc` - Documentación ReDoc

### Backtests
- `GET /api/v1/backtests/strategies` - Lista de estrategias disponibles
- `GET /api/v1/backtests/symbols` - Lista de símbolos disponibles
- `GET /api/v1/backtests/quick-test/{symbol}` - Ejecutar backtest rápido
- `GET /api/v1/backtests/compare/{symbol}` - Comparar estrategias

### Recomendaciones
- `GET /api/v1/enhanced-recommendations/generate/{symbol}` - Generar recomendación
- `GET /api/v1/enhanced-recommendations/supported-symbols` - Símbolos soportados

## 📝 Notas

- **Backend**: Usa FastAPI con recarga automática (flag `--reload`)
- **Frontend**: Usa Vite con recarga automática (HMR)
- **Base de Datos**: SQLite local (`onetrade.db`)
- **CORS**: Configurado para permitir localhost:5173

## 🔄 Reiniciar el Sistema

Si algo no funciona, prueba reiniciar:

1. **Detener todo**: Ctrl+C en ambas terminales
2. **Limpiar puertos** (ver sección "Puerto ya en uso")
3. **Reiniciar backend** primero
4. **Reiniciar frontend** después
5. **Recargar navegador** con Ctrl+Shift+R

## 📚 Documentación Adicional

- **Frontend**: `decision_app/frontend/README.md`
- **QA Backtests**: `decision_app/frontend/docs/QA_BACKTEST_SECTION.md`
- **Migración API**: `decision_app/BACKTEST_REAL_DATA_MIGRATION_SUMMARY.md`
- **Índice General**: `decision_app/IMPLEMENTATION_INDEX.md`

---

**Última Actualización**: 2025-10-15
**Versión del Sistema**: 2.0 (Post-migración a API real)


