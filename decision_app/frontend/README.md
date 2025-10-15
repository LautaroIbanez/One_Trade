# Trading Decision Frontend

Frontend de React + TypeScript + Vite para la aplicación de decisiones de trading.

## Características

- **Recomendaciones en Tiempo Real**: Visualización de recomendaciones de trading con análisis multi-estrategia
- **Modo Mock Completo**: Sistema de datos simulados para desarrollo sin backend
- **Gestión de Riesgos**: Evaluación de riesgo y contexto de mercado
- **Backtesting Interactivo**: Ejecución y visualización de backtests
- **UI Moderna**: Interfaz construida con TailwindCSS y componentes reutilizables

## Inicio Rápido

```bash
# Instalar dependencias
npm install

# Modo desarrollo (con mock data)
npm run dev

# Build de producción
npm run build

# Ejecutar tests
npm run test
```

## Estructura del Proyecto

```
src/
├── components/          # Componentes React
│   ├── EnhancedRecommendations.tsx
│   ├── BacktestRunner.tsx
│   ├── layout/          # Componentes de layout
│   └── ui/              # Componentes UI base
├── hooks/               # Custom hooks
│   └── useMockData.ts   # Hook para datos mock y API
├── lib/                 # Utilidades
│   └── formatters.ts    # Helpers de formateo seguros
├── pages/               # Páginas/vistas
├── types/               # Tipos TypeScript compartidos
│   └── recommendations.ts
└── test/                # Configuración de tests
```

## Modo Mock

El frontend puede operar en modo mock sin necesidad de un backend activo. Esto es útil para:
- Desarrollo de UI sin dependencias
- Testing de componentes
- Demos y presentaciones

### Activar/Desactivar Mock Mode

En `src/hooks/useMockData.ts`:
```typescript
const MOCK_MODE = true;  // true = mock, false = API real
```

Ver [docs/frontend-mocks.md](docs/frontend-mocks.md) para documentación completa.

## Cambios Recientes (Corrección Pantalla en Blanco)

### Problema Resuelto
La aplicación quedaba en blanco al intentar acceder a propiedades `undefined` en el componente `EnhancedRecommendations`.

### Solución Implementada

1. **Tipos Compartidos** (`src/types/recommendations.ts`)
   - Interfaces TypeScript formalizadas
   - Valores por defecto documentados
   - Tipos consistentes entre componentes

2. **Hook Mock Mejorado** (`src/hooks/useMockData.ts`)
   - Ahora devuelve objetos `EnhancedRecommendation` completos
   - Generación dinámica de todos los campos requeridos
   - Datos realistas con variación controlada

3. **Helpers de Formateo** (`src/lib/formatters.ts`)
   - Funciones seguras que manejan valores null/undefined
   - `formatPrice()`, `formatPercentage()`, `formatNumber()`
   - `safeGet()` para acceso seguro a valores

4. **Componente Resiliente** (`src/components/EnhancedRecommendations.tsx`)
   - Uso de optional chaining (`?.`)
   - Nullish coalescing (`??`)
   - Validación de arrays antes de iteración
   - Mensajes de fallback cuando faltan datos

5. **Tests Agregados**
   - `src/lib/__tests__/formatters.test.ts`
   - `src/components/__tests__/EnhancedRecommendations.test.tsx`

### Archivos Creados/Modificados

#### Nuevos Archivos
- `src/types/recommendations.ts`
- `src/lib/formatters.ts`
- `src/lib/__tests__/formatters.test.ts`
- `src/components/__tests__/EnhancedRecommendations.test.tsx`
- `docs/frontend-mocks.md`

#### Archivos Modificados
- `src/hooks/useMockData.ts`: Generación completa de datos mock
- `src/components/EnhancedRecommendations.tsx`: Uso de tipos y helpers seguros

## Tecnologías

- **React 18**: Framework UI
- **TypeScript**: Tipado estático
- **Vite**: Build tool y dev server
- **TailwindCSS**: Estilos utility-first
- **Vitest**: Testing framework
- **React Testing Library**: Testing de componentes
- **Lucide React**: Íconos

## Scripts Disponibles

```bash
npm run dev          # Servidor de desarrollo
npm run build        # Build de producción
npm run preview      # Preview del build
npm run test         # Ejecutar tests
npm run lint         # Linter ESLint
npm run type-check   # Verificación de tipos TypeScript
```

## Documentación Adicional

- [Frontend Mocks](docs/frontend-mocks.md) - Guía completa del sistema de datos mock
- [Arquitectura](../docs/ARCHITECTURE.md) - Arquitectura general del sistema
- [Guía de Desarrollo](../docs/DEVELOPMENT.md) - Guía para desarrolladores

## Buenas Prácticas

1. **Siempre usar helpers de formateo** para valores mostrados al usuario
2. **Verificar tipos opcionales** con `?.` y `??`
3. **Importar tipos** desde `src/types/recommendations.ts`
4. **Escribir tests** para nuevos componentes y funciones
5. **Documentar cambios** significativos en la arquitectura

## Troubleshooting

### Pantalla en Blanco
- Verificar console de DevTools para errores
- Asegurar que `MOCK_MODE = true` si no hay backend
- Verificar imports de helpers de formateo

### Errores de TypeScript
- Ejecutar `npm run type-check`
- Verificar imports de tipos desde `src/types/`
- Revisar que valores opcionales usen `?.` o `??`

### Tests Fallan
- Ejecutar `npm install` para actualizar dependencias
- Verificar que mocks en tests devuelvan objetos completos
- Consultar ejemplos en `src/**/__tests__/`

## Contribuir

Al agregar nuevas features:
1. Crear tipos en `src/types/` si son compartidos
2. Agregar helpers de formateo si manejan valores opcionales
3. Escribir tests para funcionalidad crítica
4. Actualizar documentación relevante
5. Verificar que funcione en modo mock y modo API

## Licencia

Ver LICENSE en el directorio raíz del proyecto.

