# One Trade v2.0 - Web Interface Guide

## 🚀 Inicio Rápido

### 1. Instalar Dependencias (si aún no lo hiciste)

```bash
pip install dash dash-bootstrap-components
```

### 2. Iniciar la WebApp

```bash
python run_webapp.py
```

### 3. Abrir en el Navegador

Abre tu navegador en: **http://127.0.0.1:8050**

---

## 📊 Características de la Interfaz

### Tab 1: Dashboard
- **KPI Cards**: Total Return, Win Rate, Profit Factor, Max Drawdown
- **Equity Curve**: Gráfico interactivo de la evolución del capital
- **Tabla de Trades**: Últimos 20 trades con detalles completos
- **Colores semánticos**: Verde para ganancias, rojo para pérdidas

### Tab 2: Backtest
**Formulario de Configuración:**
- Selector de símbolo (BTC/USDT, ETH/USDT)
- Selector de estrategia (Current, Baseline)
- Fechas de inicio y fin
- Botón "Run Backtest"

**Resultados en Tiempo Real:**
- Estado de ejecución
- Métricas instantáneas al completar
- Almacenamiento automático de resultados

### Tab 3: Data
**Visualización de Datos:**
- Tabla con estado de todos los símbolos y timeframes
- Rango de fechas disponibles
- Número de velas descargadas
- Indicador de estado (✓/✗)

**Actualización de Datos:**
- Selector múltiple de símbolos
- Selector múltiple de timeframes
- Botón "Update Data" para descarga incremental

---

## 🎨 Diseño y UX

### Tecnologías Utilizadas
- **Dash**: Framework web Python
- **Bootstrap 5**: Diseño moderno y responsive
- **Plotly**: Gráficos interactivos
- **Font Awesome**: Iconos

### Colores y Temas
- **Azul primario**: #0d6efd (botones, títulos)
- **Verde éxito**: #198754 (trades positivos)
- **Rojo peligro**: #dc3545 (trades negativos)
- **Gris claro**: #f8f9fa (fondos de tablas)

### Responsive Design
- Adaptable a diferentes tamaños de pantalla
- Cards con sombras sutiles
- Tablas scrollables en móviles

---

## 📈 Flujo de Uso Típico

### Primera Vez

1. **Tab Data** → Verificar datos disponibles
2. Si faltan datos: **Update Data** con símbolos y timeframes necesarios
3. **Tab Backtest** → Configurar y ejecutar primer backtest
4. **Tab Dashboard** → Ver resultados visuales

### Uso Regular

1. **Tab Backtest** → Ejecutar nuevo backtest con diferentes parámetros
2. **Tab Dashboard** → Analizar resultados
3. Comparar estrategias (current vs baseline)
4. Ajustar fechas para diferentes períodos

---

## 🔄 Actualización Automática

La webapp incluye:
- **Interval Component**: Refresco cada 60 segundos
- **Store Component**: Persistencia de resultados en sesión
- **Callbacks Optimizados**: Solo actualiza lo necesario

---

## 🎯 Ejemplos de Uso

### Ejemplo 1: Comparar Estrategias

1. Tab Backtest → Ejecutar con "Current Strategy"
2. Ver resultados en Dashboard
3. Tab Backtest → Ejecutar con "Baseline Strategy"
4. Comparar métricas:
   - ¿Cuál tiene mejor Win Rate?
   - ¿Cuál tiene menor Max Drawdown?
   - ¿Cuál genera más trades?

### Ejemplo 2: Análisis de Período

1. Ejecutar backtest de 30 días
2. Ejecutar backtest de 90 días
3. Ejecutar backtest de 1 año
4. Comparar CAGR y consistency

### Ejemplo 3: Actualización de Datos

1. Tab Data → Revisar última fecha disponible
2. Si hay gap: Update Data para ese símbolo
3. Volver a Tab Backtest
4. Ejecutar con datos actualizados

---

## 🛠️ Personalización

### Cambiar Puerto

Edita `run_webapp.py`:

```python
app.run_server(debug=False, host="127.0.0.1", port=8080)  # Cambiar puerto
```

### Cambiar Tema

Edita `webapp_v2/app.py`:

```python
external_stylesheets=[
    dbc.themes.DARKLY,  # O FLATLY, COSMO, LITERA, etc.
    dbc.icons.FONT_AWESOME
]
```

### Agregar Métricas

Edita la función `create_dashboard_content()` en `webapp_v2/app.py` para agregar más KPI cards.

---

## 🐛 Troubleshooting

### Error: "Address already in use"

Otro proceso está usando el puerto 8050. Opciones:
1. Matar el proceso anterior
2. Cambiar el puerto en `run_webapp.py`

```bash
# Windows
netstat -ano | findstr :8050
taskkill /PID <PID> /F
```

### Error: "Module not found: dash"

```bash
pip install dash dash-bootstrap-components
```

### Backtest no ejecuta

1. Verificar que hay datos disponibles (Tab Data)
2. Verificar que las fechas tienen datos
3. Revisar logs en la consola

### Datos no se actualizan

1. Verificar conexión a internet
2. Verificar API limits de exchange
3. Esperar reintentos automáticos

---

## 📊 Métricas Mostradas

### KPIs Principales
- **Total Return**: Ganancia/pérdida absoluta y porcentual
- **Win Rate**: % de trades ganadores
- **Profit Factor**: Ratio ganancias/pérdidas
- **Max Drawdown**: Máxima caída desde peak

### Tabla de Trades
- Date & Time (ART)
- Side (LONG/SHORT)
- Entry/Exit prices
- PnL absoluto y porcentual
- Exit reason

### Equity Curve
- Eje X: Tiempo
- Eje Y: Equity ($)
- Línea punteada: Capital inicial
- Hover: Valores exactos

---

## 🎓 Tips de Uso

1. **Usa fechas recientes** para backtests rápidos inicialmente
2. **Compara ambas estrategias** en el mismo período
3. **Actualiza datos regularmente** antes de backtests importantes
4. **Revisa la tabla de trades** para entender el comportamiento
5. **Observa el equity curve** para identificar períodos problemáticos

---

## 🔮 Próximas Features (Roadmap)

- [ ] Comparación side-by-side de múltiples backtests
- [ ] Gráfico de drawdown separado
- [ ] Distribución de PnL (histograma)
- [ ] Exportar resultados a Excel/PDF
- [ ] Optimización de parámetros (grid search)
- [ ] Modo paper trading (live)
- [ ] Notificaciones de trades

---

## 🆘 Soporte

Si encuentras problemas:

1. Revisar logs en la terminal
2. Verificar `config/config.yaml`
3. Ejecutar `python verify_installation.py`
4. Consultar `README_V2.md`

---

## 📝 Notas Técnicas

### Arquitectura
```
run_webapp.py
    └── webapp_v2/app.py
            ├── BacktestEngine (integra todo el backend)
            ├── Callbacks (maneja interactividad)
            └── Layout (componentes visuales)
```

### Performance
- Callbacks optimizados con `prevent_initial_call=True`
- Store component para evitar re-cálculos
- Tablas con pagination (10 filas por página)
- Gráficos con `displayModeBar=False` para simplicidad

### Seguridad
- Solo localhost por defecto (`127.0.0.1`)
- No expuesto a internet
- Sin autenticación (uso local)

---

**¡Disfruta de One Trade v2.0!** 🚀

Para más información, consulta:
- `README_V2.md` - Documentación general
- `QUICKSTART.md` - Inicio rápido
- `IMPLEMENTATION_V2_SUMMARY.md` - Detalles técnicos



