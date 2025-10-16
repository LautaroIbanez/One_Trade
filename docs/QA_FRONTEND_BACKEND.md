# QA Checklist - Frontend Backend Integration

Este checklist verifica que la integración entre frontend y backend funcione correctamente.

## 🚀 Setup Inicial

### ✅ Backend
- [ ] Backend ejecutándose en puerto 8001
- [ ] Health check responde: `curl http://localhost:8001/health`
- [ ] API docs disponibles: `http://localhost:8001/docs`
- [ ] CORS configurado correctamente

### ✅ Frontend
- [ ] Frontend ejecutándose en puerto 3000
- [ ] Variables de entorno configuradas (`VITE_API_URL`)
- [ ] No errores en consola del navegador
- [ ] Página carga completamente

## 📊 Dashboard Tests

### ✅ Estadísticas en Tiempo Real
- [ ] **Carga inicial**: Las estadísticas se muestran al cargar la página
- [ ] **Datos reales**: Valores numéricos (no 0 o NaN)
- [ ] **Refresh manual**: Botón "Refresh" actualiza los datos
- [ ] **Auto-refresh**: Datos se actualizan automáticamente cada 5 minutos
- [ ] **Timestamp**: Muestra "Last updated" con hora actual
- [ ] **Estados de carga**: Skeleton loading durante carga inicial
- [ ] **Estados de error**: Mensaje de error si falla la conexión

### ✅ Recomendaciones en Tiempo Real
- [ ] **Carga inicial**: Recomendaciones se muestran al cargar
- [ ] **Datos completos**: Cada recomendación tiene símbolo, precio, señal, confianza
- [ ] **Estrategias múltiples**: Muestra señales de diferentes estrategias
- [ ] **Análisis de riesgo**: Niveles de riesgo (LOW/MEDIUM/HIGH)
- [ ] **Contexto de mercado**: Trend, volatilidad, performance 24h
- [ ] **Refresh manual**: Botón "Refresh" actualiza recomendaciones
- [ ] **Manejo de errores**: Tarjetas amarillas para símbolos con error
- [ ] **Estados de carga**: Loading spinner durante carga

## 🔄 Backtests Tests

### ✅ Backtest Runner
- [ ] **Carga de datos**: Símbolos y estrategias se cargan automáticamente
- [ ] **Selección automática**: Primera estrategia y símbolo seleccionados por defecto
- [ ] **Quick Backtest**: Ejecuta correctamente con parámetros seleccionados
- [ ] **Full Backtest**: Ejecuta backtest completo con fechas
- [ ] **Compare Strategies**: Compara múltiples estrategias
- [ ] **Resultados detallados**: Muestra métricas completas
- [ ] **Manejo de errores**: Mensajes de error claros
- [ ] **Estados de carga**: Loading states durante ejecución

### ✅ Backtest Comparison
- [ ] **Configuración automática**: Genera tests automáticamente
- [ ] **Ejecución múltiple**: Ejecuta múltiples combinaciones
- [ ] **Resultados comparativos**: Muestra resultados lado a lado
- [ ] **Estadísticas resumen**: Mejores rendimientos identificados
- [ ] **Manejo de fallos**: Algunos tests pueden fallar, otros continúan
- [ ] **Progreso visual**: Muestra progreso durante ejecución

## 🔌 API Connection Tests

### ✅ Conectividad
- [ ] **Backend online**: Frontend puede conectarse al backend
- [ ] **Endpoints responden**: Todos los endpoints devuelven datos válidos
- [ ] **CORS funcionando**: No hay errores de CORS en consola
- [ ] **Headers correctos**: Content-Type y otros headers apropiados

### ✅ Manejo de Errores
- [ ] **Backend offline**: Mensajes de error apropiados cuando backend no responde
- [ ] **Endpoints no disponibles**: Fallback graceful cuando endpoints fallan
- [ ] **Datos inválidos**: Manejo de respuestas malformadas
- [ ] **Timeouts**: Manejo de requests que tardan demasiado

