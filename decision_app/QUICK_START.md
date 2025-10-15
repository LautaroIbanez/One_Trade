# ⚡ Quick Start - One Trade Decision App

## 🚀 Inicio Rápido (3 pasos)

### 1️⃣ Instalar Dependencias

```powershell
# Asegúrate de estar en el directorio decision_app
cd decision_app

# Opción A: Usar el script de instalación (Recomendado)
.\install_dependencies.ps1

# Opción B: Instalar manualmente
pip install -r requirements.txt
```

### 2️⃣ Arrancar el Backend

```powershell
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
...
```

### 3️⃣ Verificar que Funciona

Abre otra terminal y ejecuta:

```powershell
python test_cors.py
```

Deberías ver:
```
✅ Passed: 6/6
🎉 All tests passed! CORS is working correctly.
```

---

## 🌐 Acceder a la Aplicación

- **API Docs (Swagger):** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Symbols:** http://localhost:8000/api/v1/enhanced-recommendations/supported-symbols

---

## ❌ Solución de Errores Comunes

### Error: `ModuleNotFoundError: No module named 'fastapi'`

**Solución:**
```powershell
# Activar entorno virtual
& ..\..\.venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# O usar el script
.\install_dependencies.ps1
```

### Error: Puerto 8000 ya en uso

**Solución 1:** Encontrar y detener el proceso
```powershell
netstat -ano | findstr :8000
taskkill /F /PID <PID>
```

**Solución 2:** Cambiar el puerto
Editar `backend_simple.py`, línea final:
```python
uvicorn.run(app, host="127.0.0.1", port=8001)  # Cambiar a 8001
```

### Error: El backend se cierra inmediatamente

**Causas posibles:**
1. Puerto bloqueado por firewall
2. Falta alguna dependencia
3. Error en el código

**Diagnóstico:**
```powershell
# Ver errores detallados
python -v backend_simple.py

# Verificar dependencias
pip list | Select-String -Pattern "fastapi|uvicorn"
```

---

## 📦 Dependencias Requeridas

- `fastapi` - Framework web
- `uvicorn` - Servidor ASGI
- `pydantic` - Validación de datos
- `requests` - Cliente HTTP
- `python-multipart` - Procesamiento de formularios

Todas están en `requirements.txt`

---

## 🧪 Tests

```powershell
# Test completo de CORS
python test_cors.py

# Test manual de un endpoint
curl http://localhost:8000/health
```

---

## 📚 Más Información

- **README Completo:** [README_COMPLETO.md](./README_COMPLETO.md)
- **Guía de Desarrollo:** [GUIA_DESARROLLO.md](./GUIA_DESARROLLO.md)
- **Verificación Backend:** [VERIFICACION_BACKEND.md](./VERIFICACION_BACKEND.md)

---

## 💡 Tips

1. **Siempre activa el entorno virtual** antes de ejecutar comandos
2. **Verifica el puerto 8000** esté libre antes de arrancar
3. **Ejecuta los tests** para confirmar que todo funciona
4. **Lee los logs** del backend para debugging

---

**¿Problemas?** Consulta [GUIA_DESARROLLO.md](./GUIA_DESARROLLO.md) sección Troubleshooting
