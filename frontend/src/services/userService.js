// src/services/userService.js
import api from './api'
import { useUserStore } from '@/store/modules/usuarios'

class UserService {
  constructor() {
    this.cache = new Map() // Cache simple para usuarios
    this.cacheTimeout = 5 * 60 * 1000 // 5 minutos
  }

  /**
   * Obtiene la lista de todos los usuarios con paginación y filtros
   * @param {Object} params - { page, limit, search, role, status, sortBy, sortOrder }
   * @returns {Promise<Object>} { data, total, page, limit }
   */
  async getAll(params = {}) {
    try {
      const {
        page = 1,
        limit = 10,
        search = '',
        role = '',
        status = '',
        sortBy = 'created_at',
        sortOrder = 'desc',
      } = params

      const queryParams = new URLSearchParams({
        page,
        limit,
        ...(search && { search }),
        ...(role && { role }),
        ...(status && { status }),
        sort_by: sortBy,
        sort_order: sortOrder,
      })

      const response = await api.get(`/usuarios?${queryParams}`)
      
      console.log(`✅ ${response.data.total || response.data.data?.length} usuarios obtenidos`)
      return response.data
    } catch (error) {
      console.error('❌ Error al obtener usuarios:', error)
      throw this._formatError(error)
    }
  }

  /**
   * Obtiene un usuario específico por ID (con cache)
   * @param {number|string} id - ID del usuario
   * @param {boolean} forceRefresh - Forzar recarga sin cache
   * @returns {Promise<Object>}
   */
  async getById(id, forceRefresh = false) {
    try {
      const cacheKey = `user_${id}`

      // Verificar cache si no es refresh forzado
      if (!forceRefresh && this.cache.has(cacheKey)) {
        const cached = this.cache.get(cacheKey)
        if (Date.now() - cached.timestamp < this.cacheTimeout) {
          console.log(`📦 Usuario ${id} obtenido desde cache`)
          return cached.data
        }
      }

      const response = await api.get(`/usuarios/${id}`)
      const userData = response.data

      // Guardar en cache
      this.cache.set(cacheKey, {
        data: userData,
        timestamp: Date.now(),
      })

      console.log(`✅ Usuario ${id} obtenido`)
      return userData
    } catch (error) {
      console.error('❌ Error al obtener usuario:', error)
      throw this._formatError(error)
    }
  }

  /**
   * Busca usuarios por criterios específicos
   * @param {string} query - Término de búsqueda
   * @param {Object} filters - Filtros adicionales
   * @returns {Promise<Array>}
   */
  async search(query, filters = {}) {
    try {
      const response = await api.get('/usuarios/search', {
        params: { q: query, ...filters },
      })

      console.log(`🔍 ${response.data.length} usuarios encontrados`)
      return response.data
    } catch (error) {
      console.error('❌ Error al buscar usuarios:', error)
      throw this._formatError(error)
    }
  }

  /**
   * Crea un nuevo usuario (solo admin)
   * @param {Object} userData - Datos del nuevo usuario
   * @returns {Promise<Object>}
   */
  async create(userData) {
    try {
      // Validar datos requeridos
      this._validateUserData(userData)

      const response = await api.post('/usuarios', userData)
      const newUser = response.data

      console.log('✅ Usuario creado:', newUser.email)
      
      // Invalidar cache de lista
      this._invalidateListCache()

      return newUser
    } catch (error) {
      console.error('❌ Error al crear usuario:', error)
      throw this._formatError(error)
    }
  }

  /**
   * Actualiza un usuario existente
   * @param {number|string} id
   * @param {Object} updates
   * @returns {Promise<Object>}
   */
  async update(id, updates) {
    try {
      const response = await api.patch(`/usuarios/${id}`, updates)
      const updatedUser = response.data

      console.log('✅ Usuario actualizado:', id)

      // Actualizar cache
      const cacheKey = `user_${id}`
      if (this.cache.has(cacheKey)) {
        this.cache.set(cacheKey, {
          data: updatedUser,
          timestamp: Date.now(),
        })
      }

      // Si es el usuario actual, actualizar el store
      const userStore = useUserStore()
      if (userStore.user?.id === parseInt(id)) {
        userStore.updateUser(updatedUser)
      }

      return updatedUser
    } catch (error) {
      console.error('❌ Error al actualizar usuario:', error)
      throw this._formatError(error)
    }
  }

  /**
   * Actualización parcial de usuario
   * @param {number|string} id
   * @param {Object} updates
   * @returns {Promise<Object>}
   */
  async partialUpdate(id, updates) {
    return this.update(id, updates)
  }

