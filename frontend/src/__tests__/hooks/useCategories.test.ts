import { describe, it, expect, jest, beforeEach } from '@jest/globals'
import { renderHook, act } from '@testing-library/react'
import type { 
  Category, 
  CategorizationRule 
} from '../../types/categories'

// Mock the categories store
const mockFetchCategories = jest.fn()
const mockFetchCategory = jest.fn()
const mockCreateCategory = jest.fn()
const mockUpdateCategory = jest.fn()
const mockDeleteCategory = jest.fn()
const mockFetchCategoryTree = jest.fn()
const mockFetchCategorizationRules = jest.fn()
const mockCreateCategorizationRule = jest.fn()
const mockUpdateCategorizationRule = jest.fn()
const mockDeleteCategorizationRule = jest.fn()
const mockSetFilters = jest.fn()
const mockSetRulesFilters = jest.fn()
const mockClearCategoriesError = jest.fn()
const mockClearRulesError = jest.fn()

const mockStoreState = {
  categories: [],
  currentCategory: null,
  categoryTree: [],
  categoriesLoading: false,
  categoriesError: null,
  filters: {},
  pagination: {
    count: 0,
    page: 1,
    pageSize: 20,
    totalPages: 0
  },
  rules: [],
  currentRule: null,
  rulesLoading: false,
  rulesError: null,
  rulesFilters: {},
  rulesPagination: {
    count: 0,
    page: 1,
    pageSize: 20,
    totalPages: 0
  },
  // Computed values
  activeCategoriesCount: 0,
  systemCategoriesCount: 0,
  activeRulesCount: 0,
  // Actions
  fetchCategories: mockFetchCategories,
  fetchCategory: mockFetchCategory,
  createCategory: mockCreateCategory,
  updateCategory: mockUpdateCategory,
  deleteCategory: mockDeleteCategory,
  fetchCategoryTree: mockFetchCategoryTree,
  fetchCategorizationRules: mockFetchCategorizationRules,
  createCategorizationRule: mockCreateCategorizationRule,
  updateCategorizationRule: mockUpdateCategorizationRule,
  deleteCategorizationRule: mockDeleteCategorizationRule,
  setFilters: mockSetFilters,
  setRulesFilters: mockSetRulesFilters,
  clearCategoriesError: mockClearCategoriesError,
  clearRulesError: mockClearRulesError
}

jest.mock('../../store/categories', () => ({
  useCategoriesStore: () => mockStoreState,
  useCategoriesSelectors: () => mockStoreState
}))

