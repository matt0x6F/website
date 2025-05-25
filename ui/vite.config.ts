import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import vueDevTools from 'vite-plugin-vue-devtools'
import Components from 'unplugin-vue-components/vite';
import {PrimeVueResolver} from '@primevue/auto-import-resolver';
import tailwindcss from '@tailwindcss/vite'
import { visualizer } from 'rollup-plugin-visualizer'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueJsx(),
    vueDevTools(),
    Components({
      resolvers: [
        PrimeVueResolver()
      ]
    }),
    tailwindcss(),
    visualizer({
      open: true, // Automatically opens the report in your browser
      filename: 'dist/bundle-report.html', // Output file
      gzipSize: true,
      brotliSize: true,
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          'primevue-vendor': ['primevue', '@primeuix/themes', '@primeuix/utils'],
          'highlight-vendor': ['highlight.js'],
        },
      },
    },
  },
  preview: {
    port: 3000,
    host: '0.0.0.0',
  },
})
