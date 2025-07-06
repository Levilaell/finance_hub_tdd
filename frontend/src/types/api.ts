export interface ApiError {
  message: string
  status: number
  details?: Record<string, string[]>
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface ApiResponse<T = any> {
  data?: T
  error?: ApiError
  loading: boolean
}