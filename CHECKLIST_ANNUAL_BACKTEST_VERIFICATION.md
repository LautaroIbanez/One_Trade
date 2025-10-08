# Checklist de Verificación - Simulación Anual y Backtesting Continuo

Este documento proporciona pasos manuales para validar que la simulación anual se completó correctamente y que el backtesting continuo funciona según lo esperado.

**Fecha de Creación**: 8 de Octubre, 2025  
**Versión**: 1.0

---

## 📋 Pre-requisitos

Antes de comenzar la verificación, asegúrate de tener:

- [x] Python 3.9+ instalado
- [x] Dependencias instaladas: `pip install -r btc_1tpd_backtester/requirements.txt`
- [x] Acceso al directorio `data/` con permisos de escritura
- [x] Conexión a internet para fetch de datos históricos

---

## 1️⃣ Verificación de Configuración Base

### 1.1 Validar Lookback Mínimo de 365 Días

```bash
# Ejecutar test de configuración
pytest btc_1tpd_backtester/tests/test_annual_coverage.py::test_base_config_enforces_365_days -v
```

**Resultado Esperado**: ✅ Test PASSED confirmando `BASE_CONFIG['lookback_days'] >= 365`

**Verificación Manual**:
```python
from webapp.app import BASE_CONFIG
print(f"Lookback days: {BASE_CONFIG['lookback_days']}")
# Debe mostrar: Lookback days: 365 (o mayor)
```

- [ ] ✅ BASE_CONFIG tiene lookback_days >= 365
- [ ] ✅ Test de configuración pasa

---

### 1.2 Validar Configuración Efectiva por Modo

```bash
# Ejecutar test por modo
pytest btc_1tpd_backtester/tests/test_annual_coverage.py::test_effective_config_enforces_365_days -v
```

**Resultado Esperado**: ✅ Todos los modos (conservative, moderate, aggressive) enforzan 365+ días

- [ ] ✅ Conservative mode: 365+ días
- [ ] ✅ Moderate mode: 365+ días  
- [ ] ✅ Aggressive mode: 365+ días

---

## 2️⃣ Ejecución de Batch Runner Anual

### 2.1 Ejecutar Backtest Completo (Modo Auto)

```bash
# Ejecutar batch runner en modo automático (today - 365 días)
python manage_backtests.py --since=auto
```

**Duración Estimada**: 10-30 minutos (dependiendo del número de símbolos)

**Resultado Esperado**:
```
BATCH BACKTEST EXECUTION SUMMARY
================================
Total symbols processed: [número]
Total modes processed: 3
Total executions: [número]
Successful: [número] (>90%)
Failed: 0
Insufficient coverage: 0
Total trades generated: [número]
```

**Verificación**:
- [ ] ✅ Batch runner completó sin errores (exit code 0)
- [ ] ✅ Al menos 90% de ejecuciones exitosas
- [ ] ✅ 0 fallos con insufficient_coverage
- [ ] ✅ Log guardado en `data/backtest_execution_log.json`

---

### 2.2 Revisar Log de Ejecución

```bash
# Ver resumen del log
python manage_backtests.py --report-only
```

**Verificar en el Log** (`data/backtest_execution_log.json`):
```json
{
  "timestamp": "2025-10-08T...",
  "since_date": "2024-10-08",
  "summary": {
    "total_executions": [número],
    "successful": [número],
    "failed": 0,
    "insufficient_coverage": 0
  }
}
```

- [ ] ✅ Timestamp es reciente (hoy)
- [ ] ✅ since_date es today - 365 días
- [ ] ✅ No hay ejecuciones fallidas o con cobertura insuficiente

---

## 3️⃣ Validación de Cobertura Real

### 3.1 Test de Cobertura en CSV Generados

```bash
# Ejecutar tests de cobertura
pytest btc_1tpd_backtester/tests/test_annual_coverage.py::test_csv_coverage_meets_minimum -v
```

**Resultado Esperado**: ✅ Todos los CSV tienen >= 365 días de cobertura

**Si el test falla**, revisar:
```bash
# Identificar archivos con cobertura insuficiente
pytest btc_1tpd_backtester/tests/test_annual_coverage.py::test_csv_coverage_meets_minimum -v -s
```

- [ ] ✅ Test de cobertura pasa para todos los archivos
- [ ] ✅ No hay warnings de cobertura insuficiente

---

### 3.2 Validar Metadatos (_meta.json)

```bash
# Test de estructura de meta files
pytest btc_1tpd_backtester/tests/test_annual_coverage.py::test_meta_file_structure -v
```

**Verificación Manual** de un archivo example:
```bash
# Revisar meta file de BTC moderate
cat data/trades_final_BTC_USDT_USDT_moderate_meta.json | python -m json.tool
```

**Campos Requeridos**:
```json
{
  "actual_lookback_days": 365,  // >= 365
  "first_trade_date": "2024-10-08",
  "last_trade_date": "2025-10-08",
  "total_trades": 50,  // >= 10 recomendado
  "symbol": "BTC/USDT:USDT",
  "mode": "moderate"
}
```

