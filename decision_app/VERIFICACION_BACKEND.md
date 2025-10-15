# 🔍 Verificación del Backend - Checklist

Este documento proporciona pasos específicos para verificar que el backend está funcionando correctamente.

## ⚡ Quick Check

Ejecuta este comando para una verificación rápida:

```bash
python test_cors.py
```

Si todos los tests pasan (✅ 6/6), el backend está funcionando correctamente.

---

## 📋 Checklist Detallado

### 1. ✅ Verificar que Python está instalado

```bash
python --version
# Debería mostrar: Python 3.11.x o superior
```

### 2. ✅ Verificar dependencias instaladas

```bash
pip list | grep fastapi
pip list | grep uvicorn
pip list | grep pydantic
pip list | grep requests
```

Si falta alguna:
```bash
pip install fastapi uvicorn pydantic requests
```

### 3. ✅ Iniciar el Backend

```bash
cd decision_app
python backend_simple.py
```

**Salida esperada:**
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

INFO:     Started server process [PID]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### 4. ✅ Verificar que el servidor está escuchando

**Windows PowerShell:**
```powershell
netstat -an | findstr :8000
```

**Linux/Mac:**
```bash
netstat -an | grep :8000
# o
lsof -i :8000
```

**Salida esperada:**
```
TCP    127.0.0.1:8000    0.0.0.0:0    LISTENING
```

### 5. ✅ Test Manual de Endpoints

#### Health Check
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

#### Supported Symbols
```bash
curl http://localhost:8000/api/v1/enhanced-recommendations/supported-symbols
```

**Respuesta esperada:**
```json
["BTCUSDT","ETHUSDT","ADAUSDT","SOLUSDT","BNBUSDT","XRPUSDT"]
```

#### Generate Recommendation
```bash
curl "http://localhost:8000/api/v1/enhanced-recommendations/generate/BTCUSDT?timeframe=1d&days=30"
```

**Respuesta esperada:**
```json
{
  "symbol": "BTCUSDT",
  "recommendation": "BUY",
  "confidence": 0.75,
  "timestamp": "...",
  "details": {...}
}
```

#### Batch Recommendations
```bash
curl "http://localhost:8000/api/v1/enhanced-recommendations/batch/BTCUSDT,ETHUSDT?timeframe=1d&days=30"
```

**Respuesta esperada:**
```json
{
  "BTCUSDT": {...},
  "ETHUSDT": {...}
}
```

#### Stats
```bash
curl http://localhost:8000/api/v1/stats
```

**Respuesta esperada:**
```json
{
  "activeRecommendations": 6,
  "totalPnL": 15.2,
  "winRate": 68.0,
  "maxDrawdown": -8.0,
  "lastUpdate": "..."
}
```

### 6. ✅ Verificar CORS Headers

```bash
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     -v \
     http://localhost:8000/api/v1/enhanced-recommendations/supported-symbols
```

**Headers esperados en la respuesta:**
```
< access-control-allow-origin: http://localhost:3000
< access-control-allow-credentials: true
< access-control-allow-methods: GET, POST, PUT, DELETE, OPTIONS
< access-control-allow-headers: *
```

### 7. ✅ Verificar API Documentation

Abrir en navegador:
```
http://localhost:8000/docs
```

Deberías ver la interfaz de **Swagger UI** con todos los endpoints documentados.

### 8. ✅ Ejecutar Tests Automatizados

```bash
python test_cors.py
```

**Todos los tests deben pasar:**
```
============================================================
📊 Test Results Summary
============================================================
✅ Passed: 6/6
❌ Failed: 0/6
🎉 All tests passed! CORS is working correctly.
```

---

## 🐛 Troubleshooting

### Problema 1: `ModuleNotFoundError: No module named 'fastapi'`

**Solución:**
```bash
pip install fastapi uvicorn pydantic requests
```

### Problema 2: Puerto 8000 ya está en uso

