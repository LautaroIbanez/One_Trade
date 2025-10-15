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

## Configuración del Backend

El frontend requiere un backend activo para funcionar. Configure la URL del API en el archivo de entorno:

### Archivo de Entorno

Crear archivo `.env.local` en el directorio `frontend/`:
```bash
VITE_API_URL=http://localhost:8000/api/v1
```

Para producción, actualizar la variable `VITE_API_URL` con la URL apropiada del backend en producción.

## Cambios Recientes

### Migración a API Real (2025-10-15)

Eliminación completa de la capa mock y migración a integración real con el backend.

**Cambios Principales**:

1. **Cliente API Centralizado** (`src/lib/api-client.ts`)
   - Wrapper sobre `fetch` con manejo de errores
   - Configuración centralizada de base URL
   - Tipado fuerte de respuestas

2. **Hooks de Producción**
   - `useBacktestsApi`: Backtests y comparación de estrategias
   - `useRecommendations`: Recomendaciones mejoradas
   - `useMarketStats`: Estadísticas de mercado en tiempo real

3. **Tipos TypeScript Alineados** (`src/types/backtests.ts`)
   - Interfaces que reflejan esquemas del backend
   - Funciones de parsing para porcentajes/números
   - Normalización de respuestas

4. **Componentes Actualizados**
   - `BacktestRunner`: Usa datos reales del backend
   - `BacktestComparison`: Ejecuta comparaciones reales
   - `EnhancedRecommendations`: Sin dependencia de mocks
   - `RealTimeStats`: Calcula con datos reales

**Archivos Eliminados**:
- `src/hooks/useMockData.ts` (reemplazado por hooks de producción)
- `docs/frontend-mocks.md` (ya no relevante)

**Documentación Nueva**:
- `docs/QA_BACKTEST_SECTION.md`: Procedimiento QA manual

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

