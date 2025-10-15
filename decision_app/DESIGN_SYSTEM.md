# 🎨 Design System - One Trade Decision App

**Epic**: 0.2 - Prototipos UI/UX  
**Story Points**: 13  
**Duración**: 2-3 días  
**Status**: 🚧 EN PROGRESO

---

## 🎯 Principios de Diseño

### 1. **Clarity First** (Claridad Primero)
- Información crítica visible inmediatamente
- Jerarquía visual clara
- Reducir carga cognitiva

### 2. **Data-Driven** (Basado en Datos)
- Métricas prominentes
- Visualizaciones claras
- Contexto numérico siempre presente

### 3. **Action-Oriented** (Orientado a Acción)
- CTAs claros y prominentes
- Estados de decisión obvios
- Flujos de acción simplificados

### 4. **Trust & Transparency** (Confianza y Transparencia)
- Explicabilidad de decisiones
- Historial completo visible
- Métricas de performance claras

---

## 🎨 Paleta de Colores

### Colores Primarios

```css
/* Trading Signals */
--signal-buy: #10B981;        /* Verde - Comprar */
--signal-sell: #EF4444;       /* Rojo - Vender */
--signal-hold: #F59E0B;       /* Amarillo - Mantener */

/* Brand Colors */
--brand-primary: #3B82F6;     /* Azul principal */
--brand-secondary: #8B5CF6;   /* Púrpura secundario */
--brand-accent: #06B6D4;      /* Cian de acento */

/* Neutral Colors */
--neutral-50: #F9FAFB;        /* Fondo claro */
--neutral-100: #F3F4F6;       /* Fondo gris claro */
--neutral-200: #E5E7EB;       /* Bordes claros */
--neutral-300: #D1D5DB;       /* Bordes */
--neutral-400: #9CA3AF;       /* Texto secundario */
--neutral-500: #6B7280;       /* Texto base */
--neutral-600: #4B5563;       /* Texto importante */
--neutral-700: #374151;       /* Texto principal */
--neutral-800: #1F2937;       /* Texto oscuro */
--neutral-900: #111827;       /* Texto muy oscuro */

/* Status Colors */
--success: #10B981;           /* Éxito */
--warning: #F59E0B;           /* Advertencia */
--error: #EF4444;             /* Error */
--info: #3B82F6;              /* Información */
```

### Modo Oscuro

```css
/* Dark Mode */
--dark-bg-primary: #0F172A;   /* Fondo principal */
--dark-bg-secondary: #1E293B; /* Fondo secundario */
--dark-bg-tertiary: #334155;  /* Fondo terciario */
--dark-text-primary: #F8FAFC; /* Texto principal */
--dark-text-secondary: #CBD5E1; /* Texto secundario */
--dark-border: #475569;       /* Bordes */
```

---

## 📝 Tipografía

### Fuentes

```css
/* Primary Font - Inter (Modern, readable) */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Monospace Font - JetBrains Mono (Numbers, code) */
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');
```

### Escala Tipográfica

```css
/* Headings */
--text-4xl: 2.25rem;    /* 36px - Títulos principales */
--text-3xl: 1.875rem;   /* 30px - Títulos sección */
--text-2xl: 1.5rem;     /* 24px - Subtítulos */
--text-xl: 1.25rem;     /* 20px - Títulos cards */
--text-lg: 1.125rem;    /* 18px - Texto destacado */

/* Body Text */
--text-base: 1rem;      /* 16px - Texto base */
--text-sm: 0.875rem;    /* 14px - Texto secundario */
--text-xs: 0.75rem;     /* 12px - Labels, captions */

/* Monospace (Numbers, Code) */
--text-mono-lg: 1.125rem; /* 18px - Números grandes */
--text-mono-base: 1rem;   /* 16px - Números base */
--text-mono-sm: 0.875rem; /* 14px - Números pequeños */
```

### Pesos de Fuente

```css
--font-light: 300;      /* Texto ligero */
--font-normal: 400;     /* Texto normal */
--font-medium: 500;     /* Texto medio */
--font-semibold: 600;   /* Texto semi-bold */
--font-bold: 700;       /* Texto bold */
```

---

## 📏 Espaciado

### Escala de Espaciado