  /**
   * Elimina un usuario (soft delete)
   * @param {number|string} id
   * @returns {Promise<void>}
   */
  async delete(id) {
    try {
      await api.delete(`/usuarios/${id}`)
      
      console.log('🗑️ Usuario eliminado:', id)

      // Limpiar del cache
      this.cache.delete(`user_${id}`)
      this._invalidateListCache()

    } catch (error) {
      console.error('❌ Error al eliminar usuario:', error)
      throw this._formatError(error)
    }
  }

  /**
   * Elimina permanentemente un usuario (hard delete)
   * @param {number|string} id
   * @returns {Promise<void>}
   */
  async permanentDelete(id) {
    try {
      await api.delete(`/usuarios/${id}/permanent`)
      
      console.log('🗑️ Usuario eliminado permanentemente:', id)
      this.cache.delete(`user_${id}`)
      this._invalidateListCache()

    } catch (error) {
      console.error('❌ Error al eliminar permanentemente:', error)
      throw this._formatError(error)
    }
  }

  /**
   * Restaura un usuario eliminado (soft delete)
   * @param {number|string} id
   * @returns {Promise<Object>}
   */
  async restore(id) {
    try {
      const response = await api.post(`/usuarios/${id}/restore`)
      
      console.log('♻️ Usuario restaurado:', id)
      this._invalidateListCache()
      
      return response.data
    } catch (error) {
      console.error('❌ Error al restaurar usuario:', error)
      throw this._formatError(error)
    }
  }

  /**
   * Cambia el rol de un usuario
   * @param {number|string} id
   * @param {string} nuevoRol - 'admin', 'user', 'moderator', etc.
   * @returns {Promise<Object>}
   */
  async changeRole(id, nuevoRol) {
    try {
      const response = await api.patch(`/usuarios/${id}/rol`, { rol: nuevoRol })
      
      console.log(`✅ Rol actualizado a "${nuevoRol}" para usuario ${id}`)
      
      // Invalidar cache
      this.cache.delete(`user_${id}`)

      return response.data
    } catch (error) {
      console.error('❌ Error al cambiar rol:', error)
      throw this._formatError(error)
    }
  }

  /**
   * Cambia el estado de un usuario (activo/inactivo/bloqueado)
   * @param {number|string} id
   * @param {string} status - 'active', 'inactive', 'blocked'
   * @returns {Promise<Object>}
   */
  async changeStatus(id, status) {
    try {
      const response = await api.patch(`/usuarios/${id}/status`, { status })
      
      console.log(`✅ Estado actualizado a "${status}" para usuario ${id}`)
      this.cache.delete(`user_${id}`)

      return response.data
    } catch (error) {
      console.error('❌ Error al cambiar estado:', error)
      throw this._formatError(error)
    }
  }

  /**
   * Bloquea un usuario
   * @param {number|string} id
   * @param {string} reason - Razón del bloqueo
   * @returns {Promise<Object>}
   */
  async block(id, reason = '') {
    try {
      const response = await api.post(`/usuarios/${id}/block`, { reason })
      
      console.log('🚫 Usuario bloqueado:', id)
      this.cache.delete(`user_${id}`)

      return response.data
    } catch (error) {
      console.error('❌ Error al bloquear usuario:', error)
      throw this._formatError(error)
    }
  }

  /**
   * Desbloquea un usuario
   * @param {number|string} id
   * @returns {Promise<Object>}
   */
  async unblock(id) {
    try {
      const response = await api.post(`/usuarios/${id}/unblock`)
      
      console.log('✅ Usuario desbloqueado:', id)
      this.cache.delete(`user_${id}`)

      return response.data
    } catch (error) {
      console.error('❌ Error al desbloquear usuario:', error)
      throw this._formatError(error)
    }
  }

  /**
   * Obtiene las estadísticas de usuarios
   * @returns {Promise<Object>} { total, active, inactive, blocked, by_role }
   */
  async getStats() {
    try {
      const response = await api.get('/usuarios/stats')
      console.log('📊 Estadísticas obtenidas')
      return response.data
    } catch (error) {
      console.error('❌ Error al obtener estadísticas:', error)
      throw this._formatError(error)
    }
  }

  /**
   * Obtiene el historial de actividad de un usuario
   * @param {number|string} id
   * @param {Object} params - { page, limit }
   * @returns {Promise<Object>}
   */
  async getActivityHistory(id, params = {}) {
    try {
      const response = await api.get(`/usuarios/${id}/activity`, { params })
      console.log(`📜 Historial de actividad obtenido para usuario ${id}`)
      return response.data
    } catch (error) {
      console.error('❌ Error al obtener historial:', error)
      throw this._formatError(error)
    }
  }

