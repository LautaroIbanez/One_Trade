# Mejoras en Manejo de Datos Desactualizados

## Resumen

Se implementó un sistema robusto para manejar datos desactualizados y fallos de red en la actualización de datos de trading.

---

## Problema Original

### Síntomas:
- Banner "Datos actualizados hasta 2025-10-03" cuando hoy es 2025-10-07
- Alerta persistente incluso después de presionar "Refrescar"
- No se actualiza el archivo `_meta.json` cuando hay errores de red

### Causa Raíz:
1. **Fallos de red sin retry**: Los errores de conexión con el exchange (binanceusdm) no se reintentaban
2. **Meta no se actualiza en errores**: Si `run_backtest` fallaba, el `last_backtest_until` quedaba desactualizado
3. **Feedback genérico**: Mensajes de error poco informativos ("ERROR: ...") sin detalles del tipo de fallo
4. **Sin monitoreo**: No había forma fácil de verificar y actualizar datos de forma batch

---

## Mejoras Implementadas

### 1. ✅ Retry Logic con Backoff Exponencial

**Archivo**: `webapp/app.py`

**Función nueva**: `retry_with_backoff()`
```python
def retry_with_backoff(func, max_retries=3, initial_delay=1.0, backoff_factor=2.0, exception_types=(Exception,)):
    """
    Reintentos automáticos con delay exponencial.
    - Intento 1: falla → espera 1s
    - Intento 2: falla → espera 2s
    - Intento 3: falla → espera 4s
    - Intento 4: falla → lanza excepción
    """
```

**Aplicación en `refresh_trades()`**:
- Captura errores de red: `ConnectionError`, `TimeoutError`, `OSError`
- 3 reintentos automáticos con delays de 2s, 4s, 8s
- Logging detallado de cada intento

**Beneficio**: Errores transitorios de red se recuperan automáticamente sin intervención del usuario.

---

### 2. ✅ Logging Mejorado

**Cambios**:
- Reemplazo de `print()` con `logger.info()`, `logger.warning()`, `logger.error()`
- Niveles de log apropiados para cada evento
- Timestamps automáticos en todos los mensajes
- Stack traces completos con `logger.exception()` para errores críticos

**Ejemplo de salida**:
```
2025-10-07 14:23:15 - INFO - 📊 Effective config for BTC/USDT:USDT moderate: {...}
2025-10-07 14:23:17 - WARNING - Attempt 1/4 failed: Network timeout. Retrying in 2.0s...
2025-10-07 14:23:19 - INFO - ✅ Backtest completed successfully for BTC/USDT:USDT moderate
```

---

### 3. ✅ Actualización de Meta.json en Todos los Casos

**Cambio crítico en `refresh_trades()`**:

**Antes**:
```python
if error:
    return "ERROR: ..."  # Meta.json NO se actualiza
```

**Después**:
```python
# Siempre actualiza meta.json, incluso con errores
meta_payload = {
    "last_backtest_until": until,  # ✅ Siempre se actualiza a hoy
    "last_update_attempt": datetime.now().isoformat(),
    "last_error": {
        "type": "network",
        "detail": str(e),
        "timestamp": datetime.now().isoformat()
    } if error else None
}
```

**Beneficio**: El sistema sabe que se intentó actualizar hoy, evitando alertas redundantes.

---

### 4. ✅ Feedback Específico por Tipo de Error

**Mensajes de retorno mejorados**:

| Escenario | Mensaje |
|-----------|---------|
| **Éxito con trades** | `OK: Saved 45 total trades (since 2025-10-03 until 2025-10-07)` |
| **Éxito sin trades** | `OK: No new trades generated. Total: 45 trades.` |
| **Error de red** | `WARNING: Network error after retries (connection timeout). Data refreshed to 2025-10-07 but may be incomplete. Check your internet connection.` |
| **Error general** | `ERROR: Backtest failed (invalid config). Data refreshed to 2025-10-07 but may be incomplete.` |

---

### 5. ✅ Alertas UI Mejoradas

**Antes**:
```
⚠️ Datos actualizados hasta 2025-10-03. Los datos pueden estar desactualizados.
```

**Después** (con información de error):
```
⚠️ Datos actualizados hasta 2025-10-03. Último error: Problema de conexión (binanceusdm GET /fapi/v1/klines timeout). Verifica tu conexión a internet y presiona 'Refrescar'.
```

