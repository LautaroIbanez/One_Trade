# 🔄 User Flows - One Trade Decision App

**Epic**: 0.2 - Prototipos UI/UX  
**Story Points**: 13  
**Duración**: 2-3 días  
**Status**: 🚧 EN PROGRESO

---

## 🎯 Flujos Principales

### 1. Flujo de Decisión Diaria

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FLUJO: DECISIÓN DIARIA                                  │
└─────────────────────────────────────────────────────────────────────────────┘

👤 Usuario → 🏠 Dashboard → 📊 Decisión → 📈 Detalle → ✅ Acción

┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Usuario   │───▶│  Dashboard  │───▶│  Decisión   │───▶│   Detalle   │
│             │    │             │    │             │    │             │
│ • Login     │    │ • Ver       │    │ • Ver       │    │ • Analizar  │
│ • Check     │    │   recomend. │    │   señal     │    │   señales   │
│   notif.    │    │ • Ver       │    │ • Ver       │    │ • Ver       │
│             │    │   precio    │    │   confianza │    │   gráficos  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                    │
                                                                    ▼
                                                          ┌─────────────┐
                                                          │   Acción    │
                                                          │             │
                                                          │ • Ejecutar  │
                                                          │   trade     │
                                                          │ • Guardar   │
                                                          │   decisión  │
                                                          │ • Compartir │
                                                          └─────────────┘
```

**Pasos Detallados:**

1. **Login/Check** (5 segundos)
   - Usuario accede a la app
   - Ve notificación de nueva decisión
   - Click en notificación

2. **Dashboard** (10 segundos)
   - Ve recomendación principal
   - Revisa precio actual
   - Ve resumen de señales
   - Click en "Ver Detalles"

3. **Detalle de Decisión** (30 segundos)
   - Analiza cada estrategia
   - Ve gráficos técnicos
   - Revisa confianza
   - Toma decisión

4. **Acción** (15 segundos)
   - Ejecuta trade (si decide)
   - Guarda decisión
   - Comparte resultado

**Tiempo Total**: ~1 minuto

---

### 2. Flujo de Análisis Histórico

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FLUJO: ANÁLISIS HISTÓRICO                               │
└─────────────────────────────────────────────────────────────────────────────┘

👤 Usuario → 📊 Historial → 🔍 Filtros → 📈 Análisis → 📋 Insights

┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Usuario   │───▶│  Historial  │───▶│   Filtros   │───▶│   Análisis  │
│             │    │             │    │             │    │             │
│ • Quiere    │    │ • Ver       │    │ • Seleccion │    │ • Ver       │
│   revisar   │    │   trades    │    │   período   │    │   métricas  │
│   performance│    │ • Ver       │    │ • Seleccion │    │ • Ver       │
│             │    │   métricas  │    │   monedas   │    │   gráficos  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                    │
                                                                    ▼
                                                          ┌─────────────┐
                                                          │  Insights   │
                                                          │             │
                                                          │ • Identif.  │
                                                          │   patrones  │
                                                          │ • Optimizar │
                                                          │   estrategia│
                                                          │ • Exportar  │
                                                          └─────────────┘
```

**Pasos Detallados:**

1. **Acceso** (5 segundos)
   - Click en "Historial" desde dashboard
   - Ve lista de trades recientes

2. **Filtrado** (15 segundos)
   - Selecciona período (últimos 30 días)
   - Selecciona monedas (BTC, ETH)
   - Aplica filtros

3. **Análisis** (45 segundos)
   - Revisa métricas de performance
   - Analiza gráfico de equity curve
   - Identifica trades exitosos/fallidos

4. **Insights** (30 segundos)
   - Identifica patrones
   - Optimiza configuración
   - Exporta datos

**Tiempo Total**: ~1.5 minutos

---

### 3. Flujo de Configuración de Estrategias

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                FLUJO: CONFIGURACIÓN DE ESTRATEGIAS                         │
└─────────────────────────────────────────────────────────────────────────────┘

👤 Usuario → ⚙️ Config → 📊 Estrategias → 🔧 Editar → ✅ Guardar

┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Usuario   │───▶│  Configura. │───▶│ Estrategias │───▶│   Editar    │
│             │    │             │    │             │    │             │
│ • Quiere    │    │ • Accede    │    │ • Ve        │    │ • Modifica  │
│   optimizar │    │   a config  │    │   estrategias│    │   parámetros│
│   estrategias│    │ • Navega    │    │ • Selecciona│    │ • Ajusta    │
│             │    │   a sección │    │   estrategia│    │   pesos     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                    │
                                                                    ▼
                                                          ┌─────────────┐
                                                          │   Guardar   │
                                                          │             │
                                                          │ • Valida    │
                                                          │   cambios   │
                                                          │ • Aplica    │
                                                          │   nueva     │
                                                          │   config    │
                                                          │ • Testa     │
                                                          └─────────────┘
```

**Pasos Detallados:**

1. **Acceso** (5 segundos)
   - Click en "Configuración" desde menú
   - Navega a "Estrategias"

2. **Selección** (10 segundos)
   - Ve lista de estrategias activas
   - Selecciona estrategia a modificar
   - Click en "Editar"

3. **Edición** (60 segundos)
   - Modifica parámetros (RSI, MACD, etc.)
   - Ajusta pesos de estrategias
   - Configura niveles de confianza
   - Preview de cambios

4. **Guardado** (15 segundos)
   - Valida configuración
   - Aplica cambios
   - Ejecuta test rápido
   - Confirma guardado

**Tiempo Total**: ~1.5 minutos

---

### 4. Flujo de Backtest

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FLUJO: BACKTEST                                     │
└─────────────────────────────────────────────────────────────────────────────┘

👤 Usuario → 🧪 Backtests → ⚙️ Configurar → ▶️ Ejecutar → 📊 Resultados

┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Usuario   │───▶│  Backtests  │───▶│ Configurar  │───▶│  Ejecutar   │
│             │    │             │    │             │    │             │
│ • Quiere    │    │ • Ve        │    │ • Selecciona│    │ • Inicia    │
│   probar    │    │   backtests │    │   período   │    │   backtest  │
│   estrategia│    │   previos   │    │ • Selecciona│    │ • Ve        │
│             │    │ • Click     │    │   monedas   │    │   progreso  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                    │
                                                                    ▼
                                                          ┌─────────────┐
                                                          │  Resultados │
                                                          │             │
                                                          │ • Ve        │
                                                          │   métricas  │
                                                          │ • Analiza   │
                                                          │   gráficos  │
                                                          │ • Compara   │
                                                          │   estrategias│
                                                          └─────────────┘
```

**Pasos Detallados:**

1. **Acceso** (5 segundos)
   - Click en "Backtests" desde menú
   - Ve backtests anteriores

2. **Configuración** (30 segundos)
   - Selecciona período (6 meses)
   - Selecciona monedas (BTC/USDT)
   - Selecciona estrategias
   - Click en "Nuevo Backtest"

3. **Ejecución** (2-5 minutos)
   - Ve progreso en tiempo real
   - Espera completado
   - Recibe notificación

4. **Análisis** (60 segundos)
   - Revisa métricas (Sharpe, Win Rate, etc.)
   - Analiza gráfico de equity curve
   - Compara con backtests anteriores

**Tiempo Total**: ~3-6 minutos

---

### 5. Flujo de Configuración del Sistema

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FLUJO: CONFIGURACIÓN DEL SISTEMA                        │
└─────────────────────────────────────────────────────────────────────────────┘

👤 Usuario → ⚙️ Config → 🔧 Sistema → 💾 Guardar → ✅ Confirmar

┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Usuario   │───▶│  Configura. │───▶│   Sistema   │───▶│   Guardar   │
│             │    │             │    │             │    │             │
│ • Quiere    │    │ • Accede    │    │ • Configura │    │ • Valida    │
│   configurar│    │   a config  │    │   trading   │    │   cambios   │
│   sistema   │    │ • Navega    │    │ • Configura │    │ • Aplica    │
│             │    │   a sistema │    │   notific.  │    │   cambios   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                    │
                                                                    ▼
                                                          ┌─────────────┐
                                                          │  Confirmar  │
                                                          │             │
                                                          │ • Ve        │
                                                          │   resumen   │
                                                          │ • Confirma  │
                                                          │   cambios   │
                                                          │ • Recibe    │
                                                          │   feedback  │
                                                          └─────────────┘
```

**Pasos Detallados:**

1. **Acceso** (5 segundos)
   - Click en "Configuración" desde menú
   - Navega a "Sistema"

2. **Configuración** (90 segundos)
   - Configura parámetros de trading
   - Configura notificaciones
   - Configura API keys
   - Configura seguridad

3. **Guardado** (15 segundos)
   - Valida configuración
   - Aplica cambios
   - Ve resumen de cambios

4. **Confirmación** (10 segundos)
   - Confirma cambios
   - Recibe feedback de éxito
   - Ve estado actualizado

**Tiempo Total**: ~2 minutos

---

### 6. Flujo de Notificaciones

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FLUJO: NOTIFICACIONES                               │
└─────────────────────────────────────────────────────────────────────────────┘

🔔 Notificación → 👤 Usuario → 📱 Click → 🏠 App → 📊 Decisión

┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Notificación│───▶│   Usuario   │───▶│    Click    │───▶│     App     │
│             │    │             │    │             │    │             │
│ • Nueva     │    │ • Recibe    │    │ • Click en  │    │ • Abre      │
│   decisión  │    │   notif.    │    │   notif.    │    │   app       │
│ • Push/Email│    │ • Ve        │    │ • Navega    │    │ • Va a      │
│             │    │   preview   │    │   a app     │    │   dashboard │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                    │
                                                                    ▼
                                                          ┌─────────────┐
                                                          │  Decisión   │
                                                          │             │
                                                          │ • Ve        │
                                                          │   recomend. │
                                                          │ • Analiza   │
                                                          │   señales   │
                                                          │ • Toma      │
                                                          │   acción    │
                                                          └─────────────┘
```

**Pasos Detallados:**

1. **Notificación** (Instantáneo)
   - Sistema genera nueva decisión
   - Envía push notification
   - Envía email (opcional)

2. **Recepción** (5 segundos)
   - Usuario recibe notificación
   - Ve preview de decisión
   - Decide si abrir app

3. **Acceso** (10 segundos)
   - Click en notificación
   - App se abre
   - Navega a dashboard

4. **Acción** (30 segundos)
   - Ve recomendación
   - Analiza señales
   - Toma decisión

**Tiempo Total**: ~45 segundos

---

### 7. Flujo de Error y Recuperación

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FLUJO: ERROR Y RECUPERACIÓN                             │
└─────────────────────────────────────────────────────────────────────────────┘

❌ Error → 👤 Usuario → 🔍 Diagnóstico → 🔧 Solución → ✅ Recuperación

┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    Error    │───▶│   Usuario   │───▶│ Diagnóstico │───▶│  Solución   │
│             │    │             │    │             │    │             │
│ • API       │    │ • Ve        │    │ • Ve        │    │ • Aplica    │
│   falla     │    │   error     │    │   detalles  │    │   fix       │
│ • Datos     │    │ • Entiende  │    │ • Entiende  │    │ • Reinicia  │
│   corruptos │    │   problema  │    │   causa     │    │   servicio  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                    │
                                                                    ▼
                                                          ┌─────────────┐
                                                          │ Recuperación│
                                                          │             │
                                                          │ • Verifica  │
                                                          │   estado    │
                                                          │ • Continúa  │
                                                          │   flujo     │
                                                          │ • Reporta   │
                                                          │   éxito     │
                                                          └─────────────┘
