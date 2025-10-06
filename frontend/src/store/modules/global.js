// src/store/modules/global.js
import { defineStore } from 'pinia'

export const useGlobalStore = defineStore('global', {
  state: () => ({
    theme: 'light',          // 'light' o 'dark'
    sidebarCollapsed: false, // sidebar abierto/cerrado
    notifications: [],       // notificaciones globales
  }),
  getters: {
    isDarkMode: (state) => state.theme === 'dark',
  },
  actions: {
    toggleTheme() {
      this.theme = this.isDarkMode ? 'light' : 'dark'
    },
    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed
    },
    addNotification(notification) {
      this.notifications.push(notification)
    },
    removeNotification(index) {
      this.notifications.splice(index, 1)
    },
  },
  persist: true, // opcional, persiste automáticamente en localStorage
})
