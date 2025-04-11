import { describe, it, expect, beforeEach, vi } from 'vitest'
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
    tokenObtainPair: (...args: any[]) => mockTokenObtainPair(...args),
    tokenRefresh: (...args: any[]) => mockTokenRefresh(...args)
  })),
  AccountsApi: vi.fn(() => ({
    accountsApiWhoami: (...args: any[]) => mockAccountsApiWhoami(...args)
  })),
  Configuration: vi.fn()
}))

function createMockJWT(expiresIn: number = 3600): string {
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }))
  const now = Math.floor(Date.now() / 1000)
  const payload = btoa(JSON.stringify({
    exp: now + expiresIn,
    iat: now,
    jti: 'mock-jwt-id',
    token_type: 'access',
    user_id: 1
  }))
  const signature = btoa('mock-signature')
  return `${header}.${payload}.${signature}`
}

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
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
    it('should refresh tokens successfully', async () => {
      const store = useAuthStore()
      store.storedRefreshToken = 'old.refresh.token'
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
      const store = useAuthStore()
      store.storedRefreshToken = 'invalid.refresh.token'
      
      mockTokenRefresh.mockRejectedValue(new Error('Invalid token'))

      await expect(store.refreshToken()).rejects.toThrow('Invalid token')
      expect(store.storedAccessToken).toBe('')
      expect(store.storedRefreshToken).toBe('')
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('accessToken')
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('refreshToken')
    })
  })
}) 