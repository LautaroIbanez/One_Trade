# Frontend Mock Data Guide

Este documento explica cómo funciona el sistema de datos mock en el frontend de la aplicación de decisiones de trading.

## Resumen

El frontend puede operar en dos modos:
- **Mock Mode** (`MOCK_MODE = true`): Usa datos simulados localmente
- **API Mode** (`MOCK_MODE = false`): Se conecta al backend real

## Contrato de Datos

Todos los componentes que muestran recomendaciones esperan objetos que cumplen con la interfaz `EnhancedRecommendation` definida en `src/types/recommendations.ts`.

### Estructura de EnhancedRecommendation

```typescript
interface EnhancedRecommendation {
  symbol: string;                      // Ej: 'BTCUSDT'
  current_price: number;                // Precio actual
  recommendation: string;               // 'BUY', 'SELL', 'HOLD', etc.
  confidence: number;                   // 0-1 (porcentaje como decimal)
  reasoning: string;                    // Explicación textual
  risk_assessment: RiskAssessment;      // Evaluación de riesgo
  strategy_signals: StrategySignal[];   // Señales de estrategias individuales
  scores: SignalScores;                 // Puntajes BUY/SELL/HOLD
  market_context: MarketContext;        // Contexto de mercado
  timestamp: string;                    // ISO timestamp
}
```

### Interfaces Relacionadas

Ver `src/types/recommendations.ts` para las definiciones completas de:
- `StrategySignal`
- `RiskAssessment`
- `MarketContext`
- `SignalScores`

## Hook useMockData

El hook `useMockData` (ubicado en `src/hooks/useMockData.ts`) es el punto central para obtener datos.

### Configuración

```typescript
const MOCK_MODE = true;  // Cambiar a false para usar API real
const MOCK_DELAY = 1000; // Delay simulado en ms
```

### Funciones Principales

#### getRecommendation(symbol, timeframe, days)

Devuelve un objeto `EnhancedRecommendation` completo con todos los campos requeridos:
- `current_price`: Basado en precios mock con variación aleatoria
- `reasoning`: Generado dinámicamente basado en indicadores
- `scores`: Calculados según la recomendación
- `risk_assessment`: Determinado por el nivel de confianza
- `market_context`: Generado con valores aleatorios controlados

#### getSupportedSymbols()

Devuelve la lista de símbolos soportados:
```typescript
['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT']
```

### Extensión de Datos Mock

Para agregar nuevos símbolos o modificar datos mock:

1. Actualizar `mockPrices` con el precio base del símbolo
2. Agregar entrada en `mockRecommendations` con la configuración deseada
3. Agregar el símbolo a `mockSymbols`

```typescript
const mockPrices: Record<string, number> = {
  BTCUSDT: 45000,
  NUEVO_SIMBOLO: 100,  // Agregar aquí
};

const mockRecommendations = {
  NUEVO_SIMBOLO: {  // Agregar aquí
    recommendation: 'BUY',
    confidence: 0.70,
    details: {
      strategy: 'RSI',
      indicators: { rsi: 40, macd: 0.001, bollinger_position: 0.4 }
    }
  }
};
```

## Helpers de Formateo

Para manejar valores potencialmente `null` o `undefined`, se proporcionan helpers en `src/lib/formatters.ts`:

### Funciones Disponibles

- `formatPrice(price)`: Formatea precios con símbolo de dólar y separadores
- `formatPercentage(value)`: Convierte decimal a porcentaje formateado
- `formatNumber(value, decimals)`: Formatea números con decimales específicos
- `formatRiskLevel(level)`: Normaliza niveles de riesgo a mayúsculas
- `formatTrend(trend)`: Normaliza tendencias de mercado
- `safeGet(value, defaultValue)`: Retorna valor o default si es null/undefined

### Ejemplo de Uso

```typescript
import { formatPrice, formatPercentage } from '@/lib/formatters';

// En lugar de:
const price = rec.current_price.toLocaleString(); // ERROR si undefined

// Usar:
const price = formatPrice(rec.current_price); // Devuelve 'N/A' si es undefined
```

## Componentes Resilientes

El componente `EnhancedRecommendations` implementa las siguientes prácticas:

1. **Uso de Optional Chaining**: `rec.market_context?.trend`
2. **Nullish Coalescing**: `rec.recommendation ?? 'HOLD'`
3. **Helpers de Formateo**: Para todos los valores numéricos
4. **Valores por Defecto**: Definidos en `src/types/recommendations.ts`

### Ejemplo de Renderizado Seguro

```typescript
// Acceso seguro a propiedades anidadas
<div>{formatTrend(rec.market_context?.trend)}</div>

// Con fallback explícito
<div>{rec.reasoning ?? 'No reasoning available'}</div>

// Verificación de arrays antes de map
{rec.strategy_signals && rec.strategy_signals.length > 0 ? (
  <div>{rec.strategy_signals.map(...)}</div>
) : (
  <p>No strategy signals available</p>
)}
```

## Modo Mock vs API Real

### Activar Modo Mock

En `src/hooks/useMockData.ts`:
```typescript
const MOCK_MODE = true;
```

### Desactivar Modo Mock (API Real)

1. Configurar backend en `http://localhost:8000`
2. En `src/hooks/useMockData.ts`:
```typescript
const MOCK_MODE = false;
```

El hook manejará automáticamente las llamadas al backend en lugar de generar datos mock.

## Testing

Los tests están ubicados en:
- `src/lib/__tests__/formatters.test.ts`: Tests de helpers de formateo
- `src/components/__tests__/EnhancedRecommendations.test.tsx`: Tests del componente

### Ejecutar Tests

```bash
cd decision_app/frontend
npm run test
```

### Estrategia de Testing

Los tests verifican:
1. Formateo correcto de valores válidos
2. Manejo graceful de valores null/undefined/NaN
3. Renderizado sin errores en modo mock
4. Presencia de elementos clave en el DOM

## Troubleshooting

### Pantalla en Blanco

Si la pantalla queda en blanco:
1. Abrir DevTools Console (F12)
2. Verificar errores de tipo "Cannot read property ... of undefined"
3. Asegurar que `MOCK_MODE = true` en `useMockData.ts`
4. Verificar que todos los helpers de formateo estén importados

### Datos Incompletos

Si faltan datos en las tarjetas:
1. Verificar que `getRecommendation` devuelve un objeto completo
2. Revisar que el componente use los helpers de formateo
3. Consultar valores por defecto en `src/types/recommendations.ts`

### Errores de Tipo

Si TypeScript reporta errores:
1. Verificar que todos los imports usen los tipos de `src/types/recommendations.ts`
2. Asegurar que los helpers manejen tipos opcionales (`Type | null | undefined`)
3. Ejecutar `npm run type-check` para ver todos los errores

## Mejores Prácticas

1. **Siempre usar helpers de formateo** para valores mostrados al usuario
2. **Verificar arrays antes de map** para evitar errores en runtime
3. **Usar optional chaining** (`?.`) para acceso a propiedades anidadas
4. **Definir valores por defecto** en las interfaces para documentación
5. **Mantener consistencia** entre datos mock y datos de API real

## Próximos Pasos

Para mejorar el sistema de mocks:
1. Agregar más variabilidad en datos generados
2. Implementar persistencia de estado entre recargas
3. Crear utilidades para generar escenarios específicos (crash, rally, etc.)
4. Añadir modo de "replay" de datos históricos reales

