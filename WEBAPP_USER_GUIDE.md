# Guía de Usuario - Aplicación Web Interactiva Mejorada

## Inicio Rápido

### 1. Instalación de Dependencias

Asegúrate de tener todas las dependencias instaladas:

```bash
pip install -r requirements.txt
```

Dependencias clave:
- `dash` >= 2.0
- `dash-bootstrap-components`
- `pandas`
- `plotly`

### 2. Iniciar la Aplicación

```bash
python start_interactive_webapp.py
```

Deberías ver:

```
======================================================================
🚀 One Trade v2.0 - Interactive Web Interface (Improved)
======================================================================
📊 Dashboard: http://127.0.0.1:8053

📈 Features:
   ✓ Interactive backtest execution with ThreadPoolExecutor
   ✓ Real-time data updates
   ✓ Automatic Dashboard refresh on backtest completion
   ✓ Reactive state management with dcc.Store
   ✓ Optimized loading with caching
   ✓ Robust error handling and logging

🔧 Improvements:
   • Replaced Flask config with Dash Store components
   • Thread-safe async operations
   • Automatic cache invalidation
   • Enhanced validation and error messages

⚡ Press Ctrl+C to stop the server
======================================================================
```

### 3. Acceder a la Aplicación

Abre tu navegador en: **http://127.0.0.1:8053**

---

## Navegación por Pestañas

### 📊 Dashboard

**Propósito**: Visualizar todos los backtests guardados.

**Funcionalidades:**

1. **Vista Automática de Backtests**
   - Muestra los últimos 10 backtests ejecutados
   - Ordenados por fecha (más reciente primero)
   - Código de colores:
     - 🟢 Verde: Backtests con retorno positivo
     - 🔴 Rojo: Backtests con retorno negativo

2. **Actualización Automática** ⭐ NUEVA FUNCIONALIDAD
   - El Dashboard se actualiza **automáticamente** al completar un backtest
   - Muestra alerta verde de confirmación: "¡Nuevo backtest completado!"
   - No requiere recarga manual de la página

3. **Botón Refresh Manual**
   - Puedes forzar una actualización en cualquier momento
   - Útil si navegas de otra pestaña y quieres ver cambios

**Información Mostrada por Backtest:**

```
📈 BTC/USDT - 20241010 120000
Trades: 45 | Win Rate: 64.4% | Return: +12.45%
Final Equity: $112,450.00 | Fees: $245.50
```

---

### ⚙️ Backtest

**Propósito**: Ejecutar nuevos backtests interactivamente.

**Pasos:**

1. **Seleccionar Símbolo**
   - BTC/USDT
   - ETH/USDT

2. **Seleccionar Estrategia**
   - Baseline (EMA/RSI)
   - Current (EMA/RSI/MACD)

3. **Definir Período**
   - Fecha Inicio: Selector de calendario
   - Fecha Fin: Selector de calendario
   - Ejemplo: 2024-01-01 a 2025-10-09

4. **Ejecutar**
   - Click en botón "Ejecutar Backtest"
   - Se muestra spinner animado: ⏳ "Ejecutando backtest para BTC/USDT con estrategia baseline..."

5. **Ver Resultados**
   - Al completar, se muestran métricas clave:
     - Total Return: $1,245.50
     - Win Rate: 64.4%
     - Total Trades: 45
     - Profit Factor: 2.15

6. **Verificar Dashboard** ⭐ NUEVA FUNCIONALIDAD
   - Cambia a la pestaña "Dashboard"
   - Verás el nuevo backtest en la lista
   - Aparece alerta de confirmación automáticamente

---

### 📁 Data

**Propósito**: Gestionar datos de mercado.

**Funcionalidades:**

1. **Ver Estado de Datos**
   - Tabla con símbolos y timeframes
   - Fecha inicio/fin de datos disponibles
   - Número de velas cargadas

2. **Actualizar Datos**
   - Seleccionar símbolos (múltiple selección)
   - Seleccionar timeframes (15m, 1d)
   - Click en "Actualizar Datos"
   - Muestra progreso: ⏳ "Actualizando datos para 1 símbolos y 1 timeframes..."

3. **Verificar Completación**
   - Al terminar: ✅ "Datos actualizados exitosamente!"
   - Tabla se actualiza con nuevos rangos de fechas

---

## Verificación de Mejoras

### Prueba 1: Actualización Automática del Dashboard

**Objetivo**: Verificar que el Dashboard se actualiza sin intervención manual.

**Pasos:**

