// src/services/authService.js
import { useUserStore } from '@/store/modules/usuarios'
import api from './api'

class AuthService {
  constructor() {
    this.refreshTokenPromise = null // Para evitar múltiples refreshes simultáneos
  }

  /**
   * Login de usuario
   * @param {Object} credentials - { email, password }
   * @returns {Promise<Object>} Datos del usuario
   */
  async login(credentials) {
    try {
      const userStore = useUserStore()
      userStore.setLoading(true)
      userStore.clearError()

      const response = await api.post('/auth/login', credentials)
      const { user, access_token, refresh_token } = response.data

      if (!user || !access_token) {
        throw new Error('Respuesta de login inválida del servidor')
      }

      userStore.login(user, access_token, refresh_token)
      
      console.log('✅ Login exitoso:', user.email || user.username)
      return user
    } catch (error) {
      const userStore = useUserStore()
      const errorMessage = error.response?.data?.message || 'Error al iniciar sesión'
      
      userStore.setError(errorMessage)
      console.error('❌ Error en login:', errorMessage)
      
      throw {
        message: errorMessage,
        status: error.response?.status,
        details: error.response?.data,
      }
    } finally {
      const userStore = useUserStore()
      userStore.setLoading(false)
    }
  }

  /**
   * Registro de nuevo usuario
   * @param {Object} userData - Datos del nuevo usuario
   * @returns {Promise<Object>} Usuario creado
   */
  async register(userData) {
    try {
      const userStore = useUserStore()
      userStore.setLoading(true)
      userStore.clearError()

      const response = await api.post('/auth/register', userData)
      const { user, access_token, refresh_token } = response.data

      // Auto-login después del registro
      if (user && access_token) {
        userStore.login(user, access_token, refresh_token)
      }

      console.log('✅ Registro exitoso:', user.email)
      return user
    } catch (error) {
      const userStore = useUserStore()
      const errorMessage = error.response?.data?.message || 'Error al registrar usuario'
      
      userStore.setError(errorMessage)
      console.error('❌ Error en registro:', errorMessage)
      
      throw {
        message: errorMessage,
        status: error.response?.status,
        details: error.response?.data,
      }
    } finally {
      const userStore = useUserStore()
      userStore.setLoading(false)
    }
  }

  /**
   * Logout - Cierra sesión del usuario
   * @param {boolean} callApi - Si debe notificar al backend
   */
  async logout(callApi = true) {
    try {
      const userStore = useUserStore()
      
      // Opcional: Notificar al backend para invalidar el token
      if (callApi && userStore.token) {
        try {
          await api.post('/auth/logout')
        } catch (error) {
          console.warn('⚠️ No se pudo notificar logout al servidor:', error.message)
        }
      }

      await userStore.logout()
      console.log('👋 Logout exitoso')
    } catch (error) {
      console.error('❌ Error en logout:', error)
      // Forzar logout local aunque falle el servidor
      const userStore = useUserStore()
      await userStore.logout()
    }
  }

  /**
   * Obtiene los datos del usuario actual
   * @returns {Promise<Object>} Datos del usuario
   */
  async getCurrentUser() {
    try {
      const userStore = useUserStore()

      if (!userStore.token) {
        throw new Error('No hay sesión activa')
      }

      const response = await api.get('/auth/me')
      const user = response.data

      // Actualizar store con datos frescos
      userStore.setUser(user)

      return user
    } catch (error) {
      console.error('❌ Error al obtener usuario actual:', error)
      
      // Si falla porque no está autenticado, hacer logout
      if (error.response?.status === 401) {
        await this.logout(false)
      }
      
      throw {
        message: error.response?.data?.message || 'Error al obtener datos del usuario',
        status: error.response?.status,
      }
    }
  }

  /**
   * Refresca el access token usando el refresh token
   * @returns {Promise<string>} Nuevo access token
   */
  async refreshToken() {
    // Evitar múltiples refreshes simultáneos
    if (this.refreshTokenPromise) {
      return this.refreshTokenPromise
    }

    this.refreshTokenPromise = this._performRefresh()

    try {
      const newToken = await this.refreshTokenPromise
      return newToken
    } finally {
      this.refreshTokenPromise = null
    }
  }

  async _performRefresh() {
    try {
      const userStore = useUserStore()

      if (!userStore.refreshToken) {
        throw new Error('No hay refresh token disponible')
      }

      console.log('🔄 Refrescando token...')

      const response = await api.post('/auth/refresh', {
        refresh_token: userStore.refreshToken,
      })

      const { access_token, refresh_token } = response.data

      userStore.setToken(access_token)
      
      if (refresh_token) {
        userStore.setRefreshToken(refresh_token)
      }

      console.log('✅ Token refrescado exitosamente')
      return access_token
    } catch (error) {
      console.error('❌ Error al refrescar token:', error)
      
      // Si falla el refresh, hacer logout
      await this.logout(false)
      
      throw new Error('Sesión expirada. Por favor, inicia sesión nuevamente.')
    }
  }

