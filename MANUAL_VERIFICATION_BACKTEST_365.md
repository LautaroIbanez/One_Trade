# Guía de Verificación Manual - Backtests de 365 Días

## Objetivo
Verificar que el sistema genera y mantiene backtests de al menos 365 días para todos los símbolos y modos.

---

## Pre-requisitos

✅ Cambios implementados en:
- `webapp/app.py`
- `btc_1tpd_backtester/utils.py`  
- `verify_and_update_data.py`

✅ Tests automatizados pasados:
- `test_ohlc_validation.py` (11/11)
- `test_one_year_backtest.py` (5/5)

---

## Paso 1: Verificar Estado Actual de Datos

### Comando:
```bash
python verify_and_update_data.py --report-only
```

### Salida Esperada:
```
================================================================================
DATA FRESHNESS REPORT
================================================================================

✅ BTC/USDT:USDT (moderate)
   Last update: 2025-10-07
   Status: Data is current

⚠️ BTC/USDT:USDT (aggressive)
   Last update: 2025-10-03
   Status: Data is 4 days old

...
================================================================================
Summary: X fresh, Y stale, Z with errors
================================================================================
```

### Verificar:
- [ ] ¿Cuántos archivos están frescos (✅)?
- [ ] ¿Cuántos están obsoletos (⚠️)?
- [ ] ¿Hay errores registrados?

---

## Paso 2: Actualizar Datos Obsoletos

### Comando:
```bash
python verify_and_update_data.py
```

### Proceso Esperado:
```
2025-10-07 XX:XX:XX - INFO - Updating BTC/USDT:USDT aggressive...
2025-10-07 XX:XX:XX - INFO - 📊 Effective config for BTC/USDT:USDT aggressive: {...}
2025-10-07 XX:XX:XX - INFO - ✅ Backtest completed successfully
2025-10-07 XX:XX:XX - INFO - ✅ OK: Saved 156 total trades to ...
```

### Observar:
- [ ] ¿Se completa sin errores?
- [ ] ¿Muestra "Backtest completed successfully"?
- [ ] ¿El número de trades es razonable (100-200+)?
- [ ] Si hay errores de red, ¿se reintenta 3 veces?

### En caso de error de red:
```
2025-10-07 XX:XX:XX - WARNING - Attempt 1/4 failed: ... Retrying in 2.0s...
2025-10-07 XX:XX:XX - WARNING - Attempt 2/4 failed: ... Retrying in 4.0s...
2025-10-07 XX:XX:XX - INFO - ✅ Backtest completed successfully
```

---

## Paso 3: Verificar Archivos Meta.json

### Archivo de Ejemplo:
```bash
cat data/trades_final_BTC_USDT_USDT_moderate_meta.json
```

### Campos a Verificar:

```json
{
  "last_backtest_until": "2025-10-07",        // ← Debe ser hoy o ayer
  "first_trade_date": "2024-10-07",           // ← Debe ser ~365 días atrás
  "actual_lookback_days": 365,                // ← Debe ser >= 365
  "configured_lookback_days": 365,            // ← Debe ser 365
  "total_trades": 142,                        // ← Debe ser 100-200+
  "rebuild_type": "complete",                 // ← "complete" en primera ejecución
  "last_error": null                          // ← Debe ser null si fue exitoso
}
```

### Checklist:
- [ ] `last_backtest_until` >= hoy - 1 día
- [ ] `first_trade_date` ~ 365 días atrás
- [ ] `actual_lookback_days` >= 365
- [ ] `configured_lookback_days` = 365
- [ ] `total_trades` > 50 (mínimo razonable para 1 año)
- [ ] `last_error` = null (o con detalles si hubo error)

---

## Paso 4: Lanzar Aplicación Web

### Comando:
```bash
python webapp/app.py
```

### Salida Esperada:
```
Dash is running on http://0.0.0.0:8050/

 * Serving Flask app 'One Trade'
 * Debug mode: on
```

### Abrir Navegador:
```
http://localhost:8050
```

---

## Paso 5: Verificar Hero Section