describe('useCategories Hook', () => {
  const mockCategory: Category = {
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
  }

  const mockRule: CategorizationRule = {
    id: 1,
    company: 1,
    category: {
      id: 1,
      name: 'Receitas',
      color: '#4CAF50',
      full_path: 'Receitas'
    },
    name: 'Regra Salário',
    condition_type: 'CONTAINS',
    condition_display: 'Contains',
    field_name: 'description',
    field_display: 'Description',
    field_value: 'salario',
    priority: 1,
    is_active: true,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Categories operations', () => {
    it('should provide categories state and actions', async () => {
      const { useCategories } = await import('../../hooks/useCategories')
      const { result } = renderHook(() => useCategories())

      expect(result.current.categories).toEqual([])
      expect(result.current.currentCategory).toBeNull()
      expect(result.current.categoryTree).toEqual([])
      expect(result.current.categoriesLoading).toBe(false)
      expect(result.current.categoriesError).toBeNull()
      expect(result.current.filters).toEqual({})
      expect(result.current.pagination).toBeDefined()

      // Check actions are available
      expect(typeof result.current.fetchCategories).toBe('function')
      expect(typeof result.current.createCategory).toBe('function')
      expect(typeof result.current.updateCategory).toBe('function')
      expect(typeof result.current.deleteCategory).toBe('function')
      expect(typeof result.current.fetchCategoryTree).toBe('function')
    })

    it('should call fetchCategories with correct parameters', async () => {
      const { useCategories } = await import('../../hooks/useCategories')
      const { result } = renderHook(() => useCategories())

      const filters = { company: 1, is_active: true }

      await act(async () => {
        await result.current.fetchCategories(filters)
      })

      expect(mockFetchCategories).toHaveBeenCalledWith(filters)
    })

    it('should call createCategory with correct data', async () => {
      const { useCategories } = await import('../../hooks/useCategories')
      const { result } = renderHook(() => useCategories())

      const createData = {
        company: 1,
        name: 'Nova Categoria',
        color: '#FF5722',
        is_active: true
      }

      mockCreateCategory.mockResolvedValue(mockCategory)

      let createdCategory: Category | undefined

      await act(async () => {
        createdCategory = await result.current.createCategory(createData)
      })

      expect(mockCreateCategory).toHaveBeenCalledWith(createData)
      expect(createdCategory).toEqual(mockCategory)
    })

    it('should call updateCategory with correct parameters', async () => {
      const { useCategories } = await import('../../hooks/useCategories')
      const { result } = renderHook(() => useCategories())

      const updateData = { name: 'Categoria Atualizada' }
      const updatedCategory = { ...mockCategory, ...updateData }

      mockUpdateCategory.mockResolvedValue(updatedCategory)

      let updated: Category | undefined

      await act(async () => {
        updated = await result.current.updateCategory(1, updateData)
      })

      expect(mockUpdateCategory).toHaveBeenCalledWith(1, updateData)
      expect(updated).toEqual(updatedCategory)
    })

    it('should call deleteCategory with correct id', async () => {
      const { useCategories } = await import('../../hooks/useCategories')
      const { result } = renderHook(() => useCategories())

      await act(async () => {
        await result.current.deleteCategory(1)
      })

      expect(mockDeleteCategory).toHaveBeenCalledWith(1)
    })

    it('should fetch category tree correctly', async () => {
      const { useCategories } = await import('../../hooks/useCategories')
      const { result } = renderHook(() => useCategories())

      await act(async () => {
        await result.current.fetchCategoryTree(1)
      })

      expect(mockFetchCategoryTree).toHaveBeenCalledWith(1)
    })

    it('should set filters correctly', async () => {
      const { useCategories } = await import('../../hooks/useCategories')
      const { result } = renderHook(() => useCategories())

      const filters = { company: 1, is_active: true }

      act(() => {
        result.current.setFilters(filters)
      })

      expect(mockSetFilters).toHaveBeenCalledWith(filters)
    })

    it('should clear categories error', async () => {
      const { useCategories } = await import('../../hooks/useCategories')
      const { result } = renderHook(() => useCategories())

      act(() => {
        result.current.clearCategoriesError()
      })

      expect(mockClearCategoriesError).toHaveBeenCalled()
    })
  })

  describe('Categorization Rules operations', () => {
    it('should provide rules state and actions', async () => {
      const { useCategories } = await import('../../hooks/useCategories')
      const { result } = renderHook(() => useCategories())

      expect(result.current.rules).toEqual([])
      expect(result.current.currentRule).toBeNull()
      expect(result.current.rulesLoading).toBe(false)
      expect(result.current.rulesError).toBeNull()
      expect(result.current.rulesFilters).toEqual({})
      expect(result.current.rulesPagination).toBeDefined()

      // Check actions are available
      expect(typeof result.current.fetchCategorizationRules).toBe('function')
      expect(typeof result.current.createCategorizationRule).toBe('function')
      expect(typeof result.current.updateCategorizationRule).toBe('function')
      expect(typeof result.current.deleteCategorizationRule).toBe('function')
    })

    it('should call fetchCategorizationRules with correct parameters', async () => {
      const { useCategories } = await import('../../hooks/useCategories')
      const { result } = renderHook(() => useCategories())

      const filters = { company: 1, category: 1 }

      await act(async () => {
        await result.current.fetchCategorizationRules(filters)
      })

      expect(mockFetchCategorizationRules).toHaveBeenCalledWith(filters)
    })

    it('should call createCategorizationRule with correct data', async () => {
      const { useCategories } = await import('../../hooks/useCategories')
      const { result } = renderHook(() => useCategories())

      const createData = {
        company: 1,
        category: 1,
        name: 'Nova Regra',
        condition_type: 'CONTAINS' as const,
        field_name: 'description' as const,
        field_value: 'teste',
        priority: 1,
        is_active: true
      }

      mockCreateCategorizationRule.mockResolvedValue(mockRule)

      let createdRule: CategorizationRule | undefined

      await act(async () => {
        createdRule = await result.current.createCategorizationRule(createData)
      })

      expect(mockCreateCategorizationRule).toHaveBeenCalledWith(createData)
      expect(createdRule).toEqual(mockRule)
    })

    it('should call updateCategorizationRule with correct parameters', async () => {
      const { useCategories } = await import('../../hooks/useCategories')
      const { result } = renderHook(() => useCategories())

      const updateData = { name: 'Regra Atualizada' }
      const updatedRule = { ...mockRule, ...updateData }

      mockUpdateCategorizationRule.mockResolvedValue(updatedRule)

      let updated: CategorizationRule | undefined

      await act(async () => {
        updated = await result.current.updateCategorizationRule(1, updateData)
      })

      expect(mockUpdateCategorizationRule).toHaveBeenCalledWith(1, updateData)
      expect(updated).toEqual(updatedRule)
    })

    it('should call deleteCategorizationRule with correct id', async () => {
      const { useCategories } = await import('../../hooks/useCategories')
      const { result } = renderHook(() => useCategories())

      await act(async () => {
        await result.current.deleteCategorizationRule(1)
      })

      expect(mockDeleteCategorizationRule).toHaveBeenCalledWith(1)
    })

    it('should set rules filters correctly', async () => {
      const { useCategories } = await import('../../hooks/useCategories')
      const { result } = renderHook(() => useCategories())

      const filters = { company: 1, category: 1 }

      act(() => {
        result.current.setRulesFilters(filters)
      })

      expect(mockSetRulesFilters).toHaveBeenCalledWith(filters)
    })

    it('should clear rules error', async () => {
      const { useCategories } = await import('../../hooks/useCategories')
      const { result } = renderHook(() => useCategories())

      act(() => {
        result.current.clearRulesError()
      })

      expect(mockClearRulesError).toHaveBeenCalled()
    })
  })

  describe('Computed values', () => {
    it('should provide computed selectors', async () => {
      // Mock some categories for computed values
      mockStoreState.categories = [mockCategory, { ...mockCategory, id: 2, is_active: false }]
      mockStoreState.rules = [mockRule]

      const { useCategories } = await import('../../hooks/useCategories')
      const { result } = renderHook(() => useCategories())

      expect(typeof result.current.activeCategoriesCount).toBe('number')
      expect(typeof result.current.systemCategoriesCount).toBe('number')
      expect(typeof result.current.activeRulesCount).toBe('number')
    })

    it('should handle error states correctly', async () => {
      mockStoreState.categoriesError = 'Categories Error'
      mockStoreState.rulesError = 'Rules Error'
      mockStoreState.categoriesLoading = true
      mockStoreState.rulesLoading = true

      const { useCategories } = await import('../../hooks/useCategories')
      const { result } = renderHook(() => useCategories())

      expect(result.current.categoriesError).toBe('Categories Error')
      expect(result.current.rulesError).toBe('Rules Error')
      expect(result.current.categoriesLoading).toBe(true)
      expect(result.current.rulesLoading).toBe(true)
    })
  })
})