# Plan de Recuperación para Trades Históricos - Resumen de Implementación

## Estado Actual del Problema

**Síntoma**: El archivo `trades_final_BTC_USDT_USDT_moderate.csv` contiene solo 1 operación (8 de octubre) sin historial para análisis.

**Causa Raíz**: Error `KeyError: 'close'` durante normalización de columnas OHLC, resultando en:
- `actual_lookback_days = 0` en metadata
- Rebuild completo fallido
- CSV incompleto persistido sin validación de cobertura mínima

---

## Soluciones Implementadas ✅

### 1. Instrumentación de Captura de Fallos OHLC

**Archivo Modificado**: `btc_1tpd_backtester/utils.py`

**Mejoras en `standardize_ohlc_columns()`**:

1. **Logging Estructurado**:
   ```python
   logger.debug(f"standardize_ohlc_columns: received DataFrame with columns={list(df.columns)}, shape={df.shape}, dtypes={df.dtypes.to_dict()}")
   ```

2. **Captura de Payloads Problemáticos**:
   - Guarda samples automáticamente en `data/debug/` cuando falla
   - Formato JSON con metadata completa
   - Formato Parquet para reproducibilidad exacta
   ```
   data/debug/failed_ohlc_sample_YYYYMMDD_HHMMSS.json
   data/debug/failed_ohlc_sample_YYYYMMDD_HHMMSS.parquet
   ```

3. **Mapeos de Columnas Extendidos**:
   - **Antes**: `['close', 'Close', 'CLOSE', 'C', 'c']`
   - **Ahora**: `['close', 'Close', 'CLOSE', 'C', 'c', 'Close Price', 'close_price', 'closePrice', 'last', 'Last']`
   - Cubre variaciones detectadas: `openPrice`, `highPrice`, `lowPrice`, `baseVolume`, etc.

4. **Error Reporting Mejorado**:
   ```
   OHLC_NORMALIZATION_FAILED: missing_columns=['close'], available_columns=['timestamp', 'O', 'H', 'L', 'C', 'V'], shape=(100, 6)
   ```

---

### 2. Bloqueo de Persistencia con Cobertura Insuficiente

**Archivo Modificado**: `webapp/app.py` (función `refresh_trades`)

**Validación Crítica Agregada**:

```python
# CRITICAL VALIDATION: Block persistence if coverage < 365 days
if actual_lookback_days_check < 365:
    error_msg = f"BLOCKED: Refusing to persist data with insufficient coverage..."
    logger.error(error_msg)
    return f"ERROR: {error_msg}"
```

**Casos Bloqueados**:
1. **Cobertura < 365 días**: No persiste CSV/meta si `actual_lookback_days < 365`
2. **DataFrame vacío**: No persiste si rebuild completo resulta en 0 trades
3. **Logs detallados**: Registra motivo del bloqueo y comando sugerido

**Beneficios**:
- UI nunca muestra datos incompletos
- Meta.json siempre refleja cobertura real
- Usuario recibe instrucciones claras para resolución

---

## Próximos Pasos para Recuperación Completa

### Paso 1: Ejecutar Reconstrucción Manual (REQUERIDO)

```bash
# Forzar rebuild completo para BTC moderate
python manage_backtests.py --since=full --modes moderate --force-rebuild

# Verificar cobertura post-rebuild
pytest btc_1tpd_backtester/tests/test_annual_coverage.py::test_csv_coverage_meets_minimum -v -s
```

**Resultado Esperado**:
- CSV con 50+ trades
- `actual_lookback_days >= 365`
- Meta.json actualizado correctamente

### Paso 2: Verificar Gráficos en Dashboard

```bash
# Iniciar dashboard
python -m webapp.app
```

