# Changes Summary

## 1. Habilitación de Backtests de Un Año + Normalización OHLC (LATEST - 2025-10-07)

### Objetivo:
Asegurar que todos los backtests cubran mínimo 365 días para validación estadística significativa y corregir fallos de columnas OHLC que impedían backtests largos.

### Changes Made:

#### Normalización y Validación OHLC (`btc_1tpd_backtester/utils.py`):

##### Nueva función: `standardize_ohlc_columns(df)`:
- **Mapeo de variaciones**: Reconoce `open`, `Open`, `OPEN`, `O`, `o` (y equivalentes para H, L, C, V)
- **Renombre automático**: Normaliza a nombres estándar lowercase
- **Validación estricta**: Lanza `ValueError` si faltan columnas requeridas
- **Conversión de tipos**: Convierte a numeric con `pd.to_numeric(errors='coerce')`
- **Manejo de NaN**: Forward fill + backward fill para valores faltantes
- **Integración**: Se llama automáticamente en `fetch_historical_data()`

##### Función mejorada: `validate_data_integrity(df)`:
- **Minimum data points**: >= 24 candles
- **Data types**: Verifica todas las columnas sean numeric
- **NaN/Inf detection**: Detecta valores faltantes o infinitos
- **OHLC relationships**: High >= all, Low <= all
- **Index ordering**: Verifica orden cronológico
- **Duplicate detection**: Detecta timestamps duplicados
- **Return format**: `(is_valid: bool, message: str)` con detalles del error

#### Enforcement de 365 Días (`webapp/app.py`):

##### BASE_CONFIG:
- `lookback_days`: 30 → **365** (línea 74)
- Comentario explicativo sobre requisito de 1 año para significancia estadística

##### `get_effective_config()` mejorada:
- **Enforcement activo**: `config["lookback_days"] = max(365, config.get("lookback_days", 365))`
- **Validación de backtest_start_date**: Si está configurado, asegura >= 365 días atrás
- **Ajuste automático**: Si start_date es muy reciente, lo ajusta a 365 días atrás
- **Logging**: Advierte cuando se hacen ajustes
- **Aplica a todos los modos**: Conservative, moderate, aggressive

##### `refresh_trades()` mejorada:
**Detección de historial insuficiente** (líneas 407-440):
```python
# Check if existing trades cover sufficient history (365 days minimum)
insufficient_history = False
if not existing_trades.empty:
    earliest_date = df_dates.min().date()
    days_coverage = (today - earliest_date).days
    if days_coverage < 365:
        insufficient_history = True
```

**Triggers de rebuild completo**:
1. `mode_change_detected` - Cambio de modo
2. `existing_trades.empty` - Sin trades existentes
3. `insufficient_history` - Cobertura < 365 días

**Resultado**: Cuando se detecta historial insuficiente, se limpia el DataFrame y se hace backtest completo de 365 días.

#### Metadata Enriquecida:

**Nuevos campos en `_meta.json`** (líneas 604-647):
- `first_trade_date`: Primera operación en el archivo
- `actual_lookback_days`: Cobertura real en días
- `configured_lookback_days`: Configurado (debería ser >= 365)
- `total_trades`: Total de trades en archivo
- `rebuild_type`: "complete" o "incremental"

**Beneficios**:
- Permite verificar cobertura real vs configurada
- Facilita debugging (saber tipo de rebuild)
- Tracking de trades para detectar pérdidas

#### Tests Implementados:

##### `btc_1tpd_backtester/tests/test_ohlc_validation.py`:
- 11 tests unitarios para normalización OHLC
- Cubre: nombres estándar, capitalizados, abreviados, faltantes, no numéricos
- Validación: datos válidos, vacíos, insuficientes, NaN, OHLC inválido, índice desordenado
- **Resultado**: ✅ 11/11 passed

##### `btc_1tpd_backtester/tests/test_one_year_backtest.py`:
- 5 tests de integración para configuración de 1 año
- Valida: BASE_CONFIG, get_effective_config, ajuste de dates, detección de historial insuficiente
- **Resultado**: ✅ 5/5 passed

### Beneficios:

1. **Confiabilidad Estadística**: 12x más datos (30 → 365 días)
2. **Validación Robusta**: Detecta y corrige columnas OHLC mal formateadas
3. **Auto-corrección**: Rebuilds automáticos cuando historial es insuficiente
4. **Transparencia**: Metadata rica para tracking y debugging
5. **Testing Completo**: 16 tests adicionales garantizan calidad
6. **Modo Invertido**: Misma cobertura de 365 días para comparación justa

