import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import os from 'os'
import fs from 'fs'

// @vue-flow/* are normal declared dependencies (see package.json) - a plain
// `npm install` anywhere (a fresh clone, the deploy server, CI) installs
// them into node_modules exactly like every other package, and needs no
// special handling at all.
//
// The alias below exists ONLY for dev machines where node_modules itself is
// root-owned (blocking `npm install` for new packages) - there, these four
// packages get installed instead to a location the dev user actually owns
// (see wiki/dev notes), with that vendor install's own `vue` copy replaced
// by a symlink back to this project's real vue so there's only ever one Vue
// instance at runtime. Only applied when that vendor directory actually
// exists, so it never breaks a normal install elsewhere.
const vueFlowVendor = path.join(os.homedir(), '.vueflow_vendor', 'node_modules')
const useVueFlowVendor = fs.existsSync(vueFlowVendor)

export default defineConfig({
  cacheDir: '.vite_cache',
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      ...(useVueFlowVendor ? {
        '@vue-flow/core': path.join(vueFlowVendor, '@vue-flow/core'),
        '@vue-flow/controls': path.join(vueFlowVendor, '@vue-flow/controls'),
        '@vue-flow/minimap': path.join(vueFlowVendor, '@vue-flow/minimap'),
        '@vue-flow/background': path.join(vueFlowVendor, '@vue-flow/background')
      } : {})
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
