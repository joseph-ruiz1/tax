import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import path from 'node:path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  build: {
    outDir: 'dist', // where files go after build
    emptyOutDir: true, // clean it before each build
    manifest: true     // useful if Django templates want to use hashed file names
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000/tax/api',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''), // important!
      }
    }
  }
})
