// https://nuxt.com/docs/api/configuration/nuxt-config
import Aura from '@primeuix/themes/aura'
import tailwindcss from '@tailwindcss/vite'

export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },

  // If you want to keep your source files in src/, uncomment the next line:
  // srcDir: 'src/',
  css: ['@/assets/main.css', '@/assets/github.css', '@/assets/github-dark-dimmed.css', 'primeicons/primeicons.css'],
  vite: {
    plugins: [
      tailwindcss(),
    ],
  },
  modules: [
    '@primevue/nuxt-module',
    '@pinia/nuxt',
    '@nuxt/eslint',
    '@nuxt/icon',
    '@nuxt/image',
    '@nuxt/scripts',
    '@nuxt/test-utils'
    // Add more modules here (e.g., PrimeVue Nuxt module if available)
  ],
  primevue: {
    options: {
      theme: {
        preset: Aura
      }
    }
  },
  // PrimeVue plugin registration can be done in /plugins (see docs)
  // Runtime config, env vars, etc. can be added here
  app: {
    head: {
      link: [
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css?family=Inter:400,500,600,700&display=swap' }
      ]
    }
  }
})