### Verificar visualización:
- [ ] **Precio en vivo**: Muestra precio actual (ej: $60,234.50)
- [ ] **Variación**: Muestra cambio vs día anterior con color (verde/rojo)
- [ ] **Ventana de entrada**: Muestra horario (ej: 11:00 - 14:00)
- [ ] **Estado de sesión**: Muestra emoji (🟢/🔴/⏸️)
- [ ] **Riesgo**: Muestra monto USDT
- [ ] **Estado trade**: "Trade Activo" o "Sin Trade"

---

## Paso 6: Verificar Tabla de Trades

### Acceder:
Navegar a la pestaña **"Trades"** en el dashboard

### Verificar:
1. **Primera operación** (scroll hasta el final):
   - [ ] `entry_time` debe ser ~365 días atrás
   - Ejemplo: Si hoy es 2025-10-07, debe haber trades desde 2024-10-07

2. **Última operación** (parte superior):
   - [ ] `entry_time` debe ser reciente (hoy o ayer)
   - [ ] Debe coincidir con `last_trade_date` del meta.json

3. **Total de operaciones**:
   - [ ] Contador muestra 100-200+ trades
   - [ ] Debe coincidir con `total_trades` del meta.json

4. **Filtrado y ordenamiento**:
   - [ ] Ordenar por fecha (ascendente) → verifica que va de 2024 a 2025
   - [ ] Filtrar por "long" → verifica que se pueden filtrar
   - [ ] Filtrar por "take_profit" → verifica exit reasons

---

## Paso 7: Probar Modo Invertido

### Activar Inversión:
1. Activar switch "Invertir Estrategia" en navbar
2. Presionar botón "Refrescar"

### Verificar:
- [ ] Badge "INVERTIDA" aparece en hero section y panel de estrategia
- [ ] Tabla de trades muestra:
  - Sides invertidos (long ↔ short)
  - PnL invertidos (100 → -100)
  - Exit reasons invertidos (take_profit ↔ stop_loss)
- [ ] **Cobertura se mantiene**: Primera operación sigue siendo ~365 días atrás
- [ ] **Total trades igual**: Mismo número de operaciones que en modo normal
- [ ] Métricas actualizadas con interpretación estándar

---

## Paso 8: Verificar Gráfico de Precios

### Navegar:
Pestaña "Price Chart"

### Verificar:
- [ ] Gráfico muestra historial de precios
- [ ] Marcadores de entrada (triángulos verdes/rojos)
- [ ] Marcadores de salida (X verdes/rojos)
- [ ] **Líneas horizontales** para recomendación del día:
  - 🔵 Entry (línea azul punteada)
  - 🔴 SL (línea roja punteada)
  - 🟢 TP (línea verde punteada)
- [ ] Anotaciones en margen derecho con precios

---

## Paso 9: Probar Diferentes Símbolos y Modos

### Para cada combinación:
| Símbolo | Modo | Acción |
|---------|------|--------|
| BTC/USDT:USDT | Conservative | Verificar 365 días |
| BTC/USDT:USDT | Moderate | Verificar 365 días |
| BTC/USDT:USDT | Aggressive | Verificar 365 días |
| ETH/USDT:USDT | Moderate | Verificar 365 días |

### Para cada uno:
1. Seleccionar símbolo y modo
2. Presionar "Refrescar"
3. Verificar tabla de trades:
   - [ ] Primera operación ~365 días atrás
   - [ ] Total trades > 50
4. Verificar meta.json:
   - [ ] `actual_lookback_days` >= 365
5. Alternar modo invertido:
   - [ ] Cobertura se mantiene en 365 días

---

## Paso 10: Simular Error de Red

### Método 1: Deshabilitar Internet Temporalmente
1. Desconectar WiFi/Ethernet
2. En la app, presionar "Refrescar"
3. Observar en terminal:
   ```
   WARNING - Attempt 1/4 failed: ... Retrying in 2.0s...
   WARNING - Attempt 2/4 failed: ... Retrying in 4.0s...
   WARNING - Attempt 3/4 failed: ... Retrying in 8.0s...
   ERROR - All 4 attempts failed. Last error: ...
   ```
