import { authService } from '@/services/auth'
import { apiService } from '@/services/api'
import type { LoginRequest, RegisterRequest, AuthResponse } from '@/types/auth'

// Mock do apiService
jest.mock('@/services/api', () => ({
  apiService: {
    post: jest.fn(),
    setTokens: jest.fn(),
    clearTokens: jest.fn(),
    isAuthenticated: jest.fn(),
  },
}))

const mockedApiService = apiService as jest.Mocked<typeof apiService>

describe('AuthService', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('login', () => {
    it('should login user with valid credentials', async () => {
      // Arrange
      const loginData: LoginRequest = {
        email: 'test@example.com',
        password: 'password123',
      }

      const mockResponse: AuthResponse = {
        user: {
          id: '1',
          email: 'test@example.com',
          first_name: 'Test',
          last_name: 'User',
          timezone: 'America/Sao_Paulo',
          language: 'pt-BR',
          email_verified: true,
          two_factor_enabled: false,
          date_joined: '2024-01-01T00:00:00Z',
        },
        access: 'access_token',
        refresh: 'refresh_token',
      }

      mockedApiService.post.mockResolvedValue(mockResponse)

      // Act
      const result = await authService.login(loginData)

      // Assert
      expect(mockedApiService.post).toHaveBeenCalledWith('/api/auth/login/', loginData)
      expect(mockedApiService.setTokens).toHaveBeenCalledWith('access_token', 'refresh_token')
      expect(result).toEqual(mockResponse)
    })

    it('should throw error on invalid credentials', async () => {
      // Arrange
      const loginData: LoginRequest = {
        email: 'test@example.com',
        password: 'wrongpassword',
      }

      const mockError = new Error('Invalid credentials')
      mockedApiService.post.mockRejectedValue(mockError)

      // Act & Assert
      await expect(authService.login(loginData)).rejects.toThrow('Invalid credentials')
      expect(mockedApiService.setTokens).not.toHaveBeenCalled()
    })
  })

  describe('register', () => {
    it('should register new user', async () => {
      // Arrange
      const registerData: RegisterRequest = {
        email: 'newuser@example.com',
        password: 'SecurePass123!',
        password_confirm: 'SecurePass123!',
        first_name: 'New',
        last_name: 'User',
      }

      const mockResponse: AuthResponse = {
        user: {
          id: '2',
          email: 'newuser@example.com',
          first_name: 'New',
          last_name: 'User',
          timezone: 'America/Sao_Paulo',
          language: 'pt-BR',
          email_verified: false,
          two_factor_enabled: false,
          date_joined: '2024-01-01T00:00:00Z',
        },
        access: 'access_token',
        refresh: 'refresh_token',
      }

      mockedApiService.post.mockResolvedValue(mockResponse)

      // Act
      const result = await authService.register(registerData)

      // Assert
      expect(mockedApiService.post).toHaveBeenCalledWith('/api/auth/register/', registerData)
      expect(mockedApiService.setTokens).toHaveBeenCalledWith('access_token', 'refresh_token')
      expect(result).toEqual(mockResponse)
    })
  })

  describe('logout', () => {
    it('should clear tokens on logout', async () => {
      // Act
      await authService.logout()

      // Assert
      expect(mockedApiService.clearTokens).toHaveBeenCalled()
    })
  })

  describe('isAuthenticated', () => {
    it('should return true when user is authenticated', () => {
      // Arrange
      mockedApiService.isAuthenticated.mockReturnValue(true)

      // Act
      const result = authService.isAuthenticated()

      // Assert
      expect(result).toBe(true)
      expect(mockedApiService.isAuthenticated).toHaveBeenCalled()
    })

    it('should return false when user is not authenticated', () => {
      // Arrange
      mockedApiService.isAuthenticated.mockReturnValue(false)

      // Act
      const result = authService.isAuthenticated()

      // Assert
      expect(result).toBe(false)
      expect(mockedApiService.isAuthenticated).toHaveBeenCalled()
    })
  })
})