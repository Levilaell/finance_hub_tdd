import { useAuthStore } from '@/store/auth'
import { authService } from '@/services/auth'
import type { LoginRequest, RegisterRequest, User } from '@/types/auth'

export const useAuth = () => {
  const { user, isAuthenticated, isLoading, setUser, setLoading, clearAuth } = useAuthStore()

  const login = async (data: LoginRequest): Promise<void> => {
    setLoading(true)
    try {
      const response = await authService.login(data)
      setUser(response.user)
    } catch (error) {
      throw error
    } finally {
      setLoading(false)
    }
  }

  const register = async (data: RegisterRequest): Promise<void> => {
    setLoading(true)
    try {
      const response = await authService.register(data)
      setUser(response.user)
    } catch (error) {
      throw error
    } finally {
      setLoading(false)
    }
  }

  const logout = async (): Promise<void> => {
    await authService.logout()
    clearAuth()
  }

  const updateProfile = async (data: Partial<User>): Promise<void> => {
    setLoading(true)
    try {
      const updatedUser = await authService.updateProfile(data)
      setUser(updatedUser)
    } catch (error) {
      throw error
    } finally {
      setLoading(false)
    }
  }

  const checkAuth = async (): Promise<void> => {
    if (authService.isAuthenticated()) {
      setLoading(true)
      try {
        const profile = await authService.getProfile()
        setUser(profile)
      } catch {
        clearAuth()
      } finally {
        setLoading(false)
      }
    }
  }

  return {
    user,
    isAuthenticated,
    isLoading,
    login,
    register,
    logout,
    updateProfile,
    checkAuth,
  }
}