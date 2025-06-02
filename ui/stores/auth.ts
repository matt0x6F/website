import { ref, computed, reactive, toRaw } from 'vue'
import { defineStore } from 'pinia'
import { AccountsApi, AuthApi, type UserSelf, type UpdateAccount, type NewAccount } from '@/lib/api'
import { useRouter } from 'vue-router'
import { useApiClient } from '@/composables/useApiClient'

export const useAuthStore = defineStore('auth', () => {
  const userData = ref<UserSelf>({
    id: -1,
    username: "",
    email: "",
    firstName: "",
    lastName: "",
    isStaff: false,
    isActive: false,
    dateJoined: new Date(),
  })
  const router = useRouter()
  const redirectUrl = ref<string | null>(null)
  const isInitialized = ref(false)

  const isLoggedIn = computed(() => userData.value.id !== -1)

  async function init(cookie?: string) {
    isInitialized.value = false
    try {
      await getUserData(cookie)
    } catch (error) {
      resetUserData()
    }
    isInitialized.value = true
  }

  async function getUserData(cookie?: string) {
    const accountsApi = useApiClient(AccountsApi, cookie)
    const user = await accountsApi.whoami()
    if (!user) throw new Error('No user returned from whoami')
    userData.value = { ...user, dateJoined: new Date(user.dateJoined) }
  }

  async function login(username: string, password: string) {
    const authApi = useApiClient(AuthApi)
    await authApi.login({ username, password })
    await getUserData()
    // After successful login, check for redirect
    if (redirectUrl.value) {
      const redirect = redirectUrl.value
      redirectUrl.value = null // Clear the redirect URL
      router.push(redirect)
    }
  }

  async function logout() {
    const authApi = useApiClient(AuthApi)
    await authApi.logout()
    resetUserData()
    router.push('/')
  }

  function resetUserData() {
    userData.value = {
      id: -1,
      username: "",
      email: "",
      firstName: "",
      lastName: "",
      isStaff: false,
      isActive: false,
      dateJoined: new Date(),
    }
  }

  async function updateProfile(data: UpdateAccount) {
    const accountsApi = useApiClient(AccountsApi)
    const response = await accountsApi.updateSelf({ updateAccount: data })
    userData.value.username = response.username
    userData.value.email = response.email
    userData.value.firstName = response.firstName
    userData.value.lastName = response.lastName
    return response
  }

  function setRedirectUrl(url: string) {
    redirectUrl.value = url
  }

  async function signup(newAccount: NewAccount) {
    const accountsApi = useApiClient(AccountsApi)
    const response = await accountsApi.signUp({ newAccount })
    return response
  }

  // Pinia SSR helpers
  function dehydrate() {
    return { userData: toRaw(userData.value), isInitialized: isInitialized.value }
  }
  function hydrate(state: any) {
    if (state?.userData) userData.value = { ...state.userData, dateJoined: new Date(state.userData.dateJoined) }
    if (typeof state?.isInitialized === 'boolean') isInitialized.value = state.isInitialized
  }

  return {
    userData,
    isLoggedIn,
    login,
    logout,
    init,
    getUserData,
    updateProfile,
    redirectUrl,
    setRedirectUrl,
    signup,
    isInitialized,
    dehydrate,
    hydrate,
  }
})
