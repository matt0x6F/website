import { useAuthStore } from '@/stores/auth'

export default defineNuxtRouteMiddleware((to, from) => {
  const auth = useAuthStore()
  // Only run this check on the client
  if (import.meta.client && to.path.startsWith('/admin')) {
    if (!auth.isLoggedIn || !auth.userData.isStaff) {
      return navigateTo('/')
    }
  }
  // No redirect needed; just ensure auth is ready
}) 