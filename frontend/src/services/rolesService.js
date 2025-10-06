// src/services/rolesService.js
import api from './api'
import { useUserStore } from '@/store/modules/usuarios'

class RolesService {
  constructor() {
    this.cache = new Map()
    this.cacheDuration = 1000 * 60 * 10 // 10 minutos
    this.pendingRequests = new Map() // Para evitar requests duplicados
  }

  // =========================
  // 🔹 CRUD de Roles
  // =========================

  /**
   * Obtiene todos los roles con filtros opcionales
   * @param {Object} options - { forceRefresh, includePermissions, includeUsers, status }
   * @returns {Promise<Array>}
   */
  async getAll(options = {}) {
    const { 
      forceRefresh = false, 
      includePermissions = false,
      includeUsers = false,
      status = null 
    } = options

    const cacheKey = `roles_${JSON.stringify({ includePermissions, includeUsers, status })}`

    // Verificar cache
    if (!forceRefresh && this.cache.has(cacheKey)) {
      const { data, timestamp } = this.cache.get(cacheKey)
      if (Date.now() - timestamp < this.cacheDuration) {
        console.log('📦 Roles obtenidos desde cache')
        return data
      }
    }

    try {
      const params = new URLSearchParams()
      if (includePermissions) params.append('include_permissions', 'true')
      if (includeUsers) params.append('include_users', 'true')
      if (status) params.append('status', status)

      const response = await api.get(`/roles?${params}`)
      const roles = response.data

      // Guardar en cache
      this.cache.set(cacheKey, { data: roles, timestamp: Date.now() })
      
      console.log(`✅ ${roles.length} roles obtenidos`)
      return roles
    } catch (error) {
      this._handleError(error, 'Error al obtener roles')
    }
  }

  /**
   * Obtiene un rol específico por ID
   * @param {number|string} id
   * @param {Object} options - { forceRefresh, includePermissions, includeUsers }
   * @returns {Promise<Object>}
   */
  async getById(id, options = {}) {
    const { 
      forceRefresh = false,
      includePermissions = true,
      includeUsers = false 
    } = options

    const cacheKey = `role_${id}_${includePermissions}_${includeUsers}`

    // Verificar cache
    if (!forceRefresh && this.cache.has(cacheKey)) {
      const { data, timestamp } = this.cache.get(cacheKey)
      if (Date.now() - timestamp < this.cacheDuration) {
        console.log(`📦 Rol ${id} obtenido desde cache`)
        return data
      }
    }

    try {
      const params = new URLSearchParams()
      if (includePermissions) params.append('include_permissions', 'true')
      if (includeUsers) params.append('include_users', 'true')

      const response = await api.get(`/roles/${id}?${params}`)
      const role = response.data

      // Guardar en cache
      this.cache.set(cacheKey, { data: role, timestamp: Date.now() })
      
      console.log(`✅ Rol "${role.nombre}" obtenido`)
      return role
    } catch (error) {
      this._handleError(error, 'Error al obtener el rol')
    }
  }

  /**
   * Busca roles por nombre o descripción
   * @param {string} query
   * @returns {Promise<Array>}
   */
  async search(query) {
    try {
      const response = await api.get('/roles/search', {
        params: { q: query }
      })
      
      console.log(`🔍 ${response.data.length} roles encontrados`)
      return response.data
    } catch (error) {
      this._handleError(error, 'Error al buscar roles')
    }
  }

  /**
   * Crea un nuevo rol
   * @param {Object} data - { nombre, descripcion, permisos, color, icono, prioridad }
   * @returns {Promise<Object>}
   */
  async create(data) {
    try {
      // Validación básica
      this._validateRoleData(data)

      const response = await api.post('/roles', data)
      const newRole = response.data

      console.log(`✅ Rol "${newRole.nombre}" creado exitosamente`)
      
      // Limpiar cache
      this.clearCache()

      return newRole
    } catch (error) {
      this._handleError(error, 'Error al crear el rol')
    }
  }

  /**
   * Actualiza un rol existente
   * @param {number|string} id
   * @param {Object} updates
   * @returns {Promise<Object>}
   */
  async update(id, updates) {
    try {
      const response = await api.patch(`/roles/${id}`, updates)
      const updatedRole = response.data

      console.log(`✅ Rol "${updatedRole.nombre}" actualizado`)
      
      // Limpiar cache
      this.clearCache()

      return updatedRole
    } catch (error) {
      this._handleError(error, 'Error al actualizar el rol')
    }
  }

