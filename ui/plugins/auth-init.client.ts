import { useAuthStore } from '@/stores/auth'

// This plugin only runs on the client. It initializes auth if not already hydrated from SSR.
export default defineNuxtPlugin(async (nuxtApp) => {
  const auth = useAuthStore()
  if (!auth.isInitialized) {
    await auth.init()
  }
}) 