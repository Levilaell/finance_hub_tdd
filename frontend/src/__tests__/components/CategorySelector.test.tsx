import React from 'react'
import { describe, it, expect, jest, beforeEach } from '@jest/globals'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { Category } from '../../types/categories'

// Mock the useCategories hook
const mockFetchCategories = jest.fn()
const mockFetchCategoryTree = jest.fn()
const mockClearCategoriesError = jest.fn()

const mockCategoriesData: Category[] = [
  {
    id: 1,
    company: 1,
    parent: null,
    name: 'Receitas',
    color: '#4CAF50',
    is_system: false,
    is_active: true,
    full_path: 'Receitas',
    children_count: 3,
    rules_count: 2,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  },
  {
    id: 2,
    company: 1,
    parent: { id: 1, name: 'Receitas', color: '#4CAF50' },
    name: 'Salário',
    color: '#2196F3',
    is_system: false,
    is_active: true,
    full_path: 'Receitas > Salário',
    children_count: 0,
    rules_count: 1,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  },
  {
    id: 3,
    company: 1,
    parent: null,
    name: 'Despesas',
    color: '#F44336',
    is_system: false,
    is_active: true,
    full_path: 'Despesas',
    children_count: 2,
    rules_count: 0,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  }
]

const mockUseCategoriesReturn = {
  categories: mockCategoriesData,
  categoryTree: mockCategoriesData,
  categoriesLoading: false,
  categoriesError: null,
  fetchCategories: mockFetchCategories,
  fetchCategoryTree: mockFetchCategoryTree,
  clearCategoriesError: mockClearCategoriesError,
  getActiveCategoriesOnly: () => mockCategoriesData.filter(cat => cat.is_active)
}

jest.mock('../../hooks/useCategories', () => ({
  useCategories: () => mockUseCategoriesReturn,
  default: () => mockUseCategoriesReturn
}))