**Verificar qué proceso usa el puerto:**
```powershell
# Windows
netstat -ano | findstr :8000
tasklist /FI "PID eq <PID>"

# Linux/Mac
lsof -i :8000
```

**Solución 1:** Matar el proceso existente

**Solución 2:** Cambiar puerto en `backend_simple.py`
```python
uvicorn.run(app, host="127.0.0.1", port=8001)  # Cambiar a 8001
```

Y actualizar `frontend/.env`:
```env
VITE_API_URL=http://localhost:8001
```

### Problema 3: Backend se cierra inmediatamente

**Posibles causas:**
1. Puerto bloqueado por firewall/antivirus
2. Permisos insuficientes
3. Error en el código

**Diagnóstico:**
```bash
# Ejecutar con más verbosidad
python -v backend_simple.py

# Revisar logs
# (el backend imprime errores en la terminal)
```

**Solución:**
1. Verificar firewall/antivirus
2. Ejecutar como administrador (solo si es necesario)
3. Revisar código para errores de sintaxis

### Problema 4: CORS errors persisten

**Verificación:**
```bash
python test_cors.py
```

Si el test `test_cors_headers` falla:

**Solución:**
1. Verificar que el backend está usando `backend_simple.py` (no otro archivo)
2. Verificar que el frontend está en `http://localhost:3000` o `http://localhost:5173`
3. Agregar el origen del frontend a `ALLOWED_ORIGINS` en `.env`

---

## ✅ Criterios de Éxito

El backend está funcionando correctamente si:

- ✅ El servidor arranca sin errores
- ✅ El puerto 8000 está en LISTENING
- ✅ `/health` retorna status "healthy"
- ✅ Todos los endpoints responden correctamente
- ✅ Headers CORS están presentes
- ✅ `python test_cors.py` pasa todos los tests (6/6)
- ✅ Swagger UI está accesible en `/docs`
- ✅ No hay errores en la consola/terminal

---

## 📊 Métricas de Salud

### Normal (Todo OK)

```
✅ Status Code: 200
✅ Response Time: < 100ms
✅ CORS Headers: Present
✅ Memory Usage: < 100MB
✅ CPU Usage: < 5%
```

### Warning (Revisar)

```
⚠️  Response Time: 100-500ms
⚠️  Memory Usage: 100-200MB
⚠️  Errores ocasionales en logs
```

### Critical (Acción Requerida)

```
❌ Status Code: 500
❌ Response Time: > 500ms
❌ CORS Headers: Missing
❌ Memory Usage: > 200MB
❌ Errores constantes en logs
```

---

## 🔄 Reinicio del Backend

Si algo va mal, reinicia el backend:

```bash
# 1. Detener el servidor (Ctrl+C en la terminal)

# 2. Verificar que no hay procesos zombies
netstat -an | findstr :8000

# 3. Si hay procesos, matarlos
# Windows:
taskkill /F /PID <PID>
# Linux/Mac:
kill -9 <PID>

# 4. Reiniciar el backend
python backend_simple.py

# 5. Verificar que está corriendo
curl http://localhost:8000/health
```

---

## 📝 Log de Verificación

Usa este checklist para documentar tu verificación:

```
Fecha: _______________
Hora: _______________

[ ] Python 3.11+ instalado
[ ] Dependencias instaladas (fastapi, uvicorn, pydantic, requests)
[ ] Backend arranca sin errores
[ ] Puerto 8000 en LISTENING
[ ] /health retorna "healthy"
[ ] /supported-symbols retorna lista de símbolos
[ ] /generate/{symbol} retorna recomendación
[ ] /batch/{symbols} retorna múltiples recomendaciones
[ ] /stats retorna estadísticas
[ ] CORS headers presentes
[ ] python test_cors.py pasa (6/6)
[ ] Swagger UI accesible en /docs
[ ] No hay errores en consola/terminal

Notas adicionales:
_________________________________
_________________________________
_________________________________
```

---

**Última actualización:** 15 de Octubre de 2025  
**Versión:** 1.0.0
