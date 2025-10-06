// src/config/appConfig.js

// Nombre y versión de la app
export const APP_NAME = 'Jey2'
export const APP_VERSION = '1.0.0'

// URL base del backend (puede usar variable de entorno de Vite)
export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Colores o temas globales (opcional)
export const THEME = {
  primary: '#2563eb',
  secondary: '#facc15',
  danger: '#dc2626',
  success: '#16a34a',
}

// Alguna otra configuración global que quieras
export const PAGINATION_DEFAULT = {
  page: 1,
  limit: 10,
}