### ✅ Performance
- [ ] **Carga rápida**: Dashboard carga en menos de 3 segundos
- [ ] **Responsive**: Interfaz responde rápidamente a interacciones
- [ ] **Memory leaks**: No hay incremento continuo de memoria
- [ ] **Network efficiency**: Requests optimizados, no duplicados

## 🎯 User Experience Tests

### ✅ Navegación
- [ ] **Sidebar funcional**: Navegación entre secciones funciona
- [ ] **URLs correctas**: URLs cambian al navegar
- [ ] **Breadcrumbs**: Usuario sabe dónde está
- [ ] **Responsive**: Funciona en diferentes tamaños de pantalla

### ✅ Interacciones
- [ ] **Botones funcionales**: Todos los botones responden
- [ ] **Formularios**: Inputs y selects funcionan correctamente
- [ ] **Estados visuales**: Loading, success, error states claros
- [ ] **Feedback inmediato**: Usuario recibe feedback de acciones

### ✅ Datos en Tiempo Real
- [ ] **Actualizaciones**: Datos se actualizan automáticamente
- [ ] **Consistencia**: Datos coherentes entre secciones
- [ ] **Precisión**: Valores numéricos son realistas
- [ ] **Completitud**: No hay datos faltantes o placeholder

## 🐛 Error Scenarios

### ✅ Backend Desconectado
1. [ ] Detener backend
2. [ ] Refrescar frontend
3. [ ] Verificar mensajes de error apropiados
4. [ ] Verificar botones de retry funcionan
5. [ ] Reconectar backend
6. [ ] Verificar que datos se cargan nuevamente

### ✅ Datos Corruptos
1. [ ] Simular respuesta inválida del backend
2. [ ] Verificar manejo graceful de errores
3. [ ] Verificar que aplicación no crashea
4. [ ] Verificar mensajes de error informativos

### ✅ Network Issues
1. [ ] Simular conexión lenta
2. [ ] Verificar timeouts apropiados
3. [ ] Verificar loading states
4. [ ] Verificar que UI no se bloquea

## 📱 Cross-Browser Tests

### ✅ Navegadores
- [ ] **Chrome**: Funcionalidad completa
- [ ] **Firefox**: Funcionalidad completa
- [ ] **Safari**: Funcionalidad completa (si aplica)
- [ ] **Edge**: Funcionalidad completa

### ✅ Dispositivos
- [ ] **Desktop**: Experiencia completa
- [ ] **Tablet**: Interfaz responsive
- [ ] **Mobile**: Navegación y funcionalidad básica

## 🚀 Performance Tests

### ✅ Métricas
- [ ] **First Contentful Paint**: < 2 segundos
- [ ] **Largest Contentful Paint**: < 3 segundos
- [ ] **Time to Interactive**: < 5 segundos
- [ ] **Bundle Size**: < 2MB gzipped

### ✅ Network
- [ ] **API Response Time**: < 1 segundo promedio
- [ ] **Concurrent Requests**: Maneja múltiples requests
- [ ] **Retry Logic**: Reintentos automáticos funcionan
- [ ] **Caching**: Headers de cache apropiados

## ✅ Checklist Final

### ✅ Funcionalidad Core
- [ ] Dashboard muestra datos reales
- [ ] Recomendaciones se actualizan
- [ ] Backtests ejecutan correctamente
- [ ] Comparaciones funcionan
- [ ] Manejo de errores robusto

### ✅ Integración Backend
- [ ] Todos los endpoints utilizados
- [ ] Datos fluyen correctamente
- [ ] Estados sincronizados
- [ ] Errores manejados apropiadamente

### ✅ User Experience
- [ ] Interfaz intuitiva
- [ ] Feedback claro
- [ ] Performance aceptable
- [ ] Responsive design

## 🎉 Sign-off

- [ ] **QA Lead**: _________________ (Fecha: _______)
- [ ] **Frontend Dev**: _________________ (Fecha: _______)
- [ ] **Backend Dev**: _________________ (Fecha: _______)
- [ ] **Product Owner**: _________________ (Fecha: _______)

---

**Notas adicionales:**
- Testear con datos reales del backend
- Verificar logs tanto en frontend como backend
- Documentar cualquier issue encontrado
- Confirmar que todos los casos de uso principales funcionan

