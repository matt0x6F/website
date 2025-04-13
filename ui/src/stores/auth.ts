import { ref, computed, reactive } from 'vue'
import { defineStore } from 'pinia'
import { AccountsApi, Configuration, TokenApi, type ConfigurationParameters, type UserSelf, type UpdateAccount, type NewAccount } from '@/lib/api'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
  const storedAccessToken = ref<string>(localStorage.getItem("accessToken") || "")
  const storedRefreshToken = ref<string>(localStorage.getItem("refreshToken") || "")
  const refreshTokenTimeout = ref<number>(0)
  const userData = reactive<UserSelf>({
    id: -1,
    username: "",
    email: "",
    firstName: "",
    lastName: "",
    isStaff: false,
    isActive: false,
    dateJoined: new Date(),
  })
  // refresh token is not undefined or blank
  const isLoggedIn = computed(() => storedRefreshToken.value !== "")
  const router = useRouter()
  const redirectUrl = ref<string | null>(null)

  async function init() {
    if (storedRefreshToken.value) {
      try {
        await refreshToken()
        await getUserData()
        startRefreshTokenTimer()
      } catch (error) {
        logout()
        throw error
      }
    }
  }

  async function getUserData() {
    if (!storedAccessToken.value) {
        throw new Error('No access token available')
    }

    const params: ConfigurationParameters = {
        basePath: import.meta.env.VITE_API_URL,
        accessToken: storedAccessToken.value,
        headers: {
            'Authorization': `Bearer ${storedAccessToken.value}`
        }
    }

    const config = new Configuration(params)

    try {
        const accountsApi = new AccountsApi(config)
        const user = await accountsApi.apiWhoami()

        userData.id = user.id
        userData.username = user.username
        userData.email = user.email
        userData.firstName = user.firstName
        userData.lastName = user.lastName
        userData.isStaff = user.isStaff
        userData.isActive = user.isActive
        userData.dateJoined = user.dateJoined
    } catch (error) {
        if (error instanceof Error && 
            'status' in error && 
            error.status === 401 && 
            storedRefreshToken.value) {
            await refreshToken()
            // Try again with the new token
            return await getUserData()
        }
        throw error
    }
  }

  async function login(username: string, password: string) {
    const params: ConfigurationParameters = {
        basePath: import.meta.env.VITE_API_URL,
    }

    const anonConfig = new Configuration(params)
    const tokenApi = new TokenApi(anonConfig)

    try {
        const tokens = await tokenApi.obtainPair({ 
          tokenObtainPairInputSchema: { email: username, password: password } 
        })
        
        storedAccessToken.value = tokens.access
        storedRefreshToken.value = tokens.refresh
        
        localStorage.setItem("accessToken", storedAccessToken.value)
        localStorage.setItem("refreshToken", storedRefreshToken.value)

        const authedParams: ConfigurationParameters = {
            basePath: import.meta.env.VITE_API_URL,
            accessToken: storedAccessToken.value,
            headers: {
                'Authorization': `Bearer ${storedAccessToken.value}`
            }
        }
        const authedConfig = new Configuration(authedParams)
        const accountsApi = new AccountsApi(authedConfig)

        const user = await accountsApi.apiWhoami()
        
        userData.id = user.id
        userData.username = user.username
        userData.email = user.email
        userData.firstName = user.firstName
        userData.lastName = user.lastName
        userData.isStaff = user.isStaff
        userData.isActive = user.isActive
        userData.dateJoined = user.dateJoined

        startRefreshTokenTimer();

        // After successful login, check for redirect
        if (redirectUrl.value) {
          const redirect = redirectUrl.value
          redirectUrl.value = null // Clear the redirect URL
          router.push(redirect)
        }
    } catch (error) {
        // If anything fails, clear everything
        clearTokens()
        throw error
    }
  }

  function clearTokens() {
    localStorage.removeItem("accessToken")
    localStorage.removeItem("refreshToken")
    storedAccessToken.value = ""
    storedRefreshToken.value = ""
  }

  async function logout() {
    try {
      clearTokens()
      // Reset user data
      userData.id = -1
      userData.username = ""
      userData.email = ""
      userData.firstName = ""
      userData.lastName = ""
      userData.isStaff = false
      userData.isActive = false
      userData.dateJoined = new Date()

      stopRefreshTokenTimer()
      router.push('/')
    } catch (error) {
      throw error
    }
  }

  async function refreshToken() {
    const params: ConfigurationParameters = {
      basePath: import.meta.env.VITE_API_URL,
    }

    const config = new Configuration(params)
    const tokenApi = new TokenApi(config)
    
    try {
      const tokens = await tokenApi.refresh({ 
        tokenRefreshInputSchema: { refresh: storedRefreshToken.value } 
      })

      storedAccessToken.value = tokens.access !== null ? tokens.access : storedAccessToken.value
      storedRefreshToken.value = tokens.refresh

      localStorage.setItem("accessToken", storedAccessToken.value)
      localStorage.setItem("refreshToken", storedRefreshToken.value)

      startRefreshTokenTimer()
    } catch (error) {
      clearTokens()
      throw error
    }
  }

  function startRefreshTokenTimer() {
    // Clear any existing timeout first
    stopRefreshTokenTimer()
    
    try {
      // Parse the access token
      const jwtBase64 = storedAccessToken.value.split('.')[1];
      const jwtToken = JSON.parse(atob(jwtBase64));

      // Set a timeout to refresh the token when it's at 75% of its lifetime
      // This ensures we refresh well before expiration
      const expires = new Date(jwtToken.exp * 1000);
      const issued = new Date(jwtToken.iat * 1000);
      const tokenLifetime = expires.getTime() - issued.getTime();
      const refreshAt = issued.getTime() + (tokenLifetime * 0.75);
      const timeout = refreshAt - Date.now();
      
      // Only set the timer if the timeout is positive and reasonable
      if (timeout > 0 && timeout < tokenLifetime) {
        refreshTokenTimeout.value = window.setTimeout(async () => {
          try {
            await refreshToken()
            // After successful refresh, start the timer again
            startRefreshTokenTimer()
          } catch (error) {
            console.error('Token refresh failed:', error)
            // If refresh fails, attempt one more time after a short delay
            const retryTimeout = window.setTimeout(async () => {
              try {
                await refreshToken()
                startRefreshTokenTimer()
              } catch (retryError) {
                console.error('Token refresh retry failed:', retryError)
                await logout()
              }
              clearTimeout(retryTimeout)
            }, 5000) // Wait 5 seconds before retry
          }
        }, timeout);
      } else if (storedRefreshToken.value) {
        // If we're already past the refresh time but have a refresh token, try to refresh immediately
        refreshToken().catch(async (error) => {
          console.error('Immediate token refresh failed:', error)
          await logout()
        })
      }
    } catch (error) {
      console.error('Error starting refresh timer:', error)
      stopRefreshTokenTimer()
    }
  }

  function stopRefreshTokenTimer() {
    if (refreshTokenTimeout.value) {
      clearTimeout(refreshTokenTimeout.value)
      refreshTokenTimeout.value = 0
    }
  }

  async function updateProfile(data: UpdateAccount) {
    if (!storedAccessToken.value) {
      throw new Error('No access token available')
    }

    const params: ConfigurationParameters = {
      basePath: import.meta.env.VITE_API_URL,
      accessToken: storedAccessToken.value,
      headers: {
        'Authorization': `Bearer ${storedAccessToken.value}`
      }
    }

    const config = new Configuration(params)

    try {
      const accountsApi = new AccountsApi(config)
      const response = await accountsApi.apiUpdateSelf({
        updateAccount: data
      })
      
      // Update all user data fields from response
      userData.username = response.username
      userData.email = response.email
      userData.firstName = response.firstName
      userData.lastName = response.lastName
      return response
    } catch (error) {
      if (error instanceof Error && 
          'status' in error && 
          error.status === 401 && 
          storedRefreshToken.value) {
        await refreshToken()
        // Try again with the new token
        return await updateProfile(data)
      }
      throw error
    }
  }

  function setRedirectUrl(url: string) {
    redirectUrl.value = url
  }

  async function signup(newAccount: NewAccount) {
    const params: ConfigurationParameters = {
      basePath: import.meta.env.VITE_API_URL,
    }
    const config = new Configuration(params)
    const api = new AccountsApi(config);
    const response = await api.apiSignUp({ newAccount });
    return response;
  }

  // Initialize the store when created
  init()

  // Export all methods that might be needed externally
  return { 
    storedAccessToken, 
    storedRefreshToken,
    userData, 
    isLoggedIn, 
    login, 
    logout,
    init,
    refreshToken,
    getUserData,
    updateProfile,
    redirectUrl,
    setRedirectUrl,
    signup,
    startRefreshTokenTimer,
    stopRefreshTokenTimer,
  }
})
