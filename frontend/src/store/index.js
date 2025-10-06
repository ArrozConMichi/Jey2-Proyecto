// src/store/index.js
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

const pinia = createPinia()

// ===== Plugin para persistencia =====
pinia.use(piniaPluginPersistedstate)

export default pinia
