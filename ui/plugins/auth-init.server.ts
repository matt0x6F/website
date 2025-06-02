import { useAuthStore } from '@/stores/auth'

export default defineNuxtPlugin(async (nuxtApp) => {
  if (process.server) {
    const cookie = useRequestHeaders(['cookie']).cookie || ''
    const auth = useAuthStore()
    if (!auth.isInitialized) {
      await auth.init(cookie)
    }
  }
}) 