  /**
   * Elimina un rol (soft delete)
   * @param {number|string} id
   * @returns {Promise<void>}
   */
  async delete(id) {
    try {
      await api.delete(`/roles/${id}`)
      
      console.log(`🗑️ Rol ${id} eliminado`)
      this.clearCache()
    } catch (error) {
      this._handleError(error, 'Error al eliminar el rol')
    }
  }

  /**
   * Restaura un rol eliminado
   * @param {number|string} id
   * @returns {Promise<Object>}
   */
  async restore(id) {
    try {
      const response = await api.post(`/roles/${id}/restore`)
      
      console.log(`♻️ Rol ${id} restaurado`)
      this.clearCache()
      
      return response.data
    } catch (error) {
      this._handleError(error, 'Error al restaurar el rol')
    }
  }

  /**
   * Duplica un rol existente
   * @param {number|string} id
   * @param {string} newName
   * @returns {Promise<Object>}
   */
  async duplicate(id, newName) {
    try {
      const response = await api.post(`/roles/${id}/duplicate`, {
        nombre: newName
      })
      
      console.log(`✅ Rol duplicado como "${newName}"`)
      this.clearCache()
      
      return response.data
    } catch (error) {
      this._handleError(error, 'Error al duplicar el rol')
    }
  }

  // =========================
  // 🔹 Gestión de Usuarios y Roles
  // =========================

  /**
   * Asigna un rol a un usuario
   * @param {number|string} userId
   * @param {number|string} roleId
   * @returns {Promise<Object>}
   */
  async assignToUser(userId, roleId) {
    try {
      const response = await api.post(`/usuarios/${userId}/roles`, { 
        role_id: roleId 
      })

      console.log(`✅ Rol asignado al usuario ${userId}`)
      this.clearCache()

      // Actualizar store si es el usuario actual
      const userStore = useUserStore()
      if (userStore.user?.id === parseInt(userId)) {
        await this.refreshCurrentUserRoles()
      }

      return response.data
    } catch (error) {
      this._handleError(error, 'Error al asignar rol al usuario')
    }
  }

  /**
   * Asigna múltiples roles a un usuario
   * @param {number|string} userId
   * @param {Array<number>} roleIds
   * @returns {Promise<Object>}
   */
  async assignMultipleToUser(userId, roleIds) {
    try {
      const response = await api.post(`/usuarios/${userId}/roles/bulk`, {
        role_ids: roleIds
      })

      console.log(`✅ ${roleIds.length} roles asignados al usuario ${userId}`)
      this.clearCache()

      // Actualizar store si es el usuario actual
      const userStore = useUserStore()
      if (userStore.user?.id === parseInt(userId)) {
        await this.refreshCurrentUserRoles()
      }

      return response.data
    } catch (error) {
      this._handleError(error, 'Error al asignar roles al usuario')
    }
  }

  /**
   * Remueve un rol de un usuario
   * @param {number|string} userId
   * @param {number|string} roleId
   * @returns {Promise<void>}
   */
  async removeFromUser(userId, roleId) {
    try {
      await api.delete(`/usuarios/${userId}/roles/${roleId}`)

      console.log(`✅ Rol removido del usuario ${userId}`)
      this.clearCache()

      // Actualizar store si es el usuario actual
      const userStore = useUserStore()
      if (userStore.user?.id === parseInt(userId)) {
        await this.refreshCurrentUserRoles()
      }
    } catch (error) {
      this._handleError(error, 'Error al remover rol del usuario')
    }
  }

  /**
   * Obtiene todos los roles de un usuario específico
   * @param {number|string} userId
   * @returns {Promise<Array>}
   */
  async getUserRoles(userId) {
    try {
      const response = await api.get(`/usuarios/${userId}/roles`)
      console.log(`✅ Roles del usuario ${userId} obtenidos`)
      return response.data
    } catch (error) {
      this._handleError(error, 'Error al obtener roles del usuario')
    }
  }

  /**
   * Obtiene usuarios que tienen un rol específico
   * @param {number|string} roleId
   * @param {Object} params - { page, limit }
   * @returns {Promise<Object>}
   */
  async getRoleUsers(roleId, params = {}) {
    try {
      const response = await api.get(`/roles/${roleId}/usuarios`, { params })
      console.log(`✅ Usuarios del rol ${roleId} obtenidos`)
      return response.data
    } catch (error) {
      this._handleError(error, 'Error al obtener usuarios del rol')
    }
  }

  /**
   * Obtiene los roles del usuario actual desde el store
   * @returns {Promise<Array>}
   */
  async getCurrentUserRoles() {
    try {
      const userStore = useUserStore()
      
      if (!userStore.user?.id) {
        throw new Error('Usuario no autenticado')
      }

      const response = await api.get(`/usuarios/${userStore.user.id}/roles`)
      return response.data
    } catch (error) {
      this._handleError(error, 'Error al obtener roles del usuario actual')
    }
  }

