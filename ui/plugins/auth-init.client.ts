import { useAuthStore } from '@/stores/auth'

export default defineNuxtPlugin(async (nuxtApp) => {
  const auth = useAuthStore()
  if (!auth.isInitialized) {
    await auth.init()
  }
}) 