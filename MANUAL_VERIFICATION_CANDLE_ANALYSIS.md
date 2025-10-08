# Manual Verification Checklist - Annual Candle Analysis Enhancements

Este documento describe el proceso de verificación manual para las mejoras de análisis de velas anuales implementadas en el dashboard.

## Objetivo
Validar que el sistema garantiza al menos 365 días de cobertura de datos históricos y que las tareas de análisis se muestran correctamente en todos los modos.

## Verificaciones Automatizadas Completadas ✓

Se ejecutaron 13 tests automatizados que validan:
- ✓ Función `determine_price_date_range` garantiza 365+ días
- ✓ Expansión automática de rangos cortos a 365 días
- ✓ Preservación de rangos válidos (>365 días)
- ✓ Manejo de fechas inválidas con fallback
- ✓ Soporte para lookback personalizado
- ✓ Timezone awareness (UTC)
- ✓ Función `build_candle_analysis_tasks` genera tareas para todos los modos
- ✓ Estructura correcta de tareas (title, description, priority)
- ✓ Prioridades dentro del rango 1-3
- ✓ Notas de inversión cuando `inverted=True`
- ✓ Tareas base presentes en todos los modos
- ✓ Tareas específicas por modo

**Resultado**: 13/13 tests PASSED ✓

## Checklist de Verificación Manual

### 1. Preparación
- [ ] Navegar a `C:\Users\lauta\OneDrive\Desktop\Trading\One_Trade`
- [ ] Ejecutar la aplicación Dash: `python -m webapp.app`
- [ ] Abrir navegador en `http://localhost:8050`

### 2. Verificación de Modo Conservador

#### Sin Inversión
- [ ] Seleccionar modo "Conservador" en el navbar
- [ ] Observar el log de la consola para confirmar:
  - `Price chart date range for [symbol]: [start] to [end] (365+ days)`
- [ ] Verificar que el gráfico de precios se carga sin errores
- [ ] Expandir panel "Tareas de Análisis Anual"
- [ ] Verificar 4 tareas presentes:
  - [ ] "Validar cobertura de datos" (P1 - rojo)
  - [ ] "Revisar patrones de largo plazo" (P2 - amarillo)
  - [ ] "Analizar zonas de sobrecompra/sobreventa anuales" (P2 - amarillo)
  - [ ] "Validar eficacia de reversión a la media" (P3 - azul)
- [ ] Verificar que las descripciones NO mencionan "(estrategia invertida)"

#### Con Inversión
- [ ] Activar switch "Invertir Estrategia"
- [ ] Expandir panel "Tareas de Análisis Anual"
- [ ] Verificar que TODAS las descripciones ahora incluyen "(estrategia invertida)"
- [ ] Confirmar que el badge "INVERTIDA" aparece en el panel

### 3. Verificación de Modo Moderado

#### Sin Inversión
- [ ] Seleccionar modo "Moderado" en el navbar
- [ ] Observar el log para confirmar 365+ días
- [ ] Verificar que el gráfico se actualiza correctamente
- [ ] Expandir panel "Tareas de Análisis Anual"
- [ ] Verificar 4 tareas presentes:
  - [ ] "Validar cobertura de datos" (P1 - rojo)
  - [ ] "Revisar patrones de largo plazo" (P2 - amarillo)
  - [ ] "Identificar tendencias dominantes anuales" (P2 - amarillo)
  - [ ] "Evaluar consistencia de seguimiento de tendencia" (P3 - azul)
- [ ] Verificar menciones de EMA, ADX, Heikin Ashi en las tareas

#### Con Inversión
- [ ] Activar switch "Invertir Estrategia"
- [ ] Verificar actualizaciones dinámicas con notas de inversión

### 4. Verificación de Modo Agresivo

#### Sin Inversión
- [ ] Seleccionar modo "Arriesgado" en el navbar
- [ ] Observar el log para confirmar 365+ días
- [ ] Expandir panel "Tareas de Análisis Anual"
- [ ] Verificar 4 tareas presentes:
  - [ ] "Validar cobertura de datos" (P1 - rojo)
  - [ ] "Revisar patrones de largo plazo" (P2 - amarillo)
  - [ ] "Mapear breakouts y fakeouts históricos" (P2 - amarillo)
  - [ ] "Analizar volatilidad extrema anual" (P3 - azul)
- [ ] Verificar menciones de breakouts, fakeouts, RSI extremo