**Validar en UI** (http://localhost:8050):
- [ ] Equity curve muestra >= 365 días
- [ ] Price Chart tiene datos históricos
- [ ] Métricas no son cero
- [ ] No aparece banner de error

### Paso 3: Extender a Todos los Símbolos/Modos

```bash
# Rebuild completo de todos los modos
python manage_backtests.py --since=full --force-rebuild

# Validar todo
pytest btc_1tpd_backtester/tests/test_annual_coverage.py -v
```

---

## Tareas Pendientes de Implementación

### Task 2.2: UI Alert para Cobertura Insuficiente

**Descripción**: Agregar banner rojo visible cuando cobertura < 365 días

**Ubicación**: `webapp/app.py` (callback `update_dashboard`)

**Implementación Sugerida**:
```python
if hasattr(trades, 'attrs') and trades.attrs.get('insufficient_coverage'):
    alert_msg = "⚠️ COBERTURA INSUFICIENTE: Solo {days} días de historial (necesita 365+). Ejecute: python manage_backtests.py --since=full --force-rebuild"
    alert_color = "danger"
```

### Task 3.1: Modo `--diagnose` en verify_and_update_data.py

**Descripción**: Comando de diagnóstico automático

**Uso Sugerido**:
```bash
python verify_and_update_data.py --diagnose
```

**Funcionalidad**:
- Ejecuta backtest en modo verbose
- Valida cobertura >= 365 días
- Detecta errores de columnas OHLC
- Genera reporte OK/FAIL con causa raíz

### Task 3.2: Caché Local de Respuestas CCXT

**Descripción**: Guardar respuestas CCXT cuando fallan para debugging

**Ubicación**: `btc_1tpd_backtester/utils.py` (función `fetch_with_retry`)

**Beneficio**: Evita repetir llamadas API durante depuración

---

## Herramientas de Diagnóstico

### 1. Revisar Samples de Fallos

```bash
# Ver último fallo capturado
ls -lart data/debug/failed_ohlc_sample_*.json | tail -1 | xargs cat | python -m json.tool
```

**Información Disponible**:
- Columnas recibidas
- Columnas faltantes
- Shape del DataFrame
- 5 primeras filas de muestra

### 2. Validar Cobertura de CSV Existente

```python
import pandas as pd
import json

# Leer meta
with open('data/trades_final_BTC_USDT_USDT_moderate_meta.json') as f:
    meta = json.load(f)

print(f"Coverage: {meta['actual_lookback_days']} days")
print(f"Range: {meta['first_trade_date']} to {meta['last_trade_date']}")
print(f"Trades: {meta['total_trades']}")
```

### 3. Probar Normalización de Columnas

```python
from btc_1tpd_backtester.utils import standardize_ohlc_columns
import pandas as pd

# Simular payload problemático
df_problem = pd.DataFrame({
    'timestamp': [1234567890],
    'O': [50000],
    'H': [51000],
    'L': [49000],
    'C': [50500],  # <- Si esta columna falta, ahora se captura
    'V': [100]
})

try:
    df_normalized = standardize_ohlc_columns(df_problem)
    print("✓ Normalización exitosa")
except ValueError as e:
    print(f"✗ Error capturado: {e}")
    print("Ver data/debug/ para samples")
```

---

## Checklist de Verificación Post-Recuperación

### Datos Históricos
- [ ] `trades_final_BTC_USDT_USDT_moderate.csv` tiene >= 50 trades
- [ ] `actual_lookback_days >= 365` en meta.json
- [ ] `first_trade_date` es ~365 días atrás desde hoy
- [ ] `last_trade_date` es hoy o ayer

### Dashboard
- [ ] Equity curve muestra datos históricos completos
- [ ] Price Chart tiene velas de >= 365 días
- [ ] Monthly Performance muestra múltiples meses
- [ ] Métricas de resumen no son cero
- [ ] No aparece error en banner principal

### Tests Automatizados
- [ ] `test_csv_coverage_meets_minimum` PASSED
- [ ] `test_csv_matches_meta_trade_count` PASSED
- [ ] `test_csv_date_range_consistency` PASSED
- [ ] `test_no_future_trades` PASSED

### Logs
- [ ] No aparece `KeyError: 'close'` en logs recientes
- [ ] No aparece `BLOCKED: Refusing to persist` post-rebuild
- [ ] Logs muestran "Backtest completed successfully"

---

## Comandos Rápidos de Recuperación

```bash
# 1. Limpiar datos corruptos (opcional, hace backup automático)
mv data/trades_final_BTC_USDT_USDT_moderate.csv data/trades_final_BTC_USDT_USDT_moderate.csv.backup
mv data/trades_final_BTC_USDT_USDT_moderate_meta.json data/trades_final_BTC_USDT_USDT_moderate_meta.json.backup

# 2. Forzar rebuild completo
python manage_backtests.py --since=full --modes moderate --force-rebuild

# 3. Verificar resultado
pytest btc_1tpd_backtester/tests/test_annual_coverage.py::test_csv_coverage_meets_minimum -v -s

# 4. Validar dashboard
python -m webapp.app
# Abrir http://localhost:8050 y verificar datos históricos

# 5. Si todo OK, rebuild todos los modos
python manage_backtests.py --since=full --force-rebuild
```

---

## Métricas de Éxito

**Antes de la Recuperación**:
- 1 trade en CSV
- actual_lookback_days = 0
- Error KeyError: 'close'
- Dashboard sin datos históricos

**Después de la Recuperación**:
- 50+ trades en CSV (varía por símbolo)
- actual_lookback_days >= 365
- Sin errores de normalización
- Dashboard con gráficos completos de 1 año

---

## Prevención de Futuros Fallos

### 1. Monitoreo Automatizado

**Agregar a cron diario** (después de backtest batch):
```bash
# Verificar cobertura post-actualización
pytest btc_1tpd_backtester/tests/test_annual_coverage.py::test_csv_coverage_meets_minimum || \
    echo "WARNING: Coverage check failed" | mail -s "Backtest Alert" admin@example.com
```

### 2. Revisión de Logs

```bash
# Buscar fallos de normalización
grep "OHLC_NORMALIZATION_FAILED" logs/*.log

# Buscar bloqueos de persistencia
grep "BLOCKED: Refusing to persist" logs/*.log
```

### 3. Alertas en Dashboard

- Implementar Task 2.2 (banner rojo para cobertura insuficiente)
- Mostrar fecha de última actualización exitosa
- Indicador visual de "stale data"

---

## Soporte y Debugging

### Si persiste KeyError: 'close'

1. Revisar `data/debug/failed_ohlc_sample_*.json`
2. Identificar columnas recibidas
3. Agregar alias faltante a `column_mappings`
4. Crear test unitario con payload problemático

### Si cobertura sigue < 365 días

1. Verificar conexión a API CCXT
2. Revisar logs de `fetch_historical_data`
3. Intentar fetch manual para debug:
```python
from btc_1tpd_backtester.utils import fetch_historical_data
df = fetch_historical_data('BTC/USDT:USDT', '2024-01-01', '2025-01-01', '1h')
print(f"Fetched {len(df)} candles")
```

### Si persist sigue fallando

1. Revisar permisos del directorio `data/`
2. Verificar espacio en disco
3. Revisar logs para errores de I/O

---

**Última Actualización**: 8 de Octubre, 2025  
**Estado**: Core fixes implemented, awaiting manual rebuild execution