  /**
   * Verifica si el usuario está autenticado
   * @returns {boolean}
   */
  isAuthenticated() {
    const userStore = useUserStore()
    return userStore.isLoggedIn && !userStore.isTokenExpired
  }

  /**
   * Solicita recuperación de contraseña
   * @param {string} email
   */
  async forgotPassword(email) {
    try {
      const response = await api.post('/auth/forgot-password', { email })
      console.log('✅ Email de recuperación enviado')
      return response.data
    } catch (error) {
      const errorMessage = error.response?.data?.message || 'Error al enviar email de recuperación'
      console.error('❌ Error en forgot password:', errorMessage)
      
      throw {
        message: errorMessage,
        status: error.response?.status,
      }
    }
  }

  /**
   * Restablece la contraseña con token
   * @param {string} token - Token de recuperación
   * @param {string} newPassword - Nueva contraseña
   */
  async resetPassword(token, newPassword) {
    try {
      const response = await api.post('/auth/reset-password', {
        token,
        password: newPassword,
      })
      
      console.log('✅ Contraseña restablecida exitosamente')
      return response.data
    } catch (error) {
      const errorMessage = error.response?.data?.message || 'Error al restablecer contraseña'
      console.error('❌ Error en reset password:', errorMessage)
      
      throw {
        message: errorMessage,
        status: error.response?.status,
      }
    }
  }

  /**
   * Cambia la contraseña del usuario actual
   * @param {string} currentPassword
   * @param {string} newPassword
   */
  async changePassword(currentPassword, newPassword) {
    try {
      const response = await api.post('/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword,
      })
      
      console.log('✅ Contraseña cambiada exitosamente')
      return response.data
    } catch (error) {
      const errorMessage = error.response?.data?.message || 'Error al cambiar contraseña'
      console.error('❌ Error en change password:', errorMessage)
      
      throw {
        message: errorMessage,
        status: error.response?.status,
      }
    }
  }

  /**
   * Verifica email con token
   * @param {string} token - Token de verificación
   */
  async verifyEmail(token) {
    try {
      const response = await api.post('/auth/verify-email', { token })
      console.log('✅ Email verificado exitosamente')
      return response.data
    } catch (error) {
      const errorMessage = error.response?.data?.message || 'Error al verificar email'
      console.error('❌ Error en verify email:', errorMessage)
      
      throw {
        message: errorMessage,
        status: error.response?.status,
      }
    }
  }

  /**
   * Reenvía email de verificación
   */
  async resendVerificationEmail() {
    try {
      const response = await api.post('/auth/resend-verification')
      console.log('✅ Email de verificación reenviado')
      return response.data
    } catch (error) {
      const errorMessage = error.response?.data?.message || 'Error al reenviar email'
      console.error('❌ Error en resend verification:', errorMessage)
      
      throw {
        message: errorMessage,
        status: error.response?.status,
      }
    }
  }

  /**
   * Actualiza el perfil del usuario
   * @param {Object} updates - Datos a actualizar
   */
  async updateProfile(updates) {
    try {
      const userStore = useUserStore()
      userStore.setLoading(true)

      const response = await api.patch('/auth/profile', updates)
      const updatedUser = response.data

      userStore.updateUser(updatedUser)
      
      console.log('✅ Perfil actualizado exitosamente')
      return updatedUser
    } catch (error) {
      const errorMessage = error.response?.data?.message || 'Error al actualizar perfil'
      console.error('❌ Error en update profile:', errorMessage)
      
      throw {
        message: errorMessage,
        status: error.response?.status,
        details: error.response?.data,
      }
    } finally {
      const userStore = useUserStore()
      userStore.setLoading(false)
    }
  }

  /**
   * Inicializa la autenticación al cargar la app
   */
  async initAuth() {
    try {
      const userStore = useUserStore()
      
      // Restaurar sesión desde localStorage
      const hasSession = await userStore.initializeAuth()

      if (!hasSession) {
        return false
      }

      // Verificar que el token sigue siendo válido obteniendo datos del usuario
      try {
        await this.getCurrentUser()
        return true
      } catch (error) {
        console.warn('⚠️ Token inválido, limpiando sesión')
        await this.logout(false)
        return false
      }
    } catch (error) {
      console.error('❌ Error al inicializar autenticación:', error)
      return false
    }
  }
}

// Exportar instancia única (singleton)
export const authService = new AuthService()

// También exportar la clase por si se necesita instanciar
export default AuthService