import { useAuthStore } from '@/stores/auth'

export default defineNuxtRouteMiddleware(async (to, from) => {
  const auth = useAuthStore()
  if (!auth.isInitialized) {
    await new Promise(resolve => {
      const stop = watch(
        () => auth.isInitialized,
        (val) => {
          if (val) {
            stop()
            resolve(true)
          }
        }
      )
    })
  }
}) 