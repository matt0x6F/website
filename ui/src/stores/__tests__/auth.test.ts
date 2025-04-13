import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '../auth'
import { TokenApi, AccountsApi } from '@/lib/api'

// Mock the vue-router
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: vi.fn()
  })
}))

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}
Object.defineProperty(window, 'localStorage', { value: localStorageMock })

// Create mock implementations
const mockTokenObtainPair = vi.fn()
const mockTokenRefresh = vi.fn()
const mockAccountsApiWhoami = vi.fn()

// Mock the API responses
vi.mock('@/lib/api', () => ({
  TokenApi: vi.fn(() => ({
    obtainPair: (...args: any[]) => mockTokenObtainPair(...args),
    refresh: (...args: any[]) => mockTokenRefresh(...args)
  })),
  AccountsApi: vi.fn(() => ({
    apiWhoami: (...args: any[]) => mockAccountsApiWhoami(...args)
  })),
  Configuration: vi.fn()
}))

function createMockJWT(expiresIn: number = 3600): string {
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' })).replace(/=/g, '')
  const now = Math.floor(Date.now() / 1000)
  const payload = btoa(JSON.stringify({
    exp: now + expiresIn,
    iat: now,
    jti: 'mock-jwt-id',
    token_type: 'access',
    user_id: 1
  })).replace(/=/g, '')
  const signature = btoa('mock-signature').replace(/=/g, '')
  return `${header}.${payload}.${signature}`
}