- [ ] ✅ `actual_lookback_days` >= 365 para todos los modos
- [ ] ✅ `first_trade_date` y `last_trade_date` consistentes con CSV
- [ ] ✅ `total_trades` >= 10 (mínimo razonable anual)

---

### 3.3 Consistencia CSV vs Meta

```bash
# Validar que counts coinciden
pytest btc_1tpd_backtester/tests/test_annual_coverage.py::test_csv_matches_meta_trade_count -v
```

**Resultado Esperado**: ✅ Todos los CSV tienen trade count == meta.total_trades

- [ ] ✅ No hay mismatches entre CSV y meta

---

## 4️⃣ Generación de Resúmenes Anuales

### 4.1 Generar Resumen Consolidado

```bash
# Generar resúmenes para todos los modos
python generate_annual_summary.py
```

**Resultado Esperado**:
```
ANNUAL SUMMARY REPORT
=====================
Period: All available data
Modes processed: 3

Mode: CONSERVATIVE
  Total Trades: [número]
  Total PnL: $[cantidad]
  Win Rate: [%]
  ...
```

**Archivos Generados**:
- `data/annual_summary_conservative.json`
- `data/annual_summary_moderate.json`
- `data/annual_summary_aggressive.json`
- `data/annual_summary_comparison.json`

- [ ] ✅ Resúmenes generados para los 3 modos
- [ ] ✅ Archivo de comparación creado
- [ ] ✅ Métricas razonables (no infinitas, no NaN)

---

### 4.2 Generar Resumen Year-to-Date

```bash
# Solo trades del año actual
python generate_annual_summary.py --ytd-only
```

**Verificación**:
- [ ] ✅ Solo incluye trades de 2025 (año actual)
- [ ] ✅ Métricas YTD calculadas correctamente

---

### 4.3 Revisar Comparativa de Modos

```bash
# Ver comparación
cat data/annual_summary_comparison.json | python -m json.tool
```

**Verificar**:
```json
{
  "modes": {
    "conservative": {
      "total_trades": [número],
      "total_pnl": [cantidad],
      "win_rate": [%],
      "profit_factor": [ratio]
    },
    ...
  }
}
```

- [ ] ✅ Comparativa muestra los 3 modos
- [ ] ✅ Conservative tiene mayor win_rate (típicamente)
- [ ] ✅ Aggressive tiene mayor potential PnL pero más volatilidad

---

## 5️⃣ Validación de Calidad de Datos

### 5.1 No Trades Futuros

```bash
# Verificar que no hay trades con fechas futuras
pytest btc_1tpd_backtester/tests/test_annual_coverage.py::test_no_future_trades -v
```

**Resultado Esperado**: ✅ No se detectan trades con fechas futuras

- [ ] ✅ Test pasa sin trades futuros

---

### 5.2 Mínimo de Trades Anuales

```bash
# Verificar trade count razonable
pytest btc_1tpd_backtester/tests/test_annual_coverage.py::test_minimum_trades_per_year -v
```

**Advertencia Aceptable**: Algunos pares pueden tener <10 trades si tienen poca volatilidad

- [ ] ✅ Mayoría de símbolos tienen >= 10 trades anuales
- [ ] ⚠️  Documentar símbolos con bajo trade count

---

### 5.3 Consistencia de Rangos de Fechas

```bash
# Validar fechas CSV vs meta
pytest btc_1tpd_backtester/tests/test_annual_coverage.py::test_csv_date_range_consistency -v
```

**Resultado Esperado**: ✅ Rangos de fechas consistentes

- [ ] ✅ `first_trade_date` en meta coincide con CSV
- [ ] ✅ `last_trade_date` en meta coincide con CSV

---

## 6️⃣ Verificación de UI/Dashboard

### 6.1 Ejecutar Dashboard

```bash
# Iniciar aplicación web
python -m webapp.app
```

**Acceder**: http://localhost:8050

**Verificar en UI**:
- [ ] ✅ Dashboard carga sin errores
- [ ] ✅ Métricas se muestran correctamente
- [ ] ✅ Gráficos de equity curve muestran >= 365 días
- [ ] ✅ No aparece banner de "Insufficient coverage"
- [ ] ✅ Selector de modo funciona (conservative/moderate/aggressive)

---

### 6.2 Verificar Alertas de Cobertura

**Escenario de Prueba**: Si un archivo tiene <365 días, debe mostrarse alerta

- [ ] ✅ Banner de alerta aparece cuando corresponde
- [ ] ✅ Mensaje es claro y accionable

---

## 7️⃣ Monitoreo y Actualización Continua

### 7.1 Verificar Frescura de Datos

```bash
# Ejecutar verificador de datos
python verify_and_update_data.py
```

**Resultado Esperado**:
```
Checking BTC/USDT:USDT - moderate...
✓ Data is up to date (last_until: 2025-10-08)
```

- [ ] ✅ Todos los símbolos/modos están actualizados
- [ ] ✅ `last_backtest_until` es hoy o ayer

---

### 7.2 Test de Actualización Incremental

