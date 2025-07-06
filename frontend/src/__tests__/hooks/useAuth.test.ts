import { renderHook, act } from '@testing-library/react'
import { useAuth } from '@/hooks/useAuth'
import { authService } from '@/services/auth'
import { useAuthStore } from '@/store/auth'
import type { LoginRequest, RegisterRequest } from '@/types/auth'

// Mock dos serviços
jest.mock('@/services/auth')
jest.mock('@/store/auth')

const mockedAuthService = authService as jest.Mocked<typeof authService>
const mockedUseAuthStore = useAuthStore as jest.MockedFunction<typeof useAuthStore>

describe('useAuth', () => {
  const mockUser = {
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

  const mockAuthResponse = {
    user: mockUser,
    access: 'access_token',
    refresh: 'refresh_token',
  }

  let mockSetUser: jest.Mock
  let mockSetLoading: jest.Mock
  let mockClearAuth: jest.Mock

  beforeEach(() => {
    jest.clearAllMocks()

    mockSetUser = jest.fn()
    mockSetLoading = jest.fn()
    mockClearAuth = jest.fn()

    // Mock do estado inicial do store
    mockedUseAuthStore.mockReturnValue({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      setUser: mockSetUser,
      setLoading: mockSetLoading,
      clearAuth: mockClearAuth,
    })
  })

  describe('login', () => {
    it('should login user successfully', async () => {
      // Arrange
      const loginData: LoginRequest = {
        email: 'test@example.com',
        password: 'password123',
      }

      mockedAuthService.login.mockResolvedValue(mockAuthResponse)

      // Act
      const { result } = renderHook(() => useAuth())

      await act(async () => {
        await result.current.login(loginData)
      })

      // Assert
      expect(mockSetLoading).toHaveBeenCalledWith(true)
      expect(mockedAuthService.login).toHaveBeenCalledWith(loginData)
      expect(mockSetUser).toHaveBeenCalledWith(mockUser)
      expect(mockSetLoading).toHaveBeenCalledWith(false)
    })

    it('should handle login error', async () => {
      // Arrange
      const loginData: LoginRequest = {
        email: 'test@example.com',
        password: 'wrongpassword',
      }

      const mockError = new Error('Invalid credentials')
      mockedAuthService.login.mockRejectedValue(mockError)

      // Act
      const { result } = renderHook(() => useAuth())

      let thrownError: Error | null = null
      await act(async () => {
        try {
          await result.current.login(loginData)
        } catch (error) {
          thrownError = error as Error
        }
      })

      // Assert
      expect(mockSetLoading).toHaveBeenCalledWith(true)
      expect(mockedAuthService.login).toHaveBeenCalledWith(loginData)
      expect(mockSetUser).not.toHaveBeenCalled()
      expect(mockSetLoading).toHaveBeenCalledWith(false)
      expect(thrownError).toEqual(mockError)
    })
  })

  describe('register', () => {
    it('should register user successfully', async () => {
      // Arrange
      const registerData: RegisterRequest = {
        email: 'newuser@example.com',
        password: 'SecurePass123!',
        password_confirm: 'SecurePass123!',
        first_name: 'New',
        last_name: 'User',
      }

      mockedAuthService.register.mockResolvedValue(mockAuthResponse)

      // Act
      const { result } = renderHook(() => useAuth())

      await act(async () => {
        await result.current.register(registerData)
      })

      // Assert
      expect(mockSetLoading).toHaveBeenCalledWith(true)
      expect(mockedAuthService.register).toHaveBeenCalledWith(registerData)
      expect(mockSetUser).toHaveBeenCalledWith(mockUser)
      expect(mockSetLoading).toHaveBeenCalledWith(false)
    })
  })

  describe('logout', () => {
    it('should logout user successfully', async () => {
      // Arrange
      mockedAuthService.logout.mockResolvedValue()

      // Act
      const { result } = renderHook(() => useAuth())

      await act(async () => {
        await result.current.logout()
      })

      // Assert
      expect(mockedAuthService.logout).toHaveBeenCalled()
      expect(mockClearAuth).toHaveBeenCalled()
    })
  })
})