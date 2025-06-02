import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '../auth'

// Mock the vue-router
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: vi.fn()
  })
}))

// Mock $fetch for login/logout
const mockFetch = vi.fn() as any;
globalThis.$fetch = mockFetch;

// Mock AccountsApi for whoami
const mockWhoami = vi.fn()
const mockAuthApiLogin = vi.fn()
const mockAuthApiLogout = vi.fn()
vi.mock('@/lib/api', () => ({
  AccountsApi: vi.fn(() => ({
    whoami: (...args: any[]) => mockWhoami(...args)
  })),
  AuthApi: vi.fn(() => ({
    login: (...args: any[]) => mockAuthApiLogin(...args),
    logout: (...args: any[]) => mockAuthApiLogout(...args)
  })),
  Configuration: vi.fn()
}))

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('Initialization', () => {
    it('should set userData on successful whoami', async () => {
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
      mockWhoami.mockResolvedValue(mockUser)
      const store = useAuthStore()
      await store.init()
      expect(store.userData.id).toBe(mockUser.id)
      expect(store.userData.username).toBe(mockUser.username)
      expect(store.userData.email).toBe(mockUser.email)
      expect(store.userData.firstName).toBe(mockUser.firstName)
      expect(store.userData.lastName).toBe(mockUser.lastName)
      expect(store.userData.isStaff).toBe(mockUser.isStaff)
      expect(store.userData.isActive).toBe(mockUser.isActive)
      // Optionally check dateJoined type or value if needed
      expect(store.isLoggedIn).toBe(true)
    })

    it('should clear userData on failed whoami', async () => {
      mockWhoami.mockRejectedValue(new Error('Not authenticated'))
      const store = useAuthStore()
      await store.init()
      expect(store.userData.id).toBe(-1)
      expect(store.isLoggedIn).toBe(false)
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
      mockAuthApiLogin.mockResolvedValueOnce(undefined) // Ensure login resolves
      mockWhoami.mockResolvedValueOnce(mockUser) // for getUserData after login
      mockWhoami.mockResolvedValueOnce(mockUser) // in case getUserData is called again
      const store = useAuthStore()
      await store.login('test@example.com', 'password')
      console.log('mockWhoami calls:', mockWhoami.mock.calls.length)
      expect(store.userData).toBeDefined()
      expect(store.userData.id).toBe(mockUser.id)
      expect(store.userData.username).toBe(mockUser.username)
      expect(store.userData.email).toBe(mockUser.email)
      expect(store.userData.firstName).toBe(mockUser.firstName)
      expect(store.userData.lastName).toBe(mockUser.lastName)
      expect(store.userData.isStaff).toBe(mockUser.isStaff)
      expect(store.userData.isActive).toBe(mockUser.isActive)
      expect(store.isLoggedIn).toBe(true)
      expect(mockAuthApiLogin).toHaveBeenCalledWith(
        { username: 'test@example.com', password: 'password' }
      )
    })

    it('should handle logout', async () => {
      mockAuthApiLogout.mockResolvedValueOnce(undefined) // Ensure logout resolves
      const store = useAuthStore()
      // Set userData to a logged-in user
      store.userData.id = 1
      store.userData.username = 'testuser'
      await store.logout()
      expect(store.userData.id).toBe(-1)
      expect(store.isLoggedIn).toBe(false)
      expect(mockAuthApiLogout).toHaveBeenCalledWith()
    })
  })
}) 