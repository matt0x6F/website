import { defineVitestConfig } from '@nuxt/test-utils/config'

export default defineVitestConfig({
  test: {
    // You can add custom Vitest options here if needed
    environment: 'jsdom',
    include: ['**/__tests__/**/*.{test,spec}.{ts,js}'],
    // Example: setupFiles: ['<rootDir>/test/setup.ts'],
  },
})