describe('CategorySelector Component', () => {
  const defaultProps = {
    value: null,
    onChange: jest.fn(),
    companyId: 1
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Basic rendering', () => {
    it('should render category selector correctly', async () => {
      const { CategorySelector } = await import('../../components/CategorySelector')
      
      render(<CategorySelector {...defaultProps} />)

      expect(screen.getByRole('combobox')).toBeInTheDocument()
      expect(screen.getByPlaceholderText('Selecione uma categoria')).toBeInTheDocument()
    })

    it('should display selected category when value is provided', async () => {
      const { CategorySelector } = await import('../../components/CategorySelector')
      
      render(
        <CategorySelector 
          {...defaultProps} 
          value={mockCategoriesData[0]} 
        />
      )

      expect(screen.getByDisplayValue('Receitas')).toBeInTheDocument()
    })

    it('should show placeholder when no value is selected', async () => {
      const { CategorySelector } = await import('../../components/CategorySelector')
      
      render(<CategorySelector {...defaultProps} />)

      expect(screen.getByPlaceholderText('Selecione uma categoria')).toBeInTheDocument()
    })

    it('should be disabled when disabled prop is true', async () => {
      const { CategorySelector } = await import('../../components/CategorySelector')
      
      render(<CategorySelector {...defaultProps} disabled />)

      expect(screen.getByRole('combobox')).toBeDisabled()
    })
  })

  describe('Data loading', () => {
    it('should fetch categories on mount', async () => {
      const { CategorySelector } = await import('../../components/CategorySelector')
      
      render(<CategorySelector {...defaultProps} />)

      expect(mockFetchCategories).toHaveBeenCalledWith({
        company: 1,
        is_active: true
      })
    })

    it('should show loading state', async () => {
      mockUseCategoriesReturn.categoriesLoading = true

      const { CategorySelector } = await import('../../components/CategorySelector')
      
      render(<CategorySelector {...defaultProps} />)

      expect(screen.getByText(/carregando/i)).toBeInTheDocument()
    })

    it('should show error state', async () => {
      mockUseCategoriesReturn.categoriesError = 'Erro ao carregar categorias'
      mockUseCategoriesReturn.categoriesLoading = false

      const { CategorySelector } = await import('../../components/CategorySelector')
      
      render(<CategorySelector {...defaultProps} />)

      expect(screen.getByText(/erro ao carregar categorias/i)).toBeInTheDocument()
    })

    it('should show retry button on error', async () => {
      mockUseCategoriesReturn.categoriesError = 'Erro ao carregar'
      mockUseCategoriesReturn.categoriesLoading = false

      const { CategorySelector } = await import('../../components/CategorySelector')
      
      render(<CategorySelector {...defaultProps} />)

      const retryButton = screen.getByRole('button', { name: /tentar novamente/i })
      expect(retryButton).toBeInTheDocument()

      fireEvent.click(retryButton)

      expect(mockFetchCategories).toHaveBeenCalledTimes(2) // Once on mount, once on retry
    })
  })

  describe('Category selection', () => {
    beforeEach(() => {
      mockUseCategoriesReturn.categoriesLoading = false
      mockUseCategoriesReturn.categoriesError = null
    })

    it('should open dropdown when clicked', async () => {
      const { CategorySelector } = await import('../../components/CategorySelector')
      
      render(<CategorySelector {...defaultProps} />)

      const selector = screen.getByRole('combobox')
      fireEvent.click(selector)

      await waitFor(() => {
        expect(screen.getByText('Receitas')).toBeInTheDocument()
        expect(screen.getByText('Despesas')).toBeInTheDocument()
      })
    })

    it('should call onChange when category is selected', async () => {
      const { CategorySelector } = await import('../../components/CategorySelector')
      const onChange = jest.fn()
      
      render(<CategorySelector {...defaultProps} onChange={onChange} />)

      const selector = screen.getByRole('combobox')
      fireEvent.click(selector)

      await waitFor(() => {
        const option = screen.getByText('Receitas')
        fireEvent.click(option)
      })

      expect(onChange).toHaveBeenCalledWith(mockCategoriesData[0])
    })

    it('should filter categories based on search input', async () => {
      const { CategorySelector } = await import('../../components/CategorySelector')
      
      render(<CategorySelector {...defaultProps} searchable />)

      const input = screen.getByRole('combobox')
      
      // First click to open dropdown
      fireEvent.click(input)
      
      // Then type to search
      await userEvent.type(input, 'Rec')

      await waitFor(() => {
        expect(screen.getByText('Receitas')).toBeInTheDocument()
        expect(screen.queryByText('Despesas')).not.toBeInTheDocument()
      })
    })

    it('should show hierarchical display when showFullPath is true', async () => {
      const { CategorySelector } = await import('../../components/CategorySelector')
      
      render(<CategorySelector {...defaultProps} showFullPath />)

      const selector = screen.getByRole('combobox')
      fireEvent.click(selector)

      await waitFor(() => {
        expect(screen.getByText('Receitas > Salário')).toBeInTheDocument()
      })
    })

    it('should allow clearing selection when clearable is true', async () => {
      const { CategorySelector } = await import('../../components/CategorySelector')
      const onChange = jest.fn()
      
      render(
        <CategorySelector 
          {...defaultProps} 
          value={mockCategoriesData[0]}
          onChange={onChange}
          clearable 
        />
      )

      const clearButton = screen.getByRole('button', { name: /limpar/i })
      fireEvent.click(clearButton)

      expect(onChange).toHaveBeenCalledWith(null)
    })
  })

  describe('Category filtering', () => {
    beforeEach(() => {
      mockUseCategoriesReturn.categoriesLoading = false
      mockUseCategoriesReturn.categoriesError = null
    })

    it('should filter by parent category when parentId is provided', async () => {
      const { CategorySelector } = await import('../../components/CategorySelector')
      
      render(<CategorySelector {...defaultProps} parentId={1} />)

      expect(mockFetchCategories).toHaveBeenCalledWith({
        company: 1,
        is_active: true,
        parent: 1
      })
    })

    it('should show only active categories by default', async () => {
      const { CategorySelector } = await import('../../components/CategorySelector')
      
      render(<CategorySelector {...defaultProps} />)

      expect(mockFetchCategories).toHaveBeenCalledWith({
        company: 1,
        is_active: true
      })
    })

    it('should show all categories when showInactive is true', async () => {
      const { CategorySelector } = await import('../../components/CategorySelector')
      
      render(<CategorySelector {...defaultProps} showInactive />)

      expect(mockFetchCategories).toHaveBeenCalledWith({
        company: 1
      })
    })

    it('should exclude system categories when excludeSystem is true', async () => {
      const { CategorySelector } = await import('../../components/CategorySelector')
      
      render(<CategorySelector {...defaultProps} excludeSystem />)

      expect(mockFetchCategories).toHaveBeenCalledWith({
        company: 1,
        is_active: true,
        is_system: false
      })
    })
  })

  describe('Color display', () => {
    beforeEach(() => {
      mockUseCategoriesReturn.categoriesLoading = false
      mockUseCategoriesReturn.categoriesError = null
    })

    it('should show category colors when showColors is true', async () => {
      const { CategorySelector } = await import('../../components/CategorySelector')
      
      render(<CategorySelector {...defaultProps} showColors />)

      const selector = screen.getByRole('combobox')
      fireEvent.click(selector)

      await waitFor(() => {
        const colorIndicators = screen.getAllByTestId(/category-color-\d+/)
        expect(colorIndicators.length).toBeGreaterThan(0)
      })
    })

    it('should display correct color for each category', async () => {
      const { CategorySelector } = await import('../../components/CategorySelector')
      
      render(<CategorySelector {...defaultProps} showColors />)

      const selector = screen.getByRole('combobox')
      fireEvent.click(selector)

      await waitFor(() => {
        const receitasColor = screen.getByTestId('category-color-1')
        expect(receitasColor).toHaveStyle('background-color: #4CAF50')
      })
    })
  })

  describe('Tree mode', () => {
    beforeEach(() => {
      mockUseCategoriesReturn.categoriesLoading = false
      mockUseCategoriesReturn.categoriesError = null
    })

    it('should fetch category tree when treeMode is true', async () => {
      const { CategorySelector } = await import('../../components/CategorySelector')
      
      render(<CategorySelector {...defaultProps} treeMode />)

      expect(mockFetchCategoryTree).toHaveBeenCalledWith(1)
    })

    it('should display categories in tree structure', async () => {
      const { CategorySelector } = await import('../../components/CategorySelector')
      
      render(<CategorySelector {...defaultProps} treeMode />)

      const selector = screen.getByRole('combobox')
      fireEvent.click(selector)

      await waitFor(() => {
        expect(screen.getByText('Receitas')).toBeInTheDocument()
        expect(screen.getByText('Salário')).toBeInTheDocument()
      })
    })
  })

  describe('Form integration', () => {
    it('should display validation error', async () => {
      const { CategorySelector } = await import('../../components/CategorySelector')
      
      render(
        <CategorySelector 
          {...defaultProps} 
          error="Campo obrigatório"
        />
      )

      expect(screen.getByText('Campo obrigatório')).toBeInTheDocument()
    })

    it('should show required indicator when required is true', async () => {
      const { CategorySelector } = await import('../../components/CategorySelector')
      
      render(
        <CategorySelector 
          {...defaultProps} 
          label="Categoria"
          required
        />
      )

      expect(screen.getByText('Categoria *')).toBeInTheDocument()
    })

    it('should display help text', async () => {
      const { CategorySelector } = await import('../../components/CategorySelector')
      
      render(
        <CategorySelector 
          {...defaultProps} 
          helpText="Selecione a categoria da transação"
        />
      )

      expect(screen.getByText('Selecione a categoria da transação')).toBeInTheDocument()
    })
  })
})