1. Abre la aplicación en http://127.0.0.1:8053
2. Ve a la pestaña "Dashboard" y cuenta cuántos backtests hay (ej: 5)
3. Cambia a la pestaña "Backtest"
4. Configura un backtest:
   - Símbolo: BTC/USDT
   - Estrategia: baseline
   - Fechas: 2024-01-01 a 2024-01-31 (período corto para test rápido)
5. Click en "Ejecutar Backtest"
6. Espera a que complete (aprox. 10-30 segundos)
7. **SIN HACER NADA MÁS**, cambia a la pestaña "Dashboard"

**Resultado Esperado:** ✅
- Dashboard muestra +1 backtest (ahora 6 en total)
- Aparece alerta verde: "¡Nuevo backtest completado! Los resultados se han actualizado automáticamente."
- El nuevo backtest aparece en el tope de la lista

**Resultado Incorrecto:** ❌
- Dashboard sigue mostrando 5 backtests
- Necesitas hacer click en "Refresh Backtests" para verlo

---

### Prueba 2: Validación de Errores

**Objetivo**: Verificar que errores se manejan correctamente.

**Pasos:**

1. Ve a la pestaña "Backtest"
2. Configura un backtest con fechas inválidas:
   - Fecha Inicio: 2025-12-31
   - Fecha Fin: 2024-01-01 (antes de la fecha de inicio)
3. Click en "Ejecutar Backtest"

**Resultado Esperado:** ✅
- Aparece alerta roja con mensaje de error
- Error se registra en `logs/webapp.log`
- Aplicación no se cuelga

---

### Prueba 3: Concurrencia

**Objetivo**: Verificar que múltiples backtests se manejan correctamente.

**Pasos:**

1. Abre la aplicación
2. Ve a la pestaña "Backtest"
3. Configura y ejecuta un backtest largo (ej: todo 2024)
4. **Inmediatamente** después, intenta ejecutar otro backtest

**Resultado Esperado:** ✅
- Primer backtest sigue ejecutándose
- Segundo backtest entra en cola (ThreadPoolExecutor con max_workers=2)
- Ambos backtests completan exitosamente
- Dashboard muestra ambos resultados

---

### Prueba 4: Logging

**Objetivo**: Verificar que los logs se registran correctamente.

**Pasos:**

1. Abre el archivo `logs/webapp.log` en un editor
2. Ejecuta un backtest desde la UI
3. Refresca el archivo de log

**Resultado Esperado:** ✅

Deberías ver entradas como:

```
2025-10-10 15:30:45,123 - webapp_v2.interactive_app - INFO - Loading saved backtests from CSV files
2025-10-10 15:30:45,145 - webapp_v2.interactive_app - INFO - Found 12 backtest CSV files
2025-10-10 15:30:45,167 - webapp_v2.interactive_app - INFO - Successfully loaded 12 backtests
2025-10-10 15:32:10,234 - webapp_v2.interactive_app - INFO - Backtest button clicked: BTC/USDT, baseline, 2024-01-01 to 2024-01-31
2025-10-10 15:33:25,456 - webapp_v2.interactive_app - INFO - Backtest completed successfully: 45 trades
2025-10-10 15:33:25,478 - webapp_v2.interactive_app - INFO - Dashboard refreshed due to backtest completion
```

---

### Prueba 5: Caché

**Objetivo**: Verificar que el caché funciona y se invalida correctamente.

**Pasos:**

1. Ve al Dashboard (carga backtests por primera vez)
2. Observa el tiempo de carga en los logs
3. Click en otra pestaña y regresa al Dashboard
4. Observa el tiempo de carga en los logs (debería ser instantáneo - caché)
5. Ejecuta un nuevo backtest
6. Al completar, observa que Dashboard se actualiza (caché invalidado)

**Resultado Esperado:** ✅

En `logs/webapp.log`:

```
# Primera carga (sin caché)
2025-10-10 15:30:45 - INFO - Loading saved backtests from CSV files
2025-10-10 15:30:45 - INFO - Found 12 backtest CSV files
2025-10-10 15:30:45 - INFO - Successfully loaded 12 backtests

# Segunda carga (con caché - no aparecen logs de "Loading")
# No hay nuevas entradas de carga

# Después de nuevo backtest (caché invalidado)
2025-10-10 15:33:25 - INFO - Loading saved backtests from CSV files
2025-10-10 15:33:25 - INFO - Found 13 backtest CSV files
2025-10-10 15:33:25 - INFO - Successfully loaded 13 backtests
```

---

## Solución de Problemas

### Problema: Dashboard no se actualiza automáticamente

**Síntomas:**
- Ejecutas un backtest
- Cambias al Dashboard
- No aparece el nuevo backtest

**Diagnóstico:**