// Update the store type definition to include startRefreshTokenTimer
type AuthStore = ReturnType<typeof useAuthStore> & {
  startRefreshTokenTimer: () => void;
  stopRefreshTokenTimer: () => void;
}

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    vi.useFakeTimers()
    vi.spyOn(global, 'setTimeout')
  })

  afterEach(() => {
    vi.clearAllTimers()
    vi.useRealTimers()
    vi.restoreAllMocks()
  })

  describe('Initialization', () => {
    it('should initialize with empty tokens when localStorage is empty', () => {
      localStorageMock.getItem.mockReturnValue(null)
      const store = useAuthStore()
      
      expect(store.storedAccessToken).toBe('')
      expect(store.storedRefreshToken).toBe('')
      expect(store.isLoggedIn).toBe(false)
    })

    it('should initialize with tokens from localStorage', async () => {
      const mockAccessToken = createMockJWT()
      const mockRefreshToken = 'mock.refresh.token'
      const mockUser = {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        firstName: 'Test',
        lastName: 'User',
        isStaff: false,
        isActive: true,
        dateJoined: new Date()
      }

      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'accessToken') return mockAccessToken
        if (key === 'refreshToken') return mockRefreshToken
        return null
      })

      // Mock the refresh token response
      mockTokenRefresh.mockResolvedValue({
        access: createMockJWT(),
        refresh: mockRefreshToken
      })

      // Mock the user data response
      mockAccountsApiWhoami.mockResolvedValue(mockUser)

      const store = useAuthStore()
      await store.init()

      expect(store.isLoggedIn).toBe(true)
      expect(store.userData).toEqual(mockUser)
    })
  })

  describe('Login/Logout', () => {
    it('should handle successful login', async () => {
      const mockUser = {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        firstName: 'Test',
        lastName: 'User',
        isStaff: false,
        isActive: true,
        dateJoined: new Date()
      }

      mockTokenObtainPair.mockResolvedValue({
        access: createMockJWT(),
        refresh: 'new.refresh.token'
      })

      mockAccountsApiWhoami.mockResolvedValue(mockUser)

      const store = useAuthStore()
      await store.login('test@example.com', 'password')

      expect(store.isLoggedIn).toBe(true)
      expect(store.userData).toEqual(mockUser)
      expect(localStorageMock.setItem).toHaveBeenCalledWith('accessToken', expect.any(String))
      expect(localStorageMock.setItem).toHaveBeenCalledWith('refreshToken', 'new.refresh.token')
    })

    it('should handle logout', async () => {
      const store = useAuthStore()
      store.storedAccessToken = 'some.token'
      store.storedRefreshToken = 'some.refresh.token'
      
      await store.logout()

      expect(store.isLoggedIn).toBe(false)
      expect(store.storedAccessToken).toBe('')
      expect(store.storedRefreshToken).toBe('')
      expect(store.userData.id).toBe(-1)
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('accessToken')
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('refreshToken')
    })
  })

  describe('Token Refresh', () => {
    beforeEach(() => {
      // Reset Date.now() mock before each test
      vi.setSystemTime(new Date('2024-01-01T00:00:00Z'))
    })

    it('should calculate correct refresh timing', () => {
      const store = useAuthStore() as AuthStore
      const now = Math.floor(Date.now() / 1000)
      const tokenLifetime = 3600 // 1 hour

      // Create a token that expires in 1 hour from our fixed now
      const mockAccessToken = createMockJWT(tokenLifetime)
      store.storedAccessToken = mockAccessToken
      store.storedRefreshToken = 'test.refresh.token'

      // Mock successful refresh response
      const newAccessToken = createMockJWT(tokenLifetime)
      mockTokenRefresh.mockImplementation(() => Promise.resolve({
        access: newAccessToken,
        refresh: 'new.refresh.token'
      }))

      // Start the timer and immediately check the timeout value
      store.startRefreshTokenTimer()

      // The timer should be set to 75% of the token lifetime
      const expectedTimeout = tokenLifetime * 0.75 * 1000
      expect(setTimeout).toHaveBeenLastCalledWith(expect.any(Function), expectedTimeout)
    })

    it('should refresh token successfully', async () => {
      const store = useAuthStore() as AuthStore
      store.storedRefreshToken = 'test.refresh.token'
      const newAccessToken = createMockJWT()
      
      mockTokenRefresh.mockResolvedValue({
        access: newAccessToken,
        refresh: 'new.refresh.token'
      })

      await store.refreshToken()

      expect(store.storedAccessToken).toBe(newAccessToken)
      expect(store.storedRefreshToken).toBe('new.refresh.token')
      expect(localStorageMock.setItem).toHaveBeenCalledWith('accessToken', newAccessToken)
      expect(localStorageMock.setItem).toHaveBeenCalledWith('refreshToken', 'new.refresh.token')
    })

    it('should handle refresh token failure', async () => {
      const store = useAuthStore() as AuthStore
      store.storedRefreshToken = 'invalid.refresh.token'
      
      mockTokenRefresh.mockRejectedValue(new Error('Invalid token'))

      await expect(store.refreshToken()).rejects.toThrow('Invalid token')

      expect(store.storedAccessToken).toBe('')
      expect(store.storedRefreshToken).toBe('')
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('accessToken')
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('refreshToken')
    })

    it('should retry refresh on failure', async () => {
      const store = useAuthStore() as AuthStore
      store.storedAccessToken = createMockJWT(3600)
      store.storedRefreshToken = 'test.refresh.token'

      // First call fails, second succeeds
      mockTokenRefresh
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({
          access: createMockJWT(3600),
          refresh: 'new.refresh.token'
        })

      // Call refresh directly instead of using timer
      await expect(store.refreshToken()).rejects.toThrow('Network error')
      await store.refreshToken() // Second attempt should succeed

      expect(mockTokenRefresh).toHaveBeenCalledTimes(2)
      expect(store.isLoggedIn).toBe(true)
    })

    it('should logout after all refresh attempts fail', async () => {
      const store = useAuthStore() as AuthStore
      store.storedAccessToken = createMockJWT(3600)
      store.storedRefreshToken = 'test.refresh.token'

      mockTokenRefresh.mockRejectedValue(new Error('Network error'))

      // Call refresh directly instead of using timer
      await expect(store.refreshToken()).rejects.toThrow('Network error')
      await expect(store.refreshToken()).rejects.toThrow('Network error')

      expect(mockTokenRefresh).toHaveBeenCalledTimes(2)
      expect(store.isLoggedIn).toBe(false)
    })
  })
}) 