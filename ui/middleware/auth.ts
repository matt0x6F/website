import { useAuthStore } from '@/stores/auth'

export default defineNuxtRouteMiddleware(async (to, from) => {
  const auth = useAuthStore()
  if (!auth.isInitialized) {
    await auth.init()
  }
  // Only run this check on the client
  if (import.meta.client && to.path.startsWith('/admin') && !auth.isLoggedIn) {
    return navigateTo('/')
  }
  // No redirect needed; just ensure auth is ready
}) 