1. Verifica logs en `logs/webapp.log`:
```bash
tail -f logs/webapp.log | grep "Backtest completed"
```

2. Busca mensajes de error:
```bash
grep ERROR logs/webapp.log
```

**Soluciones:**

- **Si no hay entrada "Backtest completed"**: El backtest falló. Revisa el error en logs.
- **Si hay entrada pero Dashboard no actualiza**: Problema de sincronización. Reinicia el servidor.
- **Si hay error de permisos**: Verifica que `data_incremental/backtest_results/` existe y tiene permisos de escritura.

---

### Problema: Spinner no se detiene

**Síntomas:**
- Ejecutas un backtest
- Spinner sigue girando indefinidamente

**Diagnóstico:**

1. Verifica que el backtest completó:
```bash
ls -lt data_incremental/backtest_results/ | head
```

2. Verifica logs:
```bash
grep "Backtest completed\|Error" logs/webapp.log
```

**Soluciones:**

- **Si hay error en logs**: Backtest falló por datos faltantes o error de configuración. Actualiza datos primero.
- **Si backtest completó pero UI no actualiza**: Refresca la página (F5).
- **Si problema persiste**: Reinicia el servidor.

---

### Problema: Error "Missing columns ['pnl', 'fees']"

**Síntomas:**
- Error en logs al cargar Dashboard
- Algunos backtests no aparecen en la lista

**Causa:**
Archivo CSV de backtest está corrupto o incompleto.

**Solución:**

1. Identifica el archivo problemático en logs:
```
ERROR - Missing columns ['pnl'] in data_incremental/backtest_results/trades_BTC_USDT_20241010_120000.csv
```

2. Opciones:
   - Eliminar el archivo corrupto:
     ```bash
     rm data_incremental/backtest_results/trades_BTC_USDT_20241010_120000.csv
     ```
   - O regenerar el backtest

3. Refresca el Dashboard

---

### Problema: Puerto 8053 ya en uso

**Síntomas:**
```
OSError: [Errno 48] Address already in use
```

**Solución:**

1. Encuentra el proceso usando el puerto:
```bash
# Windows
netstat -ano | findstr :8053
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8053
kill -9 <PID>
```

2. O cambia el puerto en `start_interactive_webapp.py`:
```python
app.run(debug=False, host="127.0.0.1", port=8054)  # Cambiar puerto
```

---

## Comandos Útiles

### Ver logs en tiempo real

```bash
# Ver todo
tail -f logs/webapp.log

# Solo errores
tail -f logs/webapp.log | grep ERROR

# Solo eventos de backtest
tail -f logs/webapp.log | grep "Backtest"

# Solo eventos de Dashboard
tail -f logs/webapp.log | grep "Dashboard"
```

### Limpiar caché manualmente

```python
# En Python REPL
from webapp_v2.interactive_app import invalidate_cache
invalidate_cache()
```

### Ver backtests guardados

```bash
# Listar todos
ls -lh data_incremental/backtest_results/

# Últimos 5
ls -lt data_incremental/backtest_results/ | head -5

# Contar total
ls data_incremental/backtest_results/*.csv | wc -l
```

### Ejecutar pruebas

```bash
# Todas las pruebas
pytest tests/test_webapp_improvements.py -v

# Excluir pruebas lentas
pytest tests/test_webapp_improvements.py -v -m "not slow"

# Solo pruebas de carga
pytest tests/test_webapp_improvements.py::TestLoadSavedBacktests -v
```

---

## Mejoras Implementadas - Resumen

| Mejora | Antes | Después |
|--------|-------|---------|
| **Actualización Dashboard** | ❌ Manual (clic requerido) | ✅ Automática al completar |
| **Estado** | ❌ Flask config (no thread-safe) | ✅ dcc.Store (reactivo) |
| **Async** | ⚠️ threading.Thread básico | ✅ ThreadPoolExecutor |
| **Validación** | ❌ Sin validación | ✅ Columnas y formato |
| **Logging** | ❌ print() | ✅ Logger con archivo |
| **Caché** | ❌ Sin caché | ✅ LRU con invalidación |
| **Spinners** | ⚠️ Texto estático | ✅ Bootstrap animados |

---

## Soporte

Para más información, consulta:

- `WEBAPP_IMPROVEMENTS.md`: Detalles técnicos de implementación
- `tests/test_webapp_improvements.py`: Suite de pruebas automatizadas
- `logs/webapp.log`: Logs de ejecución
- GitHub Issues: [Reportar problemas](https://github.com/tu-repo/issues)

---

**¡Disfruta del Dashboard mejorado!** 🚀