  /**
   * Sube avatar del usuario
   * @param {number|string} id
   * @param {File} file - Archivo de imagen
   * @param {Function} onProgress - Callback de progreso
   * @returns {Promise<Object>}
   */
  async uploadAvatar(id, file, onProgress = null) {
    try {
      const formData = new FormData()
      formData.append('avatar', file)

      const response = await api.post(`/usuarios/${id}/avatar`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress) {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            )
            onProgress(percentCompleted)
          }
        },
      })

      console.log('✅ Avatar actualizado')
      this.cache.delete(`user_${id}`)

      // Actualizar store si es el usuario actual
      const userStore = useUserStore()
      if (userStore.user?.id === parseInt(id)) {
        userStore.updateUser({ avatar: response.data.avatar })
      }

      return response.data
    } catch (error) {
      console.error('❌ Error al subir avatar:', error)
      throw this._formatError(error)
    }
  }

  /**
   * Elimina el avatar del usuario
   * @param {number|string} id
   * @returns {Promise<void>}
   */
  async deleteAvatar(id) {
    try {
      await api.delete(`/usuarios/${id}/avatar`)
      
      console.log('🗑️ Avatar eliminado')
      this.cache.delete(`user_${id}`)

      // Actualizar store si es el usuario actual
      const userStore = useUserStore()
      if (userStore.user?.id === parseInt(id)) {
        userStore.updateUser({ avatar: null })
      }

    } catch (error) {
      console.error('❌ Error al eliminar avatar:', error)
      throw this._formatError(error)
    }
  }

  /**
   * Exporta usuarios a CSV/Excel
   * @param {Object} filters - Filtros para export
   * @param {string} format - 'csv' o 'excel'
   * @returns {Promise<Blob>}
   */
  async export(filters = {}, format = 'csv') {
    try {
      const response = await api.get('/usuarios/export', {
        params: { ...filters, format },
        responseType: 'blob',
      })

      console.log(`✅ Usuarios exportados en formato ${format}`)
      return response.data
    } catch (error) {
      console.error('❌ Error al exportar usuarios:', error)
      throw this._formatError(error)
    }
  }

  /**
   * Importa usuarios desde CSV/Excel
   * @param {File} file
   * @returns {Promise<Object>} { imported, failed, errors }
   */
  async import(file) {
    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await api.post('/usuarios/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      console.log(`✅ ${response.data.imported} usuarios importados`)
      this._invalidateListCache()

      return response.data
    } catch (error) {
      console.error('❌ Error al importar usuarios:', error)
      throw this._formatError(error)
    }
  }

  /**
   * Obtiene usuarios por rol específico
   * @param {string} role
   * @returns {Promise<Array>}
   */
  async getByRole(role) {
    try {
      const response = await api.get('/usuarios', {
        params: { role },
      })
      
      console.log(`✅ Usuarios con rol "${role}" obtenidos`)
      return response.data
    } catch (error) {
      console.error('❌ Error al obtener usuarios por rol:', error)
      throw this._formatError(error)
    }
  }

  /**
   * Envía email de bienvenida manualmente
   * @param {number|string} id
   * @returns {Promise<void>}
   */
  async sendWelcomeEmail(id) {
    try {
      await api.post(`/usuarios/${id}/send-welcome`)
      console.log('📧 Email de bienvenida enviado')
    } catch (error) {
      console.error('❌ Error al enviar email:', error)
      throw this._formatError(error)
    }
  }

  /**
   * Limpia el cache completo
   */
  clearCache() {
    this.cache.clear()
    console.log('🧹 Cache de usuarios limpiado')
  }

  /**
   * Invalida el cache de listas
   * @private
   */
  _invalidateListCache() {
    // Eliminar entradas de cache que contengan listas
    for (const key of this.cache.keys()) {
      if (key.startsWith('list_') || key === 'all_users') {
        this.cache.delete(key)
      }
    }
  }

  /**
   * Valida datos de usuario antes de crear/actualizar
   * @private
   */
  _validateUserData(userData) {
    const required = ['email', 'nombre']
    const missing = required.filter((field) => !userData[field])

    if (missing.length > 0) {
      throw new Error(`Campos requeridos faltantes: ${missing.join(', ')}`)
    }

    // Validar email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(userData.email)) {
      throw new Error('Email inválido')
    }
  }

  /**
   * Formateo estandarizado de errores
   * @private
   */
  _formatError(error) {
    return {
      message: error.response?.data?.message || error.message || 'Error en operación de usuario',
      status: error.response?.status || 500,
      details: error.response?.data,
      field: error.response?.data?.field, // Campo específico con error
    }
  }
}

// Exportar instancia única (singleton)
export const userService = new UserService()

// También exportar la clase
export default UserService