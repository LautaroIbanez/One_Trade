/**
 * Configuración de React Router con future flags para v7
 * 
 * Estas configuraciones preparan la aplicación para la migración a React Router v7
 * sin romper la compatibilidad actual.
 */

export const routerFutureConfig = {
  /**
   * v7_startTransition: Envuelve las actualizaciones de estado en React.startTransition
   * Mejora la experiencia de usuario al permitir que React priorice actualizaciones urgentes
   */
  v7_startTransition: true,

  /**
   * v7_relativeSplatPath: Cambia la resolución de rutas relativas dentro de rutas Splat
   * Hace que las rutas relativas se resuelvan relativas a la ruta coincidente, no al pathname completo
   */
  v7_relativeSplatPath: true,
};

/**
 * Notas de migración a React Router v7:
 * 
 * 1. Estas flags están disponibles en React Router v6.4+
 * 2. Habilitar estas flags ahora facilita la migración futura a v7
 * 3. No hay cambios de breaking si no usas rutas Splat o si tus rutas ya siguen el nuevo comportamiento
 * 4. Documenta cualquier cambio de comportamiento observado al habilitar estas flags
 * 
 * Recursos:
 * - https://reactrouter.com/en/main/upgrading/future
 * - https://reactrouter.com/en/main/routers/create-browser-router
 */
