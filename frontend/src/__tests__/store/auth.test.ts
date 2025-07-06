import { useAuthStore } from '@/store/auth'
import type { User } from '@/types/auth'

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
}
global.localStorage = localStorageMock as any

describe('AuthStore', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    // Reset store state
    useAuthStore.setState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
    })
  })

  const mockUser: User = {
    id: '1',
    email: 'test@example.com',
    first_name: 'Test',
    last_name: 'User',
    timezone: 'America/Sao_Paulo',
    language: 'pt-BR',
    email_verified: true,
    two_factor_enabled: false,
    date_joined: '2024-01-01T00:00:00Z',
  }

  describe('setUser', () => {
    it('should set user and authentication state', () => {
      // Act
      useAuthStore.getState().setUser(mockUser)

      // Assert
      const state = useAuthStore.getState()
      expect(state.user).toEqual(mockUser)
      expect(state.isAuthenticated).toBe(true)
    })

    it('should clear user when passed null', () => {
      // Arrange - Set initial user
      useAuthStore.getState().setUser(mockUser)

      // Act
      useAuthStore.getState().setUser(null)

      // Assert
      const state = useAuthStore.getState()
      expect(state.user).toBeNull()
      expect(state.isAuthenticated).toBe(false)
    })
  })

  describe('setLoading', () => {
    it('should set loading state', () => {
      // Act
      useAuthStore.getState().setLoading(true)

      // Assert
      expect(useAuthStore.getState().isLoading).toBe(true)

      // Act
      useAuthStore.getState().setLoading(false)

      // Assert
      expect(useAuthStore.getState().isLoading).toBe(false)
    })
  })

  describe('clearAuth', () => {
    it('should clear authentication state', () => {
      // Arrange - Set initial state
      useAuthStore.setState({
        user: mockUser,
        isAuthenticated: true,
        isLoading: false,
      })

      // Act
      useAuthStore.getState().clearAuth()

      // Assert
      const state = useAuthStore.getState()
      expect(state.user).toBeNull()
      expect(state.isAuthenticated).toBe(false)
      expect(state.isLoading).toBe(false)
    })
  })
})