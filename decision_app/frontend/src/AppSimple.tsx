import React from 'react'

function AppSimple() {
  return (
    <div style={{ 
      padding: '20px', 
      fontFamily: 'Arial, sans-serif',
      backgroundColor: '#f5f5f5',
      minHeight: '100vh'
    }}>
      <h1 style={{ color: '#333', marginBottom: '20px' }}>
        🚀 One Trade Decision App
      </h1>
      
      <div style={{
        backgroundColor: 'white',
        padding: '20px',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        marginBottom: '20px'
      }}>
        <h2 style={{ color: '#2563eb', marginBottom: '15px' }}>
          ✅ Frontend Funcionando
        </h2>
        <p style={{ color: '#666', marginBottom: '10px' }}>
          El frontend está corriendo correctamente en localhost:3000
        </p>
        <p style={{ color: '#666', marginBottom: '10px' }}>
          Backend: http://localhost:8000
        </p>
        <p style={{ color: '#666' }}>
          Timestamp: {new Date().toLocaleString()}
        </p>
      </div>

      <div style={{
        backgroundColor: 'white',
        padding: '20px',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        marginBottom: '20px'
      }}>
        <h2 style={{ color: '#059669', marginBottom: '15px' }}>
          📊 Estado del Sistema
        </h2>
        <ul style={{ color: '#666', lineHeight: '1.6' }}>
          <li>✅ Frontend React cargado</li>
          <li>✅ Vite dev server funcionando</li>
          <li>✅ TypeScript compilando</li>
          <li>🔄 Conectando con backend...</li>
        </ul>
      </div>

      <div style={{
        backgroundColor: '#fef3c7',
        border: '1px solid #f59e0b',
        padding: '15px',
        borderRadius: '8px'
      }}>
        <h3 style={{ color: '#92400e', marginBottom: '10px' }}>
          💡 Próximos Pasos
        </h3>
        <p style={{ color: '#92400e', margin: 0 }}>
          1. Verificar que el backend esté corriendo en puerto 8000<br/>
          2. Probar endpoints: /health, /docs<br/>
          3. Cargar componentes completos del dashboard
        </p>
      </div>
    </div>
  )
}

export default AppSimple
