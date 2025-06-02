import { useAuthStore } from '@/stores/auth'

export default defineNuxtRouteMiddleware(async (to, from) => {
  const auth = useAuthStore()
  if (!auth.isInitialized) {
    await auth.init()
  }
  // If the route is under /admin and the user is not logged in, redirect to /login
  if (to.path.startsWith('/admin') && !auth.isLoggedIn) {
    return navigateTo('/')
  }
  // No redirect needed; just ensure auth is ready
}) 