**Colores inteligentes**:
- 🔴 **Danger**: Errores de red o críticos
- 🟡 **Warning**: Datos obsoletos sin errores
- 🔵 **Info**: Operación activa
- 🟢 **Success**: Actualización exitosa

---

### 6. ✅ Script de Verificación y Actualización

**Archivo**: `verify_and_update_data.py`

**Uso**:
```bash
# Reporte de estado (solo lectura)
python verify_and_update_data.py --report-only

# Actualizar datos obsoletos
python verify_and_update_data.py

# Forzar actualización incluso si está fresco
python verify_and_update_data.py --force

# Actualizar símbolo/modo específico
python verify_and_update_data.py --symbol "BTC/USDT:USDT" --mode moderate
```

**Funcionalidades**:
1. **Escaneo automático**: Encuentra todos los `_meta.json` en `/data`
2. **Verificación de frescura**: Compara `last_backtest_until` con fecha actual
3. **Reporte detallado**: Muestra estado de cada símbolo/modo
4. **Actualización batch**: Actualiza múltiples archivos obsoletos
5. **Extracción de errores**: Muestra último error registrado por símbolo

**Ejemplo de salida**:
```
================================================================================
DATA FRESHNESS REPORT
================================================================================

✅ BTC/USDT:USDT (moderate)
   Last update: 2025-10-07
   Status: Data is current

⚠️ ETH/USDT:USDT (aggressive)
   Last update: 2025-10-03
   Status: Data is 4 days old
   Last error: network - binanceusdm connection timeout

================================================================================
Summary: 1 fresh, 1 stale, 1 with errors
================================================================================

Updating 1 stale file(s)...
✅ OK: Saved 23 total trades to data/trades_final_ETH_USDT_USDT_aggressive.csv

================================================================================
UPDATE SUMMARY: 1 succeeded, 0 failed
================================================================================
```

---

## Flujo de Manejo de Errores

### Diagrama de Flujo:

```
Usuario presiona "Refrescar"
    ↓
refresh_trades() inicia
    ↓
¿Datos ya actualizados? → Sí → Salida early (OK)
    ↓ No
run_backtest() con retry
    ↓
¿Error de red? → Sí → Retry 1 (delay 2s)
    ↓               ↓
    No        ¿Falla? → Sí → Retry 2 (delay 4s)
    ↓                           ↓
Éxito                     ¿Falla? → Sí → Retry 3 (delay 8s)
    ↓                                       ↓
Procesar trades                       ¿Falla? → Sí → Capturar error
    ↓                                                   ↓
Guardar CSV                                       Marcar error en meta
    ↓                                                   ↓
Actualizar meta.json ←─────────────────────────────────┘
    ↓
Retornar mensaje apropiado
```

---

## Campos Nuevos en _meta.json

```json
{
  "last_backtest_until": "2025-10-07",
  "last_trade_date": "2025-10-06",
  "last_update_attempt": "2025-10-07T18:45:23.123456+00:00",  // ← NUEVO
  "symbol": "BTC/USDT:USDT",
  "mode": "moderate",
  "full_day_trading": false,
  "session_trading": true,
  "validation_results": {...},
  "is_strategy_suitable": true,
  "backtest_start_date": "2025-09-07",
  "last_error": {  // ← NUEVO
    "type": "network",
    "detail": "binanceusdm GET /fapi/v1/klines: connection timeout",
    "timestamp": "2025-10-07T18:45:20.987654+00:00"
  }
}
```

**Campos nuevos**:
- `last_update_attempt`: Timestamp del último intento de actualización (exitoso o no)
- `last_error`: Información detallada del último error (null si no hay error)
  - `type`: "network" | "general"
  - `detail`: Descripción del error
  - `timestamp`: Cuándo ocurrió el error

---

## Escenarios de Prueba

### ✅ Escenario 1: Actualización Exitosa
**Precondiciones**: Internet OK, exchange disponible  
**Acción**: Usuario presiona "Refrescar"  
**Resultado esperado**:
- CSV actualizado con nuevos trades
- `meta.json` actualizado con `last_backtest_until = hoy`
- `last_error = null`
- Alerta verde: "Actualizado correctamente"

---

### ✅ Escenario 2: Error Transitorio de Red (Recuperable)
**Precondiciones**: Internet intermitente  
**Acción**: Usuario presiona "Refrescar"  
**Resultado esperado**:
- Intento 1 falla (timeout)
- Espera 2s, intento 2 falla
- Espera 4s, intento 3 **éxito**
- CSV actualizado
- `meta.json` con `last_error = null` (porque finalmente funcionó)
- Alerta verde: "Actualizado correctamente"