  /**
   * Refresca los roles del usuario actual en el store
   * @returns {Promise<void>}
   */
  async refreshCurrentUserRoles() {
    try {
      const roles = await this.getCurrentUserRoles()
      const userStore = useUserStore()
      userStore.updateUser({ roles })
      console.log('✅ Roles del usuario actual actualizados')
    } catch (error) {
      console.error('Error al refrescar roles:', error)
    }
  }

  /**
   * Sincroniza roles de un usuario (reemplaza todos)
   * @param {number|string} userId
   * @param {Array<number>} roleIds
   * @returns {Promise<Object>}
   */
  async syncUserRoles(userId, roleIds) {
    try {
      const response = await api.put(`/usuarios/${userId}/roles/sync`, {
        role_ids: roleIds
      })

      console.log(`✅ Roles sincronizados para usuario ${userId}`)
      this.clearCache()

      return response.data
    } catch (error) {
      this._handleError(error, 'Error al sincronizar roles')
    }
  }

  // =========================
  // 🔹 Gestión de Permisos
  // =========================

  /**
   * Obtiene todos los permisos disponibles
   * @returns {Promise<Array>}
   */
  async getAllPermissions() {
    const cacheKey = 'all_permissions'

    if (this.cache.has(cacheKey)) {
      const { data, timestamp } = this.cache.get(cacheKey)
      if (Date.now() - timestamp < this.cacheDuration) {
        return data
      }
    }

    try {
      const response = await api.get('/permisos')
      const permissions = response.data

      this.cache.set(cacheKey, { data: permissions, timestamp: Date.now() })
      console.log(`✅ ${permissions.length} permisos disponibles obtenidos`)
      
      return permissions
    } catch (error) {
      this._handleError(error, 'Error al obtener permisos disponibles')
    }
  }

  /**
   * Obtiene permisos de un rol específico
   * @param {number|string} roleId
   * @returns {Promise<Array>}
   */
  async getPermissions(roleId) {
    try {
      const response = await api.get(`/roles/${roleId}/permisos`)
      console.log(`✅ Permisos del rol ${roleId} obtenidos`)
      return response.data
    } catch (error) {
      this._handleError(error, 'Error al obtener permisos del rol')
    }
  }

  /**
   * Asigna permisos a un rol (reemplaza todos)
   * @param {number|string} roleId
   * @param {Array<string|number>} permissions
   * @returns {Promise<Object>}
   */
  async setPermissions(roleId, permissions) {
    try {
      const response = await api.put(`/roles/${roleId}/permisos`, { 
        permisos: permissions 
      })

      console.log(`✅ Permisos asignados al rol ${roleId}`)
      this.clearCache()

      return response.data
    } catch (error) {
      this._handleError(error, 'Error al asignar permisos al rol')
    }
  }

  /**
   * Añade permisos adicionales a un rol
   * @param {number|string} roleId
   * @param {Array<string|number>} permissions
   * @returns {Promise<Object>}
   */
  async addPermissions(roleId, permissions) {
    try {
      const response = await api.post(`/roles/${roleId}/permisos`, {
        permisos: permissions
      })

      console.log(`✅ ${permissions.length} permisos añadidos al rol ${roleId}`)
      this.clearCache()

      return response.data
    } catch (error) {
      this._handleError(error, 'Error al añadir permisos')
    }
  }

  /**
   * Remueve permisos específicos de un rol
   * @param {number|string} roleId
   * @param {Array<string|number>} permissions
   * @returns {Promise<Object>}
   */
  async removePermissions(roleId, permissions) {
    try {
      const response = await api.delete(`/roles/${roleId}/permisos`, {
        data: { permisos: permissions }
      })

      console.log(`✅ ${permissions.length} permisos removidos del rol ${roleId}`)
      this.clearCache()

      return response.data
    } catch (error) {
      this._handleError(error, 'Error al remover permisos')
    }
  }

  /**
   * Obtiene permisos efectivos de un usuario (combinación de todos sus roles)
   * @param {number|string} userId
   * @returns {Promise<Array>}
   */
  async getUserEffectivePermissions(userId) {
    try {
      const response = await api.get(`/usuarios/${userId}/permisos/efectivos`)
      console.log(`✅ Permisos efectivos del usuario ${userId} obtenidos`)
      return response.data
    } catch (error) {
      this._handleError(error, 'Error al obtener permisos efectivos')
    }
  }