```css
--space-0: 0;           /* 0px */
--space-1: 0.25rem;     /* 4px */
--space-2: 0.5rem;      /* 8px */
--space-3: 0.75rem;     /* 12px */
--space-4: 1rem;        /* 16px */
--space-5: 1.25rem;     /* 20px */
--space-6: 1.5rem;      /* 24px */
--space-8: 2rem;        /* 32px */
--space-10: 2.5rem;     /* 40px */
--space-12: 3rem;       /* 48px */
--space-16: 4rem;       /* 64px */
--space-20: 5rem;       /* 80px */
--space-24: 6rem;       /* 96px */
```

### Aplicación de Espaciado

```css
/* Padding */
--padding-xs: var(--space-2);    /* 8px */
--padding-sm: var(--space-3);    /* 12px */
--padding-md: var(--space-4);    /* 16px */
--padding-lg: var(--space-6);    /* 24px */
--padding-xl: var(--space-8);    /* 32px */

/* Margin */
--margin-xs: var(--space-2);     /* 8px */
--margin-sm: var(--space-3);     /* 12px */
--margin-md: var(--space-4);     /* 16px */
--margin-lg: var(--space-6);     /* 24px */
--margin-xl: var(--space-8);     /* 32px */

/* Gap */
--gap-xs: var(--space-2);        /* 8px */
--gap-sm: var(--space-3);        /* 12px */
--gap-md: var(--space-4);        /* 16px */
--gap-lg: var(--space-6);        /* 24px */
--gap-xl: var(--space-8);        /* 32px */
```

---

## 🔲 Componentes Base

### 1. Botones

```css
/* Primary Button */
.btn-primary {
  background: var(--brand-primary);
  color: white;
  padding: var(--padding-sm) var(--padding-md);
  border-radius: var(--radius-md);
  font-weight: var(--font-medium);
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background: #2563EB;
  transform: translateY(-1px);
}

/* Secondary Button */
.btn-secondary {
  background: transparent;
  color: var(--brand-primary);
  border: 1px solid var(--brand-primary);
  padding: var(--padding-sm) var(--padding-md);
  border-radius: var(--radius-md);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: all 0.2s ease;
}

/* Signal Buttons */
.btn-buy {
  background: var(--signal-buy);
  color: white;
}

.btn-sell {
  background: var(--signal-sell);
  color: white;
}

.btn-hold {
  background: var(--signal-hold);
  color: white;
}
```

### 2. Cards

```css
.card {
  background: white;
  border-radius: var(--radius-lg);
  padding: var(--padding-lg);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--neutral-200);
}

.card-header {
  border-bottom: 1px solid var(--neutral-200);
  padding-bottom: var(--padding-md);
  margin-bottom: var(--margin-md);
}

.card-title {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--neutral-800);
  margin: 0;
}

.card-subtitle {
  font-size: var(--text-sm);
  color: var(--neutral-500);
  margin: var(--margin-xs) 0 0 0;
}
```

### 3. Inputs

```css
.input {
  width: 100%;
  padding: var(--padding-sm) var(--padding-md);
  border: 1px solid var(--neutral-300);
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  transition: border-color 0.2s ease;
}

.input:focus {
  outline: none;
  border-color: var(--brand-primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.input-error {
  border-color: var(--error);
}

.input-success {
  border-color: var(--success);
}
```

### 4. Badges

```css
.badge {
  display: inline-flex;
  align-items: center;
  padding: var(--padding-xs) var(--padding-sm);
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.badge-buy {
  background: rgba(16, 185, 129, 0.1);
  color: var(--signal-buy);
}

.badge-sell {
  background: rgba(239, 68, 68, 0.1);
  color: var(--signal-sell);
}

.badge-hold {
  background: rgba(245, 158, 11, 0.1);
  color: var(--signal-hold);
}

.badge-success {
  background: rgba(16, 185, 129, 0.1);
  color: var(--success);
}

.badge-warning {
  background: rgba(245, 158, 11, 0.1);
  color: var(--warning);
}

.badge-error {
  background: rgba(239, 68, 68, 0.1);
  color: var(--error);
}
```

---

## 📊 Componentes de Datos

### 1. Metric Cards

