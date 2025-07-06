import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios'
import { ApiError } from '@/types/api'

// Extend Axios config to include retry flag
interface ExtendedAxiosRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean
}

class ApiService {
  private api: AxiosInstance

  constructor() {
    this.api = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    // Request interceptor para adicionar token
    this.api.interceptors.request.use(
      (config) => {
        const token = this.getAccessToken()
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor para lidar com tokens expirados
    this.api.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as ExtendedAxiosRequestConfig

        if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
          originalRequest._retry = true

          try {
            const refreshToken = this.getRefreshToken()
            if (refreshToken) {
              const response = await this.api.post('/api/auth/token/refresh/', {
                refresh: refreshToken,
              })
              
              const { access } = response.data
              this.setAccessToken(access)
              
              // Retry original request
              originalRequest.headers.Authorization = `Bearer ${access}`
              return this.api(originalRequest)
            }
          } catch (refreshError) {
            this.clearTokens()
            if (typeof window !== 'undefined') {
              window.location.href = '/login'
            }
          }
        }

        return Promise.reject(this.handleError(error))
      }
    )
  }

  private handleError(error: AxiosError): ApiError {
    const status = error.response?.status || 500
    const data = error.response?.data as any

    if (data?.detail) {
      return {
        message: data.detail,
        status,
      }
    }

    if (data?.non_field_errors) {
      return {
        message: data.non_field_errors[0],
        status,
      }
    }

    if (typeof data === 'object' && data !== null) {
      return {
        message: 'Erro de validação',
        status,
        details: data,
      }
    }

    return {
      message: error.message || 'Erro interno do servidor',
      status,
    }
  }

  // Token management
  getAccessToken(): string | null {
    if (typeof window === 'undefined') return null
    return localStorage.getItem('access_token')
  }

  getRefreshToken(): string | null {
    if (typeof window === 'undefined') return null
    return localStorage.getItem('refresh_token')
  }

  setAccessToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', token)
    }
  }

  setRefreshToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('refresh_token', token)
    }
  }

  setTokens(access: string, refresh: string): void {
    this.setAccessToken(access)
    this.setRefreshToken(refresh)
  }

  clearTokens(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  }

  isAuthenticated(): boolean {
    return !!this.getAccessToken()
  }

  // API methods
  async get<T>(url: string, params?: any): Promise<T> {
    const response = await this.api.get(url, { params })
    return response.data
  }

  async post<T>(url: string, data?: any): Promise<T> {
    const response = await this.api.post(url, data)
    return response.data
  }

  async put<T>(url: string, data?: any): Promise<T> {
    const response = await this.api.put(url, data)
    return response.data
  }

  async patch<T>(url: string, data?: any): Promise<T> {
    const response = await this.api.patch(url, data)
    return response.data
  }

  async delete<T>(url: string): Promise<T> {
    const response = await this.api.delete(url)
    return response.data
  }
}

export const apiService = new ApiService()