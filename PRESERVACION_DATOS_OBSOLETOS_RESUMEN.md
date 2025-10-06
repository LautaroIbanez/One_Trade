# Preservación de Datos Obsoletos y Avisos al Usuario - Resumen de Implementación

## Objetivo
Implementar la preservación de datos obsoletos en lugar de rechazarlos, y mostrar avisos al usuario cuando los datos están desactualizados.

## Cambios Implementados

### 1. Modificación de `webapp/app.py` - Función `load_trades`

**Antes:**
- Los datos con sidecar obsoleto se rechazaban con `continue`
- No se preservaban datos históricos cuando el sidecar no cubría la sesión actual

**Después:**
- Los datos obsoletos se preservan y se marcan con un atributo `stale_last_until`
- Se mantiene el filtro de fechas futuras (solo se rechazan entradas con fechas futuras)
- Se agrega el atributo `df.attrs["stale_last_until"] = last_until` cuando los datos son obsoletos

```python
# Código clave implementado:
is_stale = False
last_until = None

# ... validación de sidecar ...

if last_until is not None and last_until >= today_date:
    # Datos frescos - comportamiento normal
    pass
else:
    # Sidecar obsoleto - marcar como obsoleto pero preservar datos
    is_stale = True
    print(f"⚠️ Stale sidecar detected: {path} (last_until={last_until}, today={today_date}) - preserving data")

# Marcar DataFrame como obsoleto si es necesario
if is_stale and last_until is not None:
    df.attrs["stale_last_until"] = last_until
```

### 2. Modificación de `webapp/app.py` - Callback `update_dashboard`

**Antes:**
- No se verificaba si los datos cargados eran obsoletos
- No se mostraban avisos sobre datos desactualizados

**Después:**
- Se verifica el atributo `stale_last_until` en el DataFrame cargado
- Se genera un mensaje de alerta cuando los datos son obsoletos
- El aviso tiene prioridad sobre otros mensajes de alerta

```python
# Código clave implementado:
# Verificar datos obsoletos en los trades cargados
stale_last_until = None
if hasattr(trades, 'attrs') and "stale_last_until" in trades.attrs:
    stale_last_until = trades.attrs["stale_last_until"]
    alert_msg = f"Datos actualizados hasta {format_argentina_time(datetime.fromisoformat(stale_last_until), '%Y-%m-%d')}. Los datos pueden estar desactualizados."

# Manejar diferentes escenarios de alerta
if stale_last_until is not None:
    # Aviso de datos obsoletos tiene prioridad
    pass  # alert_msg ya establecido arriba
elif trades.empty and active_trade is None:
    # ... otros casos ...
```

### 3. Pruebas Implementadas

#### `webapp/test_core_functionality.py`
- **`test_obsolete_data_preservation()`**: Verifica que los DataFrames pueden tener atributos `stale_last_until`
- **`test_stale_data_alert_logic()`**: Verifica la lógica de detección y construcción de mensajes de alerta

#### `webapp/test_obsolete_data_integration.py` (Nuevo archivo)
- **`test_load_trades_with_stale_data()`**: Test de integración completo que:
  - Crea un CSV con sidecar obsoleto
  - Verifica que `load_trades` preserva los datos
  - Verifica que se marca correctamente con `stale_last_until`
- **`test_dashboard_alert_with_stale_data()`**: Verifica que el dashboard genera alertas correctas
- **`test_fresh_data_no_alert()`**: Verifica que los datos frescos no generan alertas

## Comportamiento Resultante

### Escenario 1: Datos Frescos
- **Sidecar**: `last_backtest_until >= today`
- **Comportamiento**: Carga normal de datos, sin atributo `stale_last_until`
- **UI**: Sin avisos de datos obsoletos

### Escenario 2: Datos Obsoletos
- **Sidecar**: `last_backtest_until < today`
- **Comportamiento**: 
  - Se preservan los datos históricos
  - Se marca con `df.attrs["stale_last_until"] = last_until`
  - Se mantiene el filtro de fechas futuras
- **UI**: Muestra alerta: "Datos actualizados hasta {fecha}. Los datos pueden estar desactualizados."

### Escenario 3: Fechas Futuras
- **Datos**: Entradas con `entry_time > today`
- **Comportamiento**: Se rechazan (filtro mantenido)
- **UI**: No se muestran datos futuros

## Beneficios

1. **Preservación de Datos**: Los datos históricos nunca se pierden, incluso con sidecars obsoletos
2. **Transparencia**: El usuario es informado claramente sobre el estado de los datos
3. **Funcionalidad**: Las métricas y gráficos se muestran normalmente con datos obsoletos
4. **Seguridad**: Se mantiene la protección contra fechas futuras
5. **Retrocompatibilidad**: No se rompe la funcionalidad existente

## Verificación

Todos los tests pasan exitosamente:
- ✅ Tests de funcionalidad básica
- ✅ Tests de integración completos
- ✅ Verificación de preservación de datos
- ✅ Verificación de generación de alertas
- ✅ Verificación de datos frescos sin alertas

La implementación está completa y funcional.