```

**Pasos Detallados:**

1. **Error** (Instantáneo)
   - Sistema detecta error
   - Muestra mensaje de error
   - Proporciona contexto

2. **Diagnóstico** (30 segundos)
   - Usuario ve detalles del error
   - Entiende la causa
   - Ve opciones de solución

3. **Solución** (60 segundos)
   - Aplica solución sugerida
   - Reinicia servicio si es necesario
   - Verifica conectividad

4. **Recuperación** (15 segundos)
   - Verifica que error se resolvió
   - Continúa con flujo normal
   - Reporta éxito

**Tiempo Total**: ~1.5 minutos

---

## 📊 Métricas de Flujo

### Tiempos Objetivo

| Flujo | Tiempo Objetivo | Tiempo Actual | Mejora |
|-------|----------------|---------------|---------|
| Decisión Diaria | 1 min | - | - |
| Análisis Histórico | 1.5 min | - | - |
| Config Estrategias | 1.5 min | - | - |
| Backtest | 3-6 min | - | - |
| Config Sistema | 2 min | - | - |
| Notificaciones | 45 seg | - | - |
| Error Recovery | 1.5 min | - | - |

### Puntos de Fricción

1. **Decisión Diaria**
   - ❌ Demasiados clicks para ver detalles
   - ❌ Información dispersa
   - ✅ Solución: Dashboard consolidado

2. **Análisis Histórico**
   - ❌ Filtros complejos
   - ❌ Gráficos lentos
   - ✅ Solución: Filtros inteligentes

3. **Configuración**
   - ❌ Demasiadas opciones
   - ❌ Validación confusa
   - ✅ Solución: Wizard guiado

---

## 🎯 Optimizaciones

### 1. Shortcuts y Atajos

```css
/* Keyboard Shortcuts */
.shortcut {
  font-size: var(--text-xs);
  color: var(--neutral-500);
  background: var(--neutral-100);
  padding: 2px 6px;
  border-radius: 4px;
  margin-left: var(--margin-xs);
}

/* Quick Actions */
.quick-action {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
}
```

### 2. Progressive Disclosure

```css
/* Collapsible Sections */
.collapsible {
  transition: all 0.3s ease;
}

.collapsible.collapsed {
  max-height: 0;
  overflow: hidden;
}

/* Expandable Cards */
.expandable-card {
  cursor: pointer;
  transition: transform 0.2s ease;
}

.expandable-card:hover {
  transform: translateY(-2px);
}
```

### 3. Smart Defaults

```css
/* Auto-save Indicators */
.auto-save {
  position: absolute;
  top: 10px;
  right: 10px;
  font-size: var(--text-xs);
  color: var(--success);
}

/* Smart Suggestions */
.suggestion {
  background: var(--brand-primary);
  color: white;
  padding: var(--padding-xs) var(--padding-sm);
  border-radius: var(--radius-md);
  margin: var(--margin-xs) 0;
}
```

---

## 📱 Responsive Flows

### Mobile Optimizations

1. **Decisión Diaria**
   - Stack vertical de información
   - Swipe para ver detalles
   - Botones grandes para acciones

2. **Análisis Histórico**
   - Tabla horizontal scroll
   - Gráficos táctiles
   - Filtros en modal

3. **Configuración**
   - Wizard paso a paso
   - Formularios simples
   - Validación en tiempo real

---

## ✅ Checklist de Flujos

### ✅ Flujos Principales
- [x] Decisión diaria documentado
- [x] Análisis histórico documentado
- [x] Configuración de estrategias documentado
- [x] Backtest documentado
- [x] Configuración del sistema documentado
- [x] Notificaciones documentado
- [x] Error y recuperación documentado

### ✅ Optimizaciones
- [x] Tiempos objetivo definidos
- [x] Puntos de fricción identificados
- [x] Soluciones propuestas
- [x] Shortcuts definidos
- [x] Progressive disclosure
- [x] Smart defaults

### ✅ Responsive
- [x] Mobile optimizations
- [x] Touch interactions
- [x] Simplified flows

---

**Status**: ✅ COMPLETADO  
**Epic**: 0.2 - Prototipos UI/UX (13 puntos)  
**Duración**: 2-3 días

**Próximo**: Prototipo navegable y componentes reutilizables