### Impacto en Performance:
- **Primera ejecución**: Más lenta (~3-5 min para 365 días)
- **Actualizaciones incrementales**: Igual velocidad (~10-30s)
- **Tamaño de CSV**: Mayor (~100-200 KB vs ~10-20 KB)
- **Calidad de métricas**: Significativamente más confiable

---

## 2. Alineación de Métricas en Modo Invertido

### Objetivo:
Actualizar el modo de inversión de estrategia para que las métricas mantengan su interpretación estándar en lugar de transformarlas (e.g., win rate → loss rate).

### Changes Made:

#### Webapp (`webapp/app.py`):

##### `invert_metrics()` - Deprecado:
- ⚠️ Marcada como `[DEPRECATED]`
- Mantiene la lógica antigua solo para compatibilidad con tests legacy
- Documentación actualizada indicando usar `compute_metrics_pure(..., invertido=True)`

##### Pipeline de Métricas:
- **Eliminada doble inversión**: Antes se invertían trades en línea 1209 y luego se pasaba `invertido=True` a compute_metrics_pure
- **Nuevo flujo**: 
  - Trades originales se mantienen para cálculo de métricas
  - Se invierten SOLO para display (gráficos y tabla)
  - `compute_metrics_pure(..., invertido=True)` maneja la inversión internamente

##### UI Labels y Colores:
- **Labels**: Se mantienen estándar ("Win rate", "Max DD", "Profit Factor") en ambos modos
- **Tooltips**: Actualizados para explicar que se calculan sobre trades invertidos
- **Colores**: Lógica estándar en ambos modos (win rate alto = verde, DD negativo = rojo)
- **Eliminado**: Transformación de labels ("Loss rate", "Max Gain", etc.)

##### Display de Trades:
- Nueva variable `trades_display` que se invierte solo para visualización
- Gráficos y tabla reciben `trades_display` (invertido)
- Métricas se calculan desde `trades` (original) con flag `invertido=True`

##### Validación:
- Se mantiene correcta: usa señales originales para comparación
- No afectada por el modo de display

#### Tests Actualizados:

##### `webapp/test_metrics_parametrized.py`:
- `test_metrics_consistency()`: Actualizado para validar win rate real de trades invertidos (no 100 - win_rate)
- Añadida documentación del NUEVO comportamiento
- Verificación de que max_drawdown siempre es negativo

##### `webapp/test_strategy_inversion_integration.py`:
- `test_complete_inversion_flow()`: Usa `compute_metrics_pure` en lugar de `invert_metrics`
- `test_metric_labels_and_colors()`: Valida que labels NO cambien en modo invertido
- `test_double_inversion_consistency()`: Actualizado para nuevo pipeline
- Documentación actualizada en todos los tests

#### Documentation:

##### `INVERSION_ESTRATEGIA_RESUMEN.md`:
- Sección nueva: "Cambios Recientes (Alineación de Métricas)"
- Comparación Antes/Ahora del comportamiento
- Actualización de la descripción del pipeline
- Documentación de métricas con interpretación estándar

### Comportamiento Actualizado:

#### Métricas Direccionales (se invierten):
- `total_pnl`: Refleja el PnL de trades invertidos (-1 * original)
- `avg_pnl`: Promedio invertido
- `roi`: Retorno invertido
- `best_trade` / `worst_trade`: Invertidos
- `expectancy`: Invertido
- `profit_factor`: Recalculado desde trades invertidos

#### Métricas con Magnitud (NO se transforman):
- `win_rate`: % REAL de trades ganadores en serie invertida (no 100 - win_rate)
- `max_drawdown`: Siempre NEGATIVO (representa pérdidas desde pico)
- `dd_in_r`: Calculado normalmente desde trades invertidos

#### UI Consistency:
- Labels estándar en ambos modos
- Colores estándar en ambos modos
- Badge "INVERTIDA" visible cuando activo
- Tooltips informativos sobre el cálculo

### Benefits:

1. **Claridad**: Métricas mantienen su significado estándar
2. **No Confusión**: Labels y colores no cambian
3. **Correctitud**: Win rate refleja realidad de trades invertidos
4. **Consistencia**: Drawdown siempre negativo (convención estándar)
5. **Simplicidad**: Un solo pipeline de cálculo (compute_metrics_pure)
6. **Profesionalismo**: Interpretación estándar de métricas financieras

### Test Coverage:
- ✅ Tests parametrizados actualizados
- ✅ Tests de integración actualizados
- ✅ Validación de comportamiento nuevo
- ✅ Documentación completa

---

## 2. Consolidar a Sesión AR Única - Eliminar Soporte 24h

### Changes Made:

#### Webapp (`webapp/app.py`):
- **Removed Session Type Radio**: Eliminated `dbc.RadioItems(id="session-type")` from the navbar
- **Updated Callback**: Removed `session_type` parameter from `update_dashboard` callback
- **Simplified Configuration**: 
  - `BASE_CONFIG` now has `full_day_trading: False` and `session_trading: True`
  - All modes use session-based AR timezone windows
  - Entry windows: `(11, 14)` for all modes (AR morning session)
  - Exit windows: `(20, 22)` for all modes (AR evening session)
- **Updated Functions**:
  - `get_effective_config()` no longer takes `session_type` parameter
  - `refresh_trades()` no longer takes `session_type` parameter
  - `load_trades()` no longer takes `session_type` parameter
- **File Naming**: Removed `_24h` suffix logic, always uses standard filenames

#### Backtester (`btc_1tpd_backtester/btc_1tpd_backtest_final.py`):
- **Removed 24h Logic**: Eliminated all `full_day_trading` branches
- **Session Only**: Always uses `full_day_trading: False` and `session_trading: True`
- **Exit Reasons**: Updated to use `session_close` and `session_end` instead of `time_limit_24h`
- **Data Processing**: Simplified to use session data only

#### Strategy (`btc_1tpd_backtester/strategy_multifactor.py`):
- **Removed 24h Logic**: Eliminated all `full_day_trading` branches
- **Session Only**: Always uses `full_day_trading: False` and `session_trading: True`
- **Exit Reasons**: Updated to use `session_close` and `session_end` instead of `time_limit_24h`

## 2. Localizar todos los timestamps a hora Argentina

### Changes Made:

#### Webapp (`webapp/app.py`):
- **Added Imports**: `ZoneInfo` with fallback to `backports.zoneinfo`
- **Timezone Helper Functions**:
  - `ARGENTINA_TZ = ZoneInfo("America/Argentina/Buenos_Aires")`
  - `to_argentina_time(dt)` - Converts any datetime to Argentina timezone
  - `format_argentina_time(dt, format_str)` - Formats datetime to Argentina timezone string
- **Updated Display Elements**:
  - Current price timestamp now shows Argentina time
  - Recommendation entry time shows Argentina time
  - Table data (entry_time, exit_time) converted to Argentina timezone
  - Alert messages use Argentina date format
- **Updated Charts**:
  - `figure_equity_curve()` - X-axis shows Argentina time
  - `figure_drawdown()` - X-axis shows Argentina time
  - `figure_trade_timeline()` - Entry/exit times in Argentina timezone
  - `figure_monthly_performance()` - Monthly grouping in Argentina timezone
  - `figure_trades_on_price()` - Entry/exit markers in Argentina timezone

### Technical Details:
- **Timezone**: Argentina uses UTC-3 (America/Argentina/Buenos_Aires)
- **Conversion Logic**: Assumes UTC if no timezone info provided
- **Format Support**: Flexible formatting with default "%Y-%m-%d %H:%M:%S %Z"
- **Edge Cases**: Handles None inputs and naive datetimes gracefully

## Testing

### Test Files Created:
1. **`webapp/test_timezone_localization.py`**: Tests timezone conversion and formatting
2. **`webapp/test_simple_verification.py`**: Comprehensive verification of all changes

### Test Results:
- ✅ Timezone conversion works correctly (UTC to Argentina time)
- ✅ All function signatures updated properly
- ✅ Configuration changes implemented correctly
- ✅ UI elements updated to remove 24h switch
- ✅ All modules updated to always use 24h mode

## Benefits

### Session AR Consolidation:
- **Simplified UI**: No more confusing session type selection
- **Consistent Behavior**: Always uses AR session trading mode
- **Reduced Complexity**: Single configuration path
- **Better Performance**: No more mode switching logic
- **Localized Trading**: Optimized for Argentina timezone sessions

### Argentina Timezone Localization:
- **User-Friendly**: All times displayed in local Argentina time
- **Consistent Experience**: Unified timezone across all UI elements
- **Professional**: Proper timezone handling for local users
- **Flexible**: Easy to change timezone if needed

## Files Modified:
- `webapp/app.py` - Main webapp with UI and configuration changes
- `btc_1tpd_backtester/live_monitor.py` - Live monitoring updates
- `btc_1tpd_backtester/signals/today_signal.py` - Signal generation updates

## Files Created:
- `webapp/test_timezone_localization.py` - Timezone testing
- `webapp/test_simple_verification.py` - Comprehensive verification
- `CHANGES_SUMMARY.md` - This summary document

All changes have been successfully implemented and tested. The system now operates in AR session trading mode by default and displays all timestamps in Argentina timezone.
