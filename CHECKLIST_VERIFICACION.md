# ✅ Checklist de Verificación - One Trade

## Verificación Rápida (5 minutos)

### 1. Estado de Datos
```bash
python verify_and_update_data.py --report-only
```

**Verificar**:
- [ ] Al menos 1 archivo está fresco (✅)
- [ ] Anotar cuántos están obsoletos: ___/___
- [ ] ¿Hay errores de red registrados? Sí/No

---

### 2. Tests Automatizados
```bash
python btc_1tpd_backtester/tests/test_ohlc_validation.py
python btc_1tpd_backtester/tests/test_one_year_backtest.py
```

**Resultado Esperado**: ✅ 16/16 tests passed

- [ ] OHLC validation: 11/11 passed
- [ ] One-year backtest: 5/5 passed

---

### 3. Sintaxis y Linter
```bash
python -m py_compile webapp/app.py btc_1tpd_backtester/utils.py
```

**Resultado Esperado**: Sin errores

- [ ] Sin errores de sintaxis

---

## Verificación Completa (15-20 minutos)

### 4. Actualizar Datos (si hay obsoletos)
```bash
python verify_and_update_data.py
```

**Observar**:
- [ ] ¿Actualización exitosa para todos?
- [ ] ¿Retry funcionó si hubo errores de red?
- [ ] ¿Total trades > 100 por símbolo/modo?

---

### 5. Lanzar Aplicación
```bash
python webapp/app.py
```

**Abrir**: http://localhost:8050

**Hero Section**:
- [ ] Precio en vivo visible
- [ ] Variación con color (verde/rojo)
- [ ] Ventana de trading con estado (🟢/🔴/⏸️)
- [ ] Riesgo por trade mostrado
- [ ] Badge "INVERTIDA" oculto (switch OFF)

---

### 6. Verificar Tabla de Trades

**Pestaña "Trades"**:
- [ ] Primera operación ~365 días atrás (scroll al final)
- [ ] Última operación reciente (hoy o ayer)
- [ ] Total trades: 100-200+ (dependiendo de estrategia)
- [ ] Columnas visibles: entry_time, side, entry/exit price, PnL, R, exit_time, reason

---

### 7. Verificar Gráfico de Precios

**Pestaña "Price Chart"**:
- [ ] Gráfico carga correctamente
- [ ] Marcadores de entrada/salida visibles
- [ ] **Líneas horizontales** (si hay recomendación del día):
  - [ ] Línea azul (Entry)
  - [ ] Línea roja (SL)
  - [ ] Línea verde (TP)
  - [ ] Anotaciones en margen derecho

---

### 8. Probar Modo Invertido

**Activar switch "Invertir Estrategia"**:
- [ ] Badge "INVERTIDA" aparece en hero y panel
- [ ] Presionar "Refrescar"
- [ ] Tabla trades muestra:
  - [ ] Sides invertidos (long ↔ short)
  - [ ] PnL invertidos (signo cambiado)
  - [ ] Exit reasons invertidos (TP ↔ SL)
- [ ] **Cobertura se mantiene**: Primera operación sigue ~365 días atrás
- [ ] **Total trades igual**: Mismo número que en modo normal
- [ ] Métricas con interpretación estándar:
  - [ ] Win rate = % real de ganadores (no 100 - win_rate)
  - [ ] Max DD negativo (no positivo)

---

### 9. Probar Diferentes Modos

**Para cada modo (conservador/moderado/arriesgado)**:
- [ ] Seleccionar modo
- [ ] Presionar "Refrescar"
- [ ] Verificar tabla tiene 365 días de trades
- [ ] Verificar meta.json tiene `actual_lookback_days >= 365`

---

### 10. Simular Error de Red

**Desconectar internet temporalmente**:
- [ ] Presionar "Refrescar"
- [ ] Observar en terminal:
  - [ ] "Attempt 1/4 failed... Retrying in 2.0s"
  - [ ] "Attempt 2/4 failed... Retrying in 4.0s"
  - [ ] "All 4 attempts failed" (si sigue sin internet)
- [ ] Verificar alerta en UI:
  - [ ] Alerta roja (danger)
  - [ ] Mensaje incluye "Problema de conexión"
  - [ ] Incluye "Verifica tu conexión y presiona 'Refrescar'"

**Reconectar internet**:
- [ ] Presionar "Refrescar" nuevamente
- [ ] Verificar actualización exitosa
- [ ] Alerta verde (success)

---

## Criterios de Éxito

### Mínimos (Obligatorios):
- [x] ✅ Tests automatizados: 25/25 passed
- [ ] ✅ Datos actualizados con 365 días de cobertura
- [ ] ✅ Meta.json con campos completos
- [ ] ✅ App web carga sin errores
- [ ] ✅ Tabla muestra 365 días de trades
- [ ] ✅ Modo invertido funciona correctamente

### Óptimos (Deseables):
- [ ] ✅ Hero section responsive en móvil
- [ ] ✅ Líneas horizontales visibles en gráfico
- [ ] ✅ Retry recupera de errores de red
- [ ] ✅ Alertas con colores y mensajes específicos
- [ ] ✅ Panel de estrategia colapsable funciona

---

## Troubleshooting Rápido

### ❌ "Insufficient data: X candles"
→ Verificar símbolo tiene >= 1 año de historial en exchange

### ❌ "Missing required OHLC columns"
→ Revisar logs, añadir variación a column_mappings si necesario

### ❌ "Network error after retries"
→ Verificar internet, estado de Binance, reintentar más tarde

### ❌ Tabla solo muestra 30 días
→ Eliminar CSV y meta.json, presionar "Refrescar" para rebuild

### ❌ Meta.json tiene last_error != null
→ Revisar detalles del error, corregir causa raíz, reintentar

---

## Reporte Final

**Fecha de verificación**: _________________

**Tests Automatizados**:
- [ ] ✅ 25/25 passed
- [ ] ❌ Algunos fallan (detallar): _______________

**Verificación Manual**:
- [ ] ✅ Todos los criterios cumplidos
- [ ] ⚠️ Algunos criterios incompletos (detallar): _______________
- [ ] ❌ Fallos críticos (detallar): _______________

**Estado Global**: 
- [ ] ✅ PASS - Listo para producción
- [ ] ⚠️ PASS CON OBSERVACIONES - Listo con notas
- [ ] ❌ FAIL - Requiere correcciones

**Notas adicionales**:
```
_____________________________________________________________________
_____________________________________________________________________
_____________________________________________________________________
```

---

## Comandos de Mantenimiento

### Verificación Diaria:
```bash
python verify_and_update_data.py --report-only
```

### Actualización Forzada (después de cambios):
```bash
python verify_and_update_data.py --force
```

### Rebuild Completo de un Símbolo:
```bash
# 1. Eliminar archivos
rm data/trades_final_BTC_USDT_USDT_moderate.csv
rm data/trades_final_BTC_USDT_USDT_moderate_meta.json

# 2. Lanzar app y presionar "Refrescar"
python webapp/app.py
```

### Ver Logs en Tiempo Real:
```bash
# En terminal separada mientras app corre
tail -f logs/app.log  # (si se configura archivo de log)
```

---

**Próxima revisión**: [Fecha]  
**Responsable**: [Nombre]