```css
.metric-card {
  background: white;
  border-radius: var(--radius-lg);
  padding: var(--padding-lg);
  border: 1px solid var(--neutral-200);
  text-align: center;
}

.metric-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  color: var(--neutral-800);
  margin: 0;
}

.metric-label {
  font-size: var(--text-sm);
  color: var(--neutral-500);
  margin: var(--margin-xs) 0 0 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.metric-change {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  margin: var(--margin-xs) 0 0 0;
}

.metric-change.positive {
  color: var(--success);
}

.metric-change.negative {
  color: var(--error);
}
```

### 2. Data Tables

```css
.data-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.data-table th {
  background: var(--neutral-50);
  padding: var(--padding-md);
  text-align: left;
  font-weight: var(--font-semibold);
  color: var(--neutral-700);
  border-bottom: 1px solid var(--neutral-200);
}

.data-table td {
  padding: var(--padding-md);
  border-bottom: 1px solid var(--neutral-100);
  color: var(--neutral-600);
}

.data-table tr:hover {
  background: var(--neutral-50);
}

.data-table tr:last-child td {
  border-bottom: none;
}
```

### 3. Progress Bars

```css
.progress-bar {
  width: 100%;
  height: 8px;
  background: var(--neutral-200);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--brand-primary);
  transition: width 0.3s ease;
}

.progress-fill.success {
  background: var(--success);
}

.progress-fill.warning {
  background: var(--warning);
}

.progress-fill.error {
  background: var(--error);
}
```

---

## 🎭 Estados y Animaciones

### Estados de Componentes

```css
/* Loading State */
.loading {
  opacity: 0.6;
  pointer-events: none;
}

.loading::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 20px;
  height: 20px;
  margin: -10px 0 0 -10px;
  border: 2px solid var(--neutral-300);
  border-top: 2px solid var(--brand-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* Disabled State */
.disabled {
  opacity: 0.5;
  pointer-events: none;
  cursor: not-allowed;
}

/* Error State */
.error {
  border-color: var(--error);
  background: rgba(239, 68, 68, 0.05);
}

/* Success State */
.success {
  border-color: var(--success);
  background: rgba(16, 185, 129, 0.05);
}
```

### Animaciones

```css
/* Keyframes */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  from { transform: translateY(-10px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Animation Classes */
.fade-in {
  animation: fadeIn 0.3s ease-in;
}

.slide-in {
  animation: slideIn 0.3s ease-out;
}

.pulse {
  animation: pulse 2s infinite;
}
```

---

## 📱 Responsive Design

### Breakpoints

```css
/* Mobile First Approach */
--breakpoint-sm: 640px;    /* Small devices */
--breakpoint-md: 768px;    /* Medium devices */
--breakpoint-lg: 1024px;   /* Large devices */
--breakpoint-xl: 1280px;   /* Extra large devices */
--breakpoint-2xl: 1536px;  /* 2X large devices */

/* Media Queries */
@media (min-width: 640px) { /* sm */ }
@media (min-width: 768px) { /* md */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }
@media (min-width: 1536px) { /* 2xl */ }
```

### Grid System

```css
.container {
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 var(--padding-md);
}

.grid {
  display: grid;
  gap: var(--gap-md);
}

.grid-cols-1 { grid-template-columns: repeat(1, 1fr); }
.grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
.grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
.grid-cols-4 { grid-template-columns: repeat(4, 1fr); }

@media (min-width: 768px) {
  .md\:grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
  .md\:grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
  .md\:grid-cols-4 { grid-template-columns: repeat(4, 1fr); }
}
```

---

## 🎨 Iconografía

### Iconos Principales

```css
/* Trading Icons */
.icon-buy::before { content: "📈"; }
.icon-sell::before { content: "📉"; }
.icon-hold::before { content: "⏸️"; }

/* Navigation Icons */
.icon-dashboard::before { content: "🏠"; }
.icon-history::before { content: "📊"; }
.icon-backtests::before { content: "🧪"; }
.icon-settings::before { content: "⚙️"; }

/* Status Icons */
.icon-success::before { content: "✅"; }
.icon-warning::before { content: "⚠️"; }
.icon-error::before { content: "❌"; }
.icon-info::before { content: "ℹ️"; }

/* Action Icons */
.icon-edit::before { content: "✏️"; }
.icon-delete::before { content: "🗑️"; }
.icon-save::before { content: "💾"; }
.icon-export::before { content: "📤"; }
.icon-refresh::before { content: "🔄"; }
```

