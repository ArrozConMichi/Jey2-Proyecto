import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path' // <- necesario para los alias

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'), // <- aquí le decimos que @ apunta a src/
    },
  },
})
