import React from 'react'
import ReactDOM from 'react-dom/client'
import AppSimple from './AppSimple.tsx'

// Función simple sin dependencias complejas
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AppSimple />
  </React.StrictMode>,
)