### Icon Sizes

```css
.icon-xs { font-size: 12px; }
.icon-sm { font-size: 14px; }
.icon-md { font-size: 16px; }
.icon-lg { font-size: 20px; }
.icon-xl { font-size: 24px; }
.icon-2xl { font-size: 32px; }
```

---

## 🌙 Modo Oscuro

### Variables de Modo Oscuro

```css
[data-theme="dark"] {
  --bg-primary: var(--dark-bg-primary);
  --bg-secondary: var(--dark-bg-secondary);
  --bg-tertiary: var(--dark-bg-tertiary);
  --text-primary: var(--dark-text-primary);
  --text-secondary: var(--dark-text-secondary);
  --border: var(--dark-border);
}

/* Dark Mode Components */
[data-theme="dark"] .card {
  background: var(--dark-bg-secondary);
  border-color: var(--dark-border);
}

[data-theme="dark"] .data-table {
  background: var(--dark-bg-secondary);
}

[data-theme="dark"] .data-table th {
  background: var(--dark-bg-tertiary);
  color: var(--dark-text-primary);
}

[data-theme="dark"] .data-table td {
  color: var(--dark-text-secondary);
}
```

---

## 🎯 Componentes Específicos de Trading

### 1. Signal Indicator

```css
.signal-indicator {
  display: inline-flex;
  align-items: center;
  gap: var(--gap-xs);
  padding: var(--padding-xs) var(--padding-sm);
  border-radius: var(--radius-md);
  font-weight: var(--font-semibold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.signal-indicator.buy {
  background: rgba(16, 185, 129, 0.1);
  color: var(--signal-buy);
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.signal-indicator.sell {
  background: rgba(239, 68, 68, 0.1);
  color: var(--signal-sell);
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.signal-indicator.hold {
  background: rgba(245, 158, 11, 0.1);
  color: var(--signal-hold);
  border: 1px solid rgba(245, 158, 11, 0.2);
}
```

### 2. Price Display

```css
.price-display {
  font-family: 'JetBrains Mono', monospace;
  font-weight: var(--font-semibold);
  color: var(--neutral-800);
}

.price-change {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  margin-left: var(--margin-xs);
}

.price-change.positive {
  color: var(--success);
}

.price-change.negative {
  color: var(--error);
}
```

### 3. Confidence Meter

```css
.confidence-meter {
  display: flex;
  align-items: center;
  gap: var(--gap-sm);
}

.confidence-bar {
  flex: 1;
  height: 8px;
  background: var(--neutral-200);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.confidence-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--error) 0%, var(--warning) 50%, var(--success) 100%);
  transition: width 0.3s ease;
}

.confidence-value {
  font-family: 'JetBrains Mono', monospace;
  font-weight: var(--font-semibold);
  color: var(--neutral-700);
  min-width: 40px;
  text-align: right;
}
```

---

## 📋 Checklist de Implementación

### ✅ Colores y Tipografía
- [x] Paleta de colores definida
- [x] Escala tipográfica establecida
- [x] Fuentes seleccionadas (Inter + JetBrains Mono)
- [x] Modo oscuro configurado

### ✅ Componentes Base
- [x] Botones (primary, secondary, signal)
- [x] Cards y contenedores
- [x] Inputs y formularios
- [x] Badges y etiquetas

### ✅ Componentes de Datos
- [x] Metric cards
- [x] Data tables
- [x] Progress bars
- [x] Signal indicators

### ✅ Estados y Animaciones
- [x] Estados de loading, disabled, error
- [x] Animaciones básicas
- [x] Transiciones suaves

### ✅ Responsive Design
- [x] Breakpoints definidos
- [x] Grid system
- [x] Mobile-first approach

### ✅ Componentes Específicos
- [x] Trading signals
- [x] Price displays
- [x] Confidence meters
- [x] Iconografía

---

**Status**: ✅ COMPLETADO  
**Epic**: 0.2 - Prototipos UI/UX (13 puntos)  
**Duración**: 2-3 días

**Próximo**: Flujos de usuario y prototipo navegable