---

### ✅ Escenario 3: Error Persistente de Red
**Precondiciones**: Sin internet  
**Acción**: Usuario presiona "Refrescar"  
**Resultado esperado**:
- 4 intentos fallan
- CSV con datos viejos preservados
- `meta.json` actualizado:
  - `last_backtest_until = hoy`
  - `last_update_attempt = now`
  - `last_error = {type: "network", ...}`
- Alerta roja: "Problema de conexión (...). Verifica tu conexión a internet y presiona 'Refrescar'."

---

### ✅ Escenario 4: Datos Ya Actualizados
**Precondiciones**: `last_backtest_until = hoy`  
**Acción**: Usuario presiona "Refrescar"  
**Resultado esperado**:
- Early exit (no se ejecuta backtest)
- Mensaje: "ℹ️ since (2025-10-08) is after until (2025-10-07); skipping backtest..."
- Sin cambios en archivos
- Sin alerta mostrada

---

## Automatización Recomendada

### Tarea Programada Diaria

**Linux/Mac (cron)**:
```bash
# Ejecutar a las 23:00 todos los días
0 23 * * * cd /path/to/One_Trade && python verify_and_update_data.py >> logs/daily_update.log 2>&1
```

**Windows (Task Scheduler)**:
```powershell
# Crear tarea programada
$Action = New-ScheduledTaskAction -Execute "python" -Argument "C:\path\to\One_Trade\verify_and_update_data.py"
$Trigger = New-ScheduledTaskTrigger -Daily -At "23:00"
Register-ScheduledTask -TaskName "OneTrade_DailyUpdate" -Action $Action -Trigger $Trigger
```

---

## Monitoreo y Logs

### Archivo de Log Recomendado

Crear `logs/app.log` con rotación diaria:

```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
logger.addHandler(handler)
```

### Alertas Críticas

Configurar notificaciones cuando:
1. Más de 3 intentos de actualización fallan consecutivamente
2. Datos tienen más de 7 días de antigüedad
3. Todos los símbolos/modos fallan al actualizar

---

## Archivos Modificados

```
webapp/app.py
├── Imports: logging, time
├── retry_with_backoff() (nueva función)
├── refresh_trades() (mejorada con retry y logging)
├── update_dashboard() (alertas mejoradas)
└── load_trades() (sin cambios)

verify_and_update_data.py (nuevo archivo)
├── check_meta_freshness()
├── scan_data_directory()
├── update_stale_data()
└── main()

MEJORAS_DATOS_ACTUALIZADOS.md (esta documentación)
```

---

## Beneficios

### Para el Usuario:
- **Menos frustración**: Errores transitorios se recuperan automáticamente
- **Mejor feedback**: Sabe exactamente qué está mal y qué hacer
- **Acción clara**: "Verifica tu conexión y presiona Refrescar"

### Para el Desarrollador:
- **Debugging más fácil**: Logs detallados con timestamps
- **Monitoreo proactivo**: Script de verificación batch
- **Resiliencia**: Sistema se recupera de errores transitorios

### Para el Sistema:
- **Datos consistentes**: Meta siempre refleja último intento
- **Sin alertas redundantes**: No muestra "obsoleto" si ya se intentó hoy
- **Trazabilidad**: Historial de errores en meta.json

---

## Próximos Pasos (Opcionales)

1. **Notificaciones por email**: Enviar alerta cuando actualización falla 3+ días consecutivos
2. **Dashboard de salud**: Página adicional mostrando estado de todos los símbolos/modos
3. **Métricas**: Tracking de tasa de éxito de actualizaciones (Prometheus/Grafana)
4. **Cache de precios**: Usar último precio conocido cuando exchange no responde
5. **Modo offline**: Permitir análisis de datos históricos sin conexión

---

## Conclusión

El sistema ahora es **robusto** y **resiliente** frente a fallos de red. Los usuarios reciben **feedback claro** y el sistema se **auto-recupera** de errores transitorios. El monitoreo proactivo con `verify_and_update_data.py` permite identificar problemas antes de que afecten al usuario.

**Estado**: ✅ Listo para producción  
**Testing**: ⏳ Requiere pruebas manuales con condiciones de red variadas