#### Con Inversión
- [ ] Activar switch "Invertir Estrategia"
- [ ] Verificar actualizaciones dinámicas con notas de inversión

### 5. Verificación de Múltiples Símbolos

- [ ] Cambiar símbolo de BTC/USDT:USDT a ETH/USDT:USDT
- [ ] Confirmar en log: `Price chart date range for ETH/USDT:USDT: ...`
- [ ] Verificar que el gráfico carga con 365+ días
- [ ] Repetir para otros símbolos disponibles según el modo

### 6. Verificación de Integración

- [ ] Presionar botón "Refrescar"
- [ ] Verificar que no hay warnings de "Insufficient history"
- [ ] Confirmar que el rango de fechas en el log siempre muestra 365+ días
- [ ] Verificar que el título del gráfico muestra "Price with Trades (365+ days)"

### 7. Verificación de Persistencia

- [ ] Cambiar entre modos múltiples veces
- [ ] Activar/desactivar inversión varias veces
- [ ] Verificar que las tareas se actualizan instantáneamente
- [ ] Confirmar que no hay errores en la consola del navegador

### 8. Verificación de Logs

Revisar logs de la aplicación para confirmar mensajes esperados:

```
INFO - Price chart date range for BTC/USDT:USDT: 2024-10-08 to 2025-10-08 (365 days)
```

O si expande rangos cortos:

```
INFO - Expanding date range from [X] days to 365 days for [symbol]
INFO - Price chart date range for [symbol]: [start] to [end] (365 days)
```

### 9. Verificación de Edge Cases

- [ ] Caso 1: Sin datos históricos previos
  - Seleccionar símbolo nuevo o modo sin CSV
  - Verificar que `determine_price_date_range` usa lookback_days=365
  - Confirmar mensaje en log

- [ ] Caso 2: Datos históricos < 365 días
  - Si existe CSV con < 365 días, verificar expansión automática
  - Confirmar en log: "Expanding date range from [X] days to 365 days"

- [ ] Caso 3: Datos históricos > 365 días
  - Verificar que se preserva el rango completo
  - Confirmar en log el número real de días

## Criterios de Aceptación

### ✓ Funcionalidad Core
- [x] `determine_price_date_range` implementada y testeada
- [x] `build_candle_analysis_tasks` implementada y testeada
- [x] `figure_trades_on_price` actualizada para usar nueva función
- [x] Panel de tareas agregado al layout
- [x] Callbacks configurados para actualización dinámica

### ✓ Tests
- [x] 5/5 tests para `determine_price_date_range` PASSED
- [x] 8/8 tests para `build_candle_analysis_tasks` PASSED
- [x] Archivo de tests compatible con Python estándar creado

### ⏳ Verificación Manual (pendiente ejecución por usuario)
- [ ] Todos los modos verificados (conservative, moderate, aggressive)
- [ ] Inversión verificada en todos los modos
- [ ] Logs confirman 365+ días en todas las combinaciones
- [ ] Panel de tareas se actualiza correctamente
- [ ] No hay errores en consola del navegador

## Problemas Conocidos y Soluciones

### Warning de NumPy
**Problema**: Warning sobre NumPy 1.x vs 2.x durante importación  
**Impacto**: No afecta funcionalidad de las nuevas características  
**Solución**: Opcional - `pip install "numpy<2"` si se desea eliminar el warning

### Pytest No Disponible
**Problema**: Módulo pytest no instalado  
**Solución**: Se creó `test_candle_analysis_simple.py` que no requiere pytest

## Próximos Pasos

1. Ejecutar verificación manual siguiendo este checklist
2. Documentar cualquier issue encontrado
3. Actualizar `MEJORAS_IMPLEMENTADAS_RESUMEN.md` con nuevas características
4. Considerar agregar tooltips adicionales en UI para explicar tareas

## Resumen de Archivos Modificados

- ✓ `webapp/app.py` - Funciones helper y UI components agregados
- ✓ `webapp/test_candle_analysis_tasks.py` - Suite de tests con pytest
- ✓ `webapp/test_candle_analysis_simple.py` - Suite de tests sin pytest
- ✓ `MANUAL_VERIFICATION_CANDLE_ANALYSIS.md` - Este documento

## Fecha de Implementación
**2025-10-08**

---

**Nota**: Este checklist debe ser completado por el usuario final antes de considerar la implementación como finalizada.

