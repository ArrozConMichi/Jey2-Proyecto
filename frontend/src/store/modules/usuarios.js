// src/store/modules/usuarios.js
import { defineStore } from 'pinia'
import { jwtDecode } from 'jwt-decode' // npm install jwt-decode

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    token: null,
    refreshToken: null,
    isAuthenticated: false,
    loading: false,
    error: null,
  }),

  getters: {
    // Verifica si el usuario está autenticado
    isLoggedIn: (state) => !!state.token && !!state.user,
    
    // Obtiene el nombre completo del usuario
    fullName: (state) => {
      if (!state.user) return ''
      return `${state.user.nombre || ''} ${state.user.apellido || ''}`.trim()
    },
    
    // Obtiene las iniciales del usuario
    initials: (state) => {
      if (!state.user) return ''
      const nombre = state.user.nombre?.[0] || ''
      const apellido = state.user.apellido?.[0] || ''
      return (nombre + apellido).toUpperCase()
    },
    
    // Verifica si el usuario tiene un rol específico
    hasRole: (state) => (role) => {
      return state.user?.roles?.includes(role) || false
    },
    
    // Verifica si el token está expirado
    isTokenExpired: (state) => {
      if (!state.token) return true
      
      try {
        const decoded = jwtDecode(state.token)
        const currentTime = Date.now() / 1000
        return decoded.exp < currentTime
      } catch (error) {
        console.error('Error al decodificar token:', error)
        return true
      }
    },
    
    // Obtiene el tiempo restante del token en minutos
    tokenExpiresIn: (state) => {
      if (!state.token) return 0
      
      try {
        const decoded = jwtDecode(state.token)
        const currentTime = Date.now() / 1000
        const remaining = decoded.exp - currentTime
        return Math.max(0, Math.floor(remaining / 60))
      } catch (error) {
        return 0
      }
    },
  },

  actions: {
    /**
     * Establece los datos del usuario
     */
    setUser(userData) {
      this.user = userData
      this.isAuthenticated = !!userData
      this.error = null
    },

    /**
     * Establece el token de acceso
     */
    setToken(token) {
      if (!token) {
        console.warn('⚠️ Intentando establecer un token vacío')
        return
      }

      this.token = token
      this.isAuthenticated = true
      this.error = null
      
      // Guardar en localStorage como respaldo
      try {
        localStorage.setItem('token', token)
      } catch (e) {
        console.error('Error al guardar token en localStorage:', e)
      }
    },

    /**
     * Establece el refresh token
     */
    setRefreshToken(refreshToken) {
      this.refreshToken = refreshToken
      
      try {
        localStorage.setItem('refreshToken', refreshToken)
      } catch (e) {
        console.error('Error al guardar refreshToken:', e)
      }
    },

    /**
     * Login completo - establece usuario y tokens
     */
    login(userData, token, refreshToken = null) {
      this.setUser(userData)
      this.setToken(token)
      
      if (refreshToken) {
        this.setRefreshToken(refreshToken)
      }
      
      console.log('✅ Usuario autenticado:', userData.email || userData.username)
    },

    /**
     * Logout - limpia todo el estado
     */
    async logout() {
      // Limpiar estado
      this.user = null
      this.token = null
      this.refreshToken = null
      this.isAuthenticated = false
      this.error = null
      this.loading = false

      // Limpiar localStorage
      try {
        localStorage.removeItem('token')
        localStorage.removeItem('refreshToken')
      } catch (e) {
        console.error('Error al limpiar localStorage:', e)
      }

      console.log('👋 Usuario desconectado')
    },

    /**
     * Actualiza los datos del usuario
     */
    updateUser(updates) {
      if (!this.user) {
        console.warn('⚠️ No hay usuario para actualizar')
        return
      }

      this.user = { ...this.user, ...updates }
      console.log('✅ Datos de usuario actualizados')
    },

    /**
     * Establece el estado de carga
     */
    setLoading(loading) {
      this.loading = loading
    },

    /**
     * Establece un error
     */
    setError(error) {
      this.error = error
      console.error('❌ Error en user store:', error)
    },

    /**
     * Limpia errores
     */
    clearError() {
      this.error = null
    },

    /**
     * Verifica si el usuario tiene permisos
     */
    hasPermission(permission) {
      return this.user?.permissions?.includes(permission) || false
    },

    /**
     * Verifica y restaura la sesión desde localStorage
     */
    async initializeAuth() {
      try {
        const token = localStorage.getItem('token')
        const refreshToken = localStorage.getItem('refreshToken')

        if (!token) {
          console.log('ℹ️ No hay sesión previa')
          return false
        }

        // Verificar si el token está expirado
        if (this.isTokenExpired) {
          console.warn('⚠️ Token expirado, limpiando sesión')
          await this.logout()
          return false
        }

        // Restaurar tokens
        this.token = token
        if (refreshToken) {
          this.refreshToken = refreshToken
        }

        // Aquí podrías hacer una llamada al backend para obtener los datos del usuario
        // const userData = await fetchCurrentUser()
        // this.setUser(userData)

        this.isAuthenticated = true
        console.log('✅ Sesión restaurada desde localStorage')
        return true
      } catch (error) {
        console.error('Error al inicializar autenticación:', error)
        await this.logout()
        return false
      }
    },

    /**
     * Decodifica y retorna los datos del token
     */
    getTokenData() {
      if (!this.token) return null

      try {
        return jwtDecode(this.token)
      } catch (error) {
        console.error('Error al decodificar token:', error)
        return null
      }
    },
  },

  persist: {
    enabled: true,
    strategies: [
      {
        key: 'user-store',
        storage: localStorage,
        paths: ['user', 'token', 'refreshToken', 'isAuthenticated'],
      },
    ],
  },
})