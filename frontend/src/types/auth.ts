export interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  phone?: string
  avatar?: string
  date_of_birth?: string
  timezone: string
  language: string
  email_verified: boolean
  two_factor_enabled: boolean
  date_joined: string
  last_login?: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  password_confirm: string
  first_name: string
  last_name: string
  phone?: string
}

export interface AuthResponse {
  user: User
  access: string
  refresh: string
}

export interface TokenRefreshRequest {
  refresh: string
}

export interface TokenRefreshResponse {
  access: string
}