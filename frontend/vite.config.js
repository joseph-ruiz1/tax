import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import path from 'node:path'

// https://vite.dev/config/
export default defineConfig(async ({ mode }) => {
  const plugins = [vue()]
  
  // Only import and use devtools in local development
  if (mode === 'local') {
    const vueDevTools = (await import('vite-plugin-vue-devtools')).default
    plugins.push(vueDevTools())
  }
  
  return {
    plugins,
    
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      },
    },
    
    build: {
      outDir: 'dist',
      emptyOutDir: true,
      manifest: true
    },
    
    server: {
      proxy: {
        '/api': {
          target: 'http://127.0.0.1:8000/tax/api',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
        }
      }
    }
  }
})