// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { rolesService } from '@/services/rolesService'

// Views
import Home from '@/views/home.vue'
import Usuarios from '@/views/Usuarios.vue'
import Productos from '@/views/Productos.vue'
import Proveedores from '@/views/Proveedores.vue'
import Ventas from '@/views/Ventas.vue'
import Login from '@/views/Login.vue'

// ===== Rutas principales =====
const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true }
  },
  {
    path: '/usuarios',
    name: 'Usuarios',
    component: Usuarios,
    meta: { requiresAuth: true, roles: ['admin'] } // solo admins
  },
  {
    path: '/productos',
    name: 'Productos',
    component: Productos,
    meta: { requiresAuth: true }
  },
  {
    path: '/proveedores',
    name: 'Proveedores',
    component: Proveedores,
    meta: { requiresAuth: true }
  },
  {
    path: '/ventas',
    name: 'Ventas',
    component: Ventas,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/:catchAll(.*)',
    redirect: '/' // Redirigir rutas no encontradas al home
  }
]

// ===== Crear router =====
const router = createRouter({
  history: createWebHistory(),
  routes
})

// ===== Guard global para auth y roles =====
router.beforeEach(async (to, from, next) => {
  const requiresAuth = to.meta.requiresAuth
  const allowedRoles = to.meta.roles || []

  try {
    // Si no requiere auth, seguir
    if (!requiresAuth) return next()

    // Verificar si hay usuario logueado y roles
    const hasRole = allowedRoles.length
      ? await rolesService.currentUserHasAnyRole(allowedRoles)
      : true

    if (!hasRole) {
      console.warn('⚠️ Acceso denegado: rol no permitido')
      return next('/') // redirigir a home si no tiene permiso
    }

    next()
  } catch (error) {
    console.error('❌ Error en guard de rutas:', error)
    next('/login') // redirigir al login si falla auth
  }
})

export default router