4. Verificar alerta en UI:
   - [ ] Alerta roja con mensaje "Problema de conexión"
   - [ ] Incluye instrucción "Verifica tu conexión y presiona 'Refrescar'"
5. Reconectar internet y presionar "Refrescar"
6. Verificar:
   - [ ] Actualización exitosa después de reconectar
   - [ ] Alerta verde "Actualizado correctamente"

### Método 2: Reconectar Durante Retry
1. Desconectar internet
2. Presionar "Refrescar"
3. Reconectar internet DURANTE los retries
4. Observar:
   - [ ] Retry 1 o 2 falla
   - [ ] Retry 3 o 4 **éxito**
   - [ ] Meta.json se actualiza con `last_error = null`

---

## Paso 11: Verificar Rebuild por Historial Insuficiente

### Setup:
1. Editar manualmente un `_meta.json` para simular historial insuficiente:
   ```json
   {
     "first_trade_date": "2025-09-01",  // Solo 1 mes atrás
     "actual_lookback_days": 36
   }
   ```
2. Guardar archivo

### Verificar:
1. Lanzar app: `python webapp/app.py`
2. Seleccionar el símbolo/modo modificado
3. Presionar "Refrescar"
4. Observar en logs:
   ```
   WARNING - Insufficient history: only 36 days, need 365+ for valid backtest
   INFO - 🔄 Insufficient history detected: forcing full rebuild with 1-year data
   INFO - 📅 Rebuilding from: 2024-10-07 (365+ days)
   ```
5. Verificar en tabla de trades:
   - [ ] Primera operación ahora es ~365 días atrás (no solo 36)
   - [ ] Total trades aumentó significativamente
6. Verificar meta.json actualizado:
   - [ ] `actual_lookback_days` >= 365
   - [ ] `rebuild_type` = "complete"

---

## Paso 12: Verificar Coherencia de Métricas

### Para cada símbolo/modo:
1. Anotar métricas en modo normal:
   - Win rate: _____%
   - Total PnL: _____
   - Max DD: _____
   - Total trades: _____

2. Activar modo invertido

3. Anotar métricas en modo invertido:
   - Win rate: _____ (debería ser 100 - win_rate_normal)
   - Total PnL: _____ (debería ser -total_pnl_normal)
   - Max DD: _____ (debería ser negativo, no positivo)
   - Total trades: _____ (debería ser igual)

4. Verificar:
   - [ ] Total trades es exactamente igual en ambos modos
   - [ ] Win rate invertido = 100 - win rate normal (± 0.1%)
   - [ ] Total PnL invertido = - total PnL normal
   - [ ] Max DD siempre negativo en ambos modos

---

## Checklist Final

### Configuración:
- [ ] `BASE_CONFIG.lookback_days` = 365
- [ ] `get_effective_config()` enforce >= 365
- [ ] `refresh_trades()` detecta historial insuficiente

### Validación OHLC:
- [ ] `standardize_ohlc_columns()` normaliza nombres
- [ ] `validate_data_integrity()` verifica datos
- [ ] Errores lanzados son claros y accionables

### Metadata:
- [ ] `first_trade_date` presente en todos los meta.json
- [ ] `actual_lookback_days` >= 365
- [ ] `configured_lookback_days` = 365
- [ ] `total_trades` > 50
- [ ] `rebuild_type` correcto

### UI:
- [ ] Hero section funcional
- [ ] Líneas horizontales en gráfico de precios
- [ ] Tabla muestra 365 días de trades
- [ ] Modo invertido mantiene 365 días
- [ ] Alertas muestran colores y mensajes correctos

### Robustez:
- [ ] Retry funciona en errores de red
- [ ] Rebuild automático con historial insuficiente
- [ ] Meta.json se actualiza incluso en errores
- [ ] Logs informativos en todos los flujos

---

## Criterios de Éxito

### Mínimo Aceptable:
✅ Todos los símbolos/modos tienen >= 365 días de cobertura
✅ Meta.json actualizado con campos completos
✅ No hay errores en validación OHLC
✅ Modo invertido funciona correctamente

