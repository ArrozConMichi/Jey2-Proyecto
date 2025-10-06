// src/services/api.js
import axios from 'axios'
import { useUserStore } from '@/store/modules/usuarios'

// 🌎 Configuración base de Axios
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000, // 15s timeout
})

// Variable para evitar múltiples redirects
let isRedirecting = false

// 🧩 Interceptor de request - Añade JWT automáticamente
api.interceptors.request.use(
  (config) => {
    try {
      const userStore = useUserStore()
      const token = userStore.token
      
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    } catch (e) {
      console.warn('⚠️ No se pudo acceder al store del usuario:', e)
    }
    return config
  },
  (error) => {
    console.error('❌ Error en request interceptor:', error)
    return Promise.reject(error)
  }
)

// 🚨 Interceptor de response - Manejo de errores globales
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { response, config } = error

    // Manejo de errores 401 (No autorizado)
    if (response?.status === 401 && !isRedirecting) {
      isRedirecting = true
      console.warn('🚫 Sesión expirada o no autorizada.')
      
      try {
        const userStore = useUserStore()
        await userStore.logout()
      } catch (e) {
        console.error('Error al hacer logout:', e)
      }
      
      // Redirigir al login
      window.location.href = '/login'
      return Promise.reject(error)
    }

    // Manejo de errores 403 (Prohibido)
    if (response?.status === 403) {
      console.error('🚫 Acceso prohibido. No tienes permisos para esta acción.')
    }

    // Manejo de errores 404 (No encontrado)
    if (response?.status === 404) {
      console.warn('🔍 Recurso no encontrado:', config?.url)
    }

    // Manejo de errores 500 (Error del servidor)
    if (response?.status >= 500) {
      console.error('💥 Error del servidor. Intenta más tarde.')
    }

    // Logging detallado según el tipo de error
    if (response) {
      console.error(
        `❌ Error ${response.status} en ${config?.method?.toUpperCase()} ${config?.url}:`,
        response.data
      )
    } else if (error.code === 'ECONNABORTED') {
      console.error('⏱️ Timeout: La petición tardó demasiado')
    } else if (error.message === 'Network Error') {
      console.error('🌐 Error de red: Verifica tu conexión a internet')
    } else {
      console.error('❌ Error desconocido:', error.message)
    }

    return Promise.reject(error)
  }
)

// 🧰 Helper function para llamadas rápidas con mejor manejo de errores
export const apiRequest = async (method, url, data = null, config = {}) => {
  try {
    const response = await api({ 
      method, 
      url, 
      ...(data && { data }),
      ...config 
    })
    return response.data
  } catch (error) {
    // Estructura de error más completa
    const errorData = {
      message: error.response?.data?.message || error.message || 'Error desconocido',
      status: error.response?.status,
      details: error.response?.data,
      url: error.config?.url,
    }
    
    throw errorData
  }
}

// 🎯 Helpers específicos para métodos HTTP (opcional pero útil)
export const get = (url, config) => apiRequest('get', url, null, config)
export const post = (url, data, config) => apiRequest('post', url, data, config)
export const put = (url, data, config) => apiRequest('put', url, data, config)
export const patch = (url, data, config) => apiRequest('patch', url, data, config)
export const del = (url, config) => apiRequest('delete', url, null, config)

// 🔧 Helper para FormData (útil para subir archivos)
export const uploadFile = async (url, formData, onUploadProgress) => {
  try {
    const response = await api.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    })
    return response.data
  } catch (error) {
    throw error.response?.data || { message: 'Error al subir archivo' }
  }
}

export default api