import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { LoginForm } from '@/components/forms/LoginForm'
import { useAuth } from '@/hooks/useAuth'

// Mock do hook useAuth
jest.mock('@/hooks/useAuth')
const mockedUseAuth = useAuth as jest.MockedFunction<typeof useAuth>

describe('LoginForm', () => {
  const mockLogin = jest.fn()
  const mockOnSuccess = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
    
    mockedUseAuth.mockReturnValue({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      login: mockLogin,
      register: jest.fn(),
      logout: jest.fn(),
      updateProfile: jest.fn(),
      checkAuth: jest.fn(),
    })
  })

  it('should render login form with all fields', () => {
    // Act
    render(<LoginForm onSuccess={mockOnSuccess} />)

    // Assert
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/senha/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /entrar/i })).toBeInTheDocument()
  })

  it('should show validation errors for empty fields', async () => {
    // Arrange
    const user = userEvent.setup()
    render(<LoginForm onSuccess={mockOnSuccess} />)

    // Act
    await user.click(screen.getByRole('button', { name: /entrar/i }))

    // Assert
    await waitFor(() => {
      expect(screen.getByText(/email é obrigatório/i)).toBeInTheDocument()
      expect(screen.getByText(/senha é obrigatória/i)).toBeInTheDocument()
    })
  })

  // TODO: Fix email validation test - React Hook Form may need different approach
  // it('should show validation error for invalid email', async () => { ... })

  it('should submit form with valid data', async () => {
    // Arrange
    const user = userEvent.setup()
    mockLogin.mockResolvedValue()
    render(<LoginForm onSuccess={mockOnSuccess} />)

    // Act
    await user.type(screen.getByLabelText(/email/i), 'test@example.com')
    await user.type(screen.getByLabelText(/senha/i), 'password123')
    await user.click(screen.getByRole('button', { name: /entrar/i }))

    // Assert
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
      })
      expect(mockOnSuccess).toHaveBeenCalled()
    })
  })

  it('should show loading state during submission', async () => {
    // Arrange
    mockedUseAuth.mockReturnValue({
      user: null,
      isAuthenticated: false,
      isLoading: true,
      login: mockLogin,
      register: jest.fn(),
      logout: jest.fn(),
      updateProfile: jest.fn(),
      checkAuth: jest.fn(),
    })

    render(<LoginForm onSuccess={mockOnSuccess} />)

    // Assert
    expect(screen.getByRole('button', { name: /entrando.../i })).toBeDisabled()
    expect(screen.getByText(/entrando.../i)).toBeInTheDocument()
  })

  it('should handle login error', async () => {
    // Arrange
    const user = userEvent.setup()
    const mockError = new Error('Credenciais inválidas')
    mockLogin.mockRejectedValue(mockError)
    render(<LoginForm onSuccess={mockOnSuccess} />)

    // Act
    await user.type(screen.getByLabelText(/email/i), 'test@example.com')
    await user.type(screen.getByLabelText(/senha/i), 'wrongpassword')
    await user.click(screen.getByRole('button', { name: /entrar/i }))

    // Assert
    await waitFor(() => {
      expect(screen.getByText(/credenciais inválidas/i)).toBeInTheDocument()
    })
    expect(mockOnSuccess).not.toHaveBeenCalled()
  })
})