### Óptimo:
✅ Actualización incremental funciona (no rebuilds innecesarios)
✅ Retry recupera de errores transitorios de red
✅ Alerts muestran mensajes específicos y accionables
✅ Performance aceptable (< 5 min primera carga, < 30s incrementales)

---

## Problemas Comunes y Soluciones

### Problema: "Insufficient data: X candles (minimum 24 required)"
**Causa**: Exchange no devolvió suficientes datos  
**Solución**:
1. Verificar que el símbolo tiene historial >= 1 año en el exchange
2. Revisar conectividad con `verify_and_update_data.py --force`
3. Probar con timeframe diferente si persiste

### Problema: "Missing required OHLC columns: ['close']"
**Causa**: Respuesta de CCXT con formato inesperado  
**Solución**:
1. Revisar logs para ver columnas recibidas: `Available columns: [...]`
2. Añadir variación a `column_mappings` en `standardize_ohlc_columns()`
3. Reportar issue si es un formato nuevo de CCXT

### Problema: Tabla muestra solo 30 días de trades
**Causa**: Configuración antigua no se reconstruyó  
**Solución**:
1. Eliminar archivo CSV y meta.json manualmente
2. Presionar "Refrescar" en la app
3. Verificar logs muestran "forcing complete rebuild"
4. Confirmar nueva cobertura de 365 días

### Problema: Meta.json tiene `last_error: {type: "network", ...}`
**Causa**: Última actualización falló por red  
**Solución**:
1. Verificar conexión a internet
2. Revisar si Binance está operativo (https://www.binance.com/en/support/announcement)
3. Ejecutar `python verify_and_update_data.py --symbol "BTC/USDT:USDT" --mode moderate`
4. Si persiste, esperar y reintentar más tarde

---

## Reporte de Verificación (Template)

```
VERIFICACIÓN MANUAL - BACKTESTS DE 365 DÍAS
Fecha: _________________
Verificador: _________________

PASO 1: Estado Actual
  ✅/❌ Archivos frescos: ___/___
  ✅/❌ Archivos obsoletos: ___/___
  ✅/❌ Archivos con errores: ___/___

PASO 2: Actualización
  ✅/❌ Actualización completada sin errores
  ✅/❌ Reintentos funcionaron en errores de red
  ✅/❌ Todos los archivos actualizados exitosamente

PASO 3: Metadata
  ✅/❌ first_trade_date ~365 días atrás
  ✅/❌ actual_lookback_days >= 365
  ✅/❌ total_trades > 50
  ✅/❌ last_error = null

PASO 4: Aplicación Web
  ✅/❌ App inicia sin errores
  ✅/❌ Hero section funcional
  ✅/❌ Tabla muestra 365 días de trades
  ✅/❌ Gráfico con líneas horizontales
  ✅/❌ Modo invertido mantiene 365 días

PASO 5: Robustez
  ✅/❌ Retry funciona
  ✅/❌ Rebuild automático funciona
  ✅/❌ Alertas muestran mensajes claros

RESULTADO GLOBAL: ✅ PASS / ❌ FAIL

NOTAS:
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```

---

## Siguiente Revisión

**Frecuencia recomendada**: Semanal

**Comandos rápidos**:
```bash
# Verificación rápida
python verify_and_update_data.py --report-only

# Ver metadata de un archivo específico
cat data/trades_final_BTC_USDT_USDT_moderate_meta.json | grep -E "(first_trade_date|actual_lookback_days|total_trades)"
```

**Alertas críticas**:
- 🔴 `actual_lookback_days` < 365
- 🔴 `last_error` != null por más de 3 días
- 🟡 Algún archivo con `last_backtest_until` < hoy - 1

---

## Conclusión

Esta guía asegura que el sistema mantiene **backtests de 365 días mínimo**, garantizando:
- Métricas estadísticamente significativas
- Validación robusta de estrategias
- Comparación justa entre modo normal e invertido
- Detección temprana de problemas de datos

**Tiempo estimado de verificación completa**: 15-20 minutos  
**Frecuencia recomendada**: Semanal o después de cada deploy