  // =========================
  // 🔹 Validación y Verificación
  // =========================

  /**
   * Verifica si el usuario actual tiene un rol específico
   * @param {string} roleName
   * @returns {Promise<boolean>}
   */
  async currentUserHasRole(roleName) {
    try {
      const roles = await this.getCurrentUserRoles()
      return roles.some(role => role.nombre === roleName || role.slug === roleName)
    } catch (error) {
      console.error('Error al verificar rol:', error)
      return false
    }
  }

  /**
   * Verifica si el usuario actual tiene un permiso específico
   * @param {string} permission
   * @returns {Promise<boolean>}
   */
  async currentUserHasPermission(permission) {
    try {
      const userStore = useUserStore()
      const permissions = await this.getUserEffectivePermissions(userStore.user.id)
      return permissions.some(p => p.nombre === permission || p.slug === permission)
    } catch (error) {
      console.error('Error al verificar permiso:', error)
      return false
    }
  }

  /**
   * Verifica si el usuario actual tiene cualquiera de los roles especificados
   * @param {Array<string>} roleNames
   * @returns {Promise<boolean>}
   */
  async currentUserHasAnyRole(roleNames) {
    try {
      const roles = await this.getCurrentUserRoles()
      return roles.some(role => 
        roleNames.includes(role.nombre) || roleNames.includes(role.slug)
      )
    } catch (error) {
      console.error('Error al verificar roles:', error)
      return false
    }
  }

  /**
   * Verifica si el usuario actual tiene todos los roles especificados
   * @param {Array<string>} roleNames
   * @returns {Promise<boolean>}
   */
  async currentUserHasAllRoles(roleNames) {
    try {
      const roles = await this.getCurrentUserRoles()
      const userRoleNames = roles.map(r => r.nombre || r.slug)
      return roleNames.every(name => userRoleNames.includes(name))
    } catch (error) {
      console.error('Error al verificar roles:', error)
      return false
    }
  }

  // =========================
  // 🔹 Estadísticas y Analytics
  // =========================

  /**
   * Obtiene estadísticas de roles
   * @returns {Promise<Object>}
   */
  async getStats() {
    try {
      const response = await api.get('/roles/stats')
      console.log('📊 Estadísticas de roles obtenidas')
      return response.data
    } catch (error) {
      this._handleError(error, 'Error al obtener estadísticas')
    }
  }

  /**
   * Obtiene el rol más usado
   * @returns {Promise<Object>}
   */
  async getMostUsedRole() {
    try {
      const response = await api.get('/roles/most-used')
      return response.data
    } catch (error) {
      this._handleError(error, 'Error al obtener rol más usado')
    }
  }

  /**
   * Obtiene roles por categoría
   * @param {string} category
   * @returns {Promise<Array>}
   */
  async getByCategory(category) {
    try {
      const response = await api.get('/roles', {
        params: { category }
      })
      return response.data
    } catch (error) {
      this._handleError(error, 'Error al obtener roles por categoría')
    }
  }

  // =========================
  // 🔹 Utilidades
  // =========================

  /**
   * Limpia todo el cache
   */
  clearCache() {
    this.cache.clear()
    console.log('🧹 Cache de roles limpiado')
  }

  /**
   * Limpia cache específico de un rol
   * @param {number|string} roleId
   */
  clearRoleCache(roleId) {
    for (const key of this.cache.keys()) {
      if (key.includes(`role_${roleId}`)) {
        this.cache.delete(key)
      }
    }
  }

  /**
   * Obtiene el tamaño del cache
   * @returns {number}
   */
  getCacheSize() {
    return this.cache.size
  }

  /**
   * Valida datos de rol antes de crear/actualizar
   * @private
   */
  _validateRoleData(data) {
    if (!data.nombre || data.nombre.trim() === '') {
      throw new Error('El nombre del rol es requerido')
    }

    if (data.nombre.length < 3) {
      throw new Error('El nombre del rol debe tener al menos 3 caracteres')
    }

    if (data.nombre.length > 50) {
      throw new Error('El nombre del rol no puede exceder 50 caracteres')
    }
  }

  /**
   * Manejo centralizado de errores
   * @private
   */
  _handleError(error, defaultMsg) {
    const message = error.response?.data?.message || error.message || defaultMsg
    
    console.error('❌', message)
    
    throw {
      message,
      status: error.response?.status,
      details: error.response?.data,
      field: error.response?.data?.field,
    }
  }
}

// Exportar instancia única (singleton)
export const rolesService = new RolesService()

// También exportar la clase
export default RolesService