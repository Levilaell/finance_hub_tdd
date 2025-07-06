import { apiService } from './api'
import type { 
  LoginRequest, 
  RegisterRequest, 
  AuthResponse, 
  User 
} from '@/types/auth'

class AuthService {
  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await apiService.post<AuthResponse>('/api/auth/login/', data)
    
    // Salvar tokens
    apiService.setTokens(response.access, response.refresh)
    
    return response
  }

  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await apiService.post<AuthResponse>('/api/auth/register/', data)
    
    // Salvar tokens
    apiService.setTokens(response.access, response.refresh)
    
    return response
  }

  async logout(): Promise<void> {
    // Limpar tokens
    apiService.clearTokens()
  }

  async getProfile(): Promise<User> {
    return apiService.get<User>('/api/auth/profile/')
  }

  async updateProfile(data: Partial<User>): Promise<User> {
    return apiService.patch<User>('/api/auth/profile/', data)
  }

  isAuthenticated(): boolean {
    return apiService.isAuthenticated()
  }
}

export const authService = new AuthService()