```bash
# Simular actualización del día siguiente
# (esto se ejecutará automáticamente en cron)
python manage_backtests.py --since=auto
```

**Verificar**:
- [ ] ✅ Solo se agregan trades nuevos (no rebuild completo)
- [ ] ✅ `actual_lookback_days` se mantiene o aumenta
- [ ] ✅ Proceso toma <5 minutos

---

## 8️⃣ Validación de Tests Automatizados

### 8.1 Ejecutar Suite Completa

```bash
# Todos los tests de cobertura anual
pytest btc_1tpd_backtester/tests/test_annual_coverage.py -v
```

**Resultado Esperado**: ✅ Todos los tests pasan

**Tests Críticos**:
- [x] `test_base_config_enforces_365_days`
- [x] `test_effective_config_enforces_365_days`
- [x] `test_csv_coverage_meets_minimum`
- [x] `test_csv_matches_meta_trade_count`
- [x] `test_no_future_trades`

- [ ] ✅ 100% de tests pasan
- [ ] ✅ No hay warnings críticos

---

## 9️⃣ Checklist de Errores Comunes

### 9.1 "Insufficient coverage" en Batch Runner

**Síntomas**: Batch runner reporta `insufficient_coverage > 0`

**Diagnóstico**:
```bash
python manage_backtests.py --report-only
# Revisar qué símbolos/modos fallaron
```

**Solución**:
```bash
# Forzar rebuild para símbolos problemáticos
python manage_backtests.py --since=full --force-rebuild
```

- [ ] ✅ Problema identificado
- [ ] ✅ Rebuild forzado completado
- [ ] ✅ Coverage ahora >= 365 días

---

### 9.2 "Network error" en refresh_trades

**Síntomas**: Log muestra errores de conexión

**Solución**:
1. Verificar conexión a internet
2. Reintenta con retries automáticos (ya implementado)
3. Si persiste, ejecutar manualmente:
```bash
python manage_backtests.py --since=auto
```

- [ ] ✅ Conexión verificada
- [ ] ✅ Retry exitoso

---

### 9.3 Bajo Trade Count (<10 trades/año)

**Síntomas**: Test muestra warnings de bajo trade count

**Diagnóstico**: Revisar meta file para ver cobertura

**Posibles Causas**:
- Símbolo con poca volatilidad
- Estrategia muy restrictiva para ese par
- Datos históricos incompletos

**Acción**:
- [ ] ⚠️  Documentar símbolos con bajo count
- [ ] ✅ Verificar que datos históricos estén completos
- [ ] Considerar ajustar parámetros de estrategia (opcional)

---

## 🔟 Checklist Final de Completitud

### Cobertura de Datos
- [ ] ✅ Todos los modos tienen >= 365 días de cobertura
- [ ] ✅ Todos los símbolos principales (BTC, ETH) tienen datos completos
- [ ] ✅ Meta files actualizados con `actual_lookback_days`

### Métricas y Resúmenes
- [ ] ✅ Resúmenes anuales generados para los 3 modos
- [ ] ✅ Comparativa de modos disponible
- [ ] ✅ Métricas razonables (no infinitas, no NaN)

### Tests y Validaciones
- [ ] ✅ Todos los tests de cobertura pasan
- [ ] ✅ No hay trades futuros
- [ ] ✅ Trade counts razonables (>=10/año mayoría)

### Dashboard y UI
- [ ] ✅ Dashboard funcional sin errores
- [ ] ✅ Gráficos muestran datos anuales
- [ ] ✅ Alertas funcionan correctamente

### Automatización
- [ ] ✅ Batch runner ejecuta correctamente
- [ ] ✅ Verificador de datos funciona
- [ ] ✅ Resúmenes se generan sin errores

---

## 📊 Reporte de Verificación

**Fecha de Verificación**: _______________  
**Verificador**: _______________  
**Versión del Sistema**: 1.0

**Resumen de Resultados**:
- Total Checks: _____ / _____
- Tests Pasados: _____ / _____
- Issues Encontrados: _____
- Issues Resueltos: _____

**Estado Final**: ⬜ APROBADO  /  ⬜ REQUIERE ATENCIÓN

**Notas Adicionales**:
```
[Espacio para notas sobre issues específicos, decisiones tomadas, etc.]
```

---

## 🔄 Mantenimiento Continuo

### Daily (Automático via cron)
- [ ] Ejecutar `manage_backtests.py --since=auto` a las 00:30 UTC
- [ ] Ejecutar `generate_annual_summary.py` después del batch
- [ ] Ejecutar `verify_and_update_data.py` para verificar frescura

### Weekly (Manual)
- [ ] Revisar log de ejecuciones en `data/backtest_execution_log.json`
- [ ] Verificar métricas de resumen anual
- [ ] Revisar warnings de bajo trade count

### Monthly (Manual)
- [ ] Ejecutar suite completa de tests
- [ ] Revisar cobertura histórica (debería aumentar)
- [ ] Actualizar documentación si hay cambios

---

**Última Actualización**: 8 de Octubre, 2025
