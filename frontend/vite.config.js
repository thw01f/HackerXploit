import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import os from 'os'

// @vue-flow/* packages live outside node_modules, in a separately-installed
// vendor directory (see wiki/dev notes) - this project's node_modules is
// root-owned in some environments, blocking `npm install` for new packages,
// so these are installed to a location the dev user actually owns and
// resolved here instead. The vendor install's own `vue` copy is replaced
// with a symlink back to this project's real vue, so there is only ever one
// Vue instance at runtime.
const vueFlowVendor = path.join(os.homedir(), '.vueflow_vendor', 'node_modules')

export default defineConfig({
  cacheDir: '.vite_cache',
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@vue-flow/core': path.join(vueFlowVendor, '@vue-flow/core'),
      '@vue-flow/controls': path.join(vueFlowVendor, '@vue-flow/controls'),
      '@vue-flow/minimap': path.join(vueFlowVendor, '@vue-flow/minimap'),
      '@vue-flow/background': path.join(vueFlowVendor, '@vue-flow/background')
    },
    dedupe: ['vue']
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/oauth': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/uploads': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/socket.io': {
        target: 'http://localhost:5000',
        ws: true
      }
    }
  }
})
