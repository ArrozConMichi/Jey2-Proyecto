// src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// Pinia
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

// Services (singleton instances)
import { userService } from './services/userService'
import { rolesService } from './services/rolesService'
import { authService } from './services/authService'

// Store
import { useUserStore } from './store/modules/usuarios'

// Utils globales (opcional)
import * as appConfig from './config/appConfig'

// CSS global
import '@/assets/css/base.css'
import '@/assets/css/variables.css'

// ===== Crear instancias =====
const app = createApp(App)
const pinia = createPinia()

// ===== Configurar Pinia con persistencia =====
pinia.use(piniaPluginPersistedstate)

// ===== Registrar plugins =====
app.use(pinia)
app.use(router)

// ===== Provide global services =====
// Permite usar `inject('userService')` en cualquier componente
app.provide('userService', userService)
app.provide('rolesService', rolesService)
app.provide('authService', authService)
app.provide('appConfig', appConfig)

// ===== Configuración global de la app =====
app.config.errorHandler = (err, instance, info) => {
  console.error('❌ Error global capturado:', err)
  console.error('📍 Componente:', instance?.$options?.name || 'Desconocido')
  console.error('ℹ️ Info:', info)
  
  // Aquí podrías enviar el error a un servicio de logging como Sentry
  // Sentry.captureException(err)
}

app.config.warnHandler = (msg, instance, trace) => {
  console.warn('⚠️ Warning Vue:', msg)
  // Solo en desarrollo
  if (import.meta.env.DEV) {
    console.warn('Trace:', trace)
  }
}

// ===== Performance Monitoring (solo desarrollo) =====
if (import.meta.env.DEV) {
  app.config.performance = true
  console.log('📊 Performance monitoring habilitado')
}

// ===== Propiedades globales opcionales =====
app.config.globalProperties.$appName = appConfig.APP_NAME || 'Mi Aplicación'
app.config.globalProperties.$appVersion = appConfig.APP_VERSION || '1.0.0'

// ===== Inicialización de autenticación =====
const initializeAuth = async () => {
  try {
    console.log('🔐 Inicializando autenticación...')
    const isAuthenticated = await authService.initAuth()
    
    if (isAuthenticated) {
      console.log('✅ Sesión restaurada')
    } else {
      console.log('ℹ️ No hay sesión previa')
    }
  } catch (error) {
    console.error('❌ Error al inicializar autenticación:', error)
  }
}

// ===== Montar la app =====
const mountApp = async () => {
  try {
    // Inicializar autenticación antes de montar
    await initializeAuth()
    
    // Montar la aplicación
    app.mount('#app')
    
    console.log('🚀 App iniciada exitosamente')
    console.log('📦 Pinia:', '✓')
    console.log('🛣️ Router:', '✓')
    console.log('🔧 Services:', '✓')
    console.log('🔐 Auth:', '✓')
    
    // Info de entorno
    console.log(`🌍 Entorno: ${import.meta.env.MODE}`)
    console.log(`📍 API URL: ${import.meta.env.VITE_API_URL || 'localhost:8000'}`)
    
  } catch (error) {
    console.error('💥 Error fatal al iniciar la aplicación:', error)
    
    // Mostrar mensaje de error al usuario
    document.getElementById('app').innerHTML = `
      <div style="
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh;
        font-family: system-ui, -apple-system, sans-serif;
        text-align: center;
        padding: 2rem;
      ">
        <h1 style="color: #dc2626; font-size: 2rem; margin-bottom: 1rem;">
          ⚠️ Error al cargar la aplicación
        </h1>
        <p style="color: #666; margin-bottom: 2rem;">
          Por favor, recarga la página o contacta al soporte técnico.
        </p>
        <button 
          onclick="window.location.reload()" 
          style="
            padding: 0.75rem 2rem;
            background: #2563eb;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
          "
        >
          🔄 Recargar página
        </button>
        ${import.meta.env.DEV ? `<pre style="margin-top: 2rem; color: #dc2626; text-align: left; background: #fee; padding: 1rem; border-radius: 8px; overflow: auto;">${error.stack}</pre>` : ''}
      </div>
    `
  }
}

// ===== Listener para cambios de conexión =====
window.addEventListener('online', () => {
  console.log('🌐 Conexión restaurada')
  // Puedes mostrar una notificación al usuario
})

window.addEventListener('offline', () => {
  console.warn('📡 Sin conexión a Internet')
  // Puedes mostrar una notificación al usuario
})

// ===== Prevenir cierre accidental con cambios sin guardar =====
let hasUnsavedChanges = false

export const setUnsavedChanges = (value) => {
  hasUnsavedChanges = value
}

window.addEventListener('beforeunload', (e) => {
  if (hasUnsavedChanges) {
    e.preventDefault()
    e.returnValue = '¿Estás seguro? Tienes cambios sin guardar.'
    return e.returnValue
  }
})

// ===== Detectar modo oscuro del sistema (opcional) =====
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)')

const updateTheme = (isDark) => {
  document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light')
  console.log(`🎨 Tema actualizado: ${isDark ? 'oscuro' : 'claro'}`)
}

// Aplicar tema inicial
updateTheme(prefersDark.matches)

// Escuchar cambios en preferencias del sistema
prefersDark.addEventListener('change', (e) => {
  updateTheme(e.matches)
})

// ===== Hot Module Replacement (HMR) - solo desarrollo =====
if (import.meta.hot) {
  import.meta.hot.accept(() => {
    console.log('🔥 HMR: Módulo actualizado')
  })
}

// ===== Iniciar aplicación =====
mountApp()

// ===== Exportar instancias para uso en tests o debugging =====
export { app, pinia, router }

// ===== Debugging en consola (solo desarrollo) =====
if (import.meta.env.DEV) {
  // Exponer en window para debugging
  window.__APP__ = app
  window.__PINIA__ = pinia
  window.__ROUTER__ = router
  window.__SERVICES__ = {
    userService,
    rolesService,
    authService,
  }
  
  console.log('🔍 Debug mode: Accede a las instancias desde window.__APP__, window.__SERVICES__, etc.')
}