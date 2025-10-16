# One Trade Decision App - Frontend Backend Integration

Esta documentación explica cómo configurar y ejecutar la aplicación completa con el frontend conectado al backend real.

## 🚀 Configuración Rápida

### 1. Configurar Variables de Entorno

Crea un archivo `.env` en el directorio `decision_app/frontend/`:

```bash
# Backend API URL
VITE_API_URL=http://localhost:8001/api/v1
```

### 2. Ejecutar Backend

```bash
# Activar entorno virtual
.venv\Scripts\Activate.ps1

# Ejecutar backend completo
python backend_complete.py
```

El backend estará disponible en: `http://localhost:8001`

### 3. Ejecutar Frontend

```bash
# En otra terminal, ir al directorio frontend
cd decision_app/frontend

# Instalar dependencias (si es necesario)
npm install

# Ejecutar en modo desarrollo
npm run dev
```

El frontend estará disponible en: `http://localhost:3000`

## 📡 Endpoints Disponibles

### Recomendaciones
- `GET /api/v1/enhanced-recommendations/supported-symbols` - Símbolos disponibles
- `GET /api/v1/enhanced-recommendations/generate/{symbol}` - Recomendación individual
- `GET /api/v1/enhanced-recommendations/batch/{symbols}` - Recomendaciones en lote

### Backtests
- `GET /api/v1/backtests/strategies` - Estrategias disponibles
- `GET /api/v1/backtests/symbols` - Símbolos para backtests
- `GET /api/v1/backtests/quick-test/{symbol}` - Backtest rápido
- `POST /api/v1/backtests/run` - Backtest completo

### Estadísticas
- `GET /api/v1/stats` - Estadísticas generales
- `GET /health` - Health check

## 🔧 Configuración Avanzada

### Variables de Entorno

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `VITE_API_URL` | URL base del backend API | `http://localhost:8001/api/v1` |

### Scripts Disponibles

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directs --max-warnings 0",
    "start:dev": "VITE_API_URL=http://localhost:8001/api/v1 vite"
  }
}
```

## 🧪 Testing

### Ejecutar Tests
```bash
npm run test
npm run lint
```

### Verificar Conexión Backend
```bash
curl http://localhost:8001/health
curl http://localhost:8001/api/v1/enhanced-recommendations/supported-symbols
```

## 📊 Funcionalidades

### Dashboard
- ✅ Estadísticas en tiempo real
- ✅ Recomendaciones actualizadas
- ✅ Botones de refresh
- ✅ Manejo de errores

### Backtests
- ✅ Runner individual
- ✅ Comparación de estrategias
- ✅ Backtests completos
- ✅ Métricas detalladas

### Recomendaciones
- ✅ Múltiples estrategias
- ✅ Análisis de riesgo
- ✅ Señales técnicas
- ✅ Contexto de mercado

## 🐛 Troubleshooting

### Backend no responde
1. Verificar que el puerto 8001 esté libre
2. Comprobar que el entorno virtual esté activado
3. Revisar logs del backend

### Frontend no conecta
1. Verificar `VITE_API_URL` en `.env`
2. Comprobar que el backend esté ejecutándose
3. Revisar consola del navegador para errores CORS

### Errores de CORS
El backend está configurado para permitir conexiones desde:
- `http://localhost:3000`
- `http://localhost:5173`
- `http://127.0.0.1:3000`
- `http://127.0.0.1:5173`

## 📝 Notas de Desarrollo

### Cliente HTTP Centralizado
- Usa `apiClient` en `src/lib/api-client.ts`
- Manejo automático de errores
- Retry automático con backoff exponencial

### Hooks Personalizados
- `useRecommendations` - Para recomendaciones
- `useBacktestsApi` - Para backtests
- Estados de loading/error unificados

### Componentes Reutilizables
- `ApiErrorState` - Para errores de API
- `EmptyState` - Para estados vacíos
- `LoadingState` - Para estados de carga

