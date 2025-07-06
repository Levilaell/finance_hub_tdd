import { describe, it, expect, jest, beforeEach } from '@jest/globals'
import type { 
  Category, 
  CategorizationRule, 
  CategoriesFilter,
  CategorizationRulesFilter
} from '../../types/categories'

// Mock the categories service
const mockGetCategories = jest.fn()
const mockGetCategory = jest.fn()
const mockCreateCategory = jest.fn()
const mockUpdateCategory = jest.fn()
const mockDeleteCategory = jest.fn()
const mockGetCategoryTree = jest.fn()
const mockGetCategorizationRules = jest.fn()
const mockGetCategorizationRule = jest.fn()
const mockCreateCategorizationRule = jest.fn()
const mockUpdateCategorizationRule = jest.fn()
const mockDeleteCategorizationRule = jest.fn()

jest.mock('../../services/categories', () => ({
  categoriesService: {
    getCategories: mockGetCategories,
    getCategory: mockGetCategory,
    createCategory: mockCreateCategory,
    updateCategory: mockUpdateCategory,
    deleteCategory: mockDeleteCategory,
    getCategoryTree: mockGetCategoryTree,
    getCategorizationRules: mockGetCategorizationRules,
    getCategorizationRule: mockGetCategorizationRule,
    createCategorizationRule: mockCreateCategorizationRule,
    updateCategorizationRule: mockUpdateCategorizationRule,
    deleteCategorizationRule: mockDeleteCategorizationRule,
  }
}))

describe('Categories Store', () => {
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

  beforeEach(async () => {
    jest.clearAllMocks()
    // Reset store state before each test
    const { useCategoriesStore } = await import('../../store/categories')
    useCategoriesStore.getState().resetState()
  })

  describe('Categories state management', () => {
    it('should initialize with default state', async () => {
      const { useCategoriesStore } = await import('../../store/categories')
      const store = useCategoriesStore.getState()

      expect(store.categories).toEqual([])
      expect(store.currentCategory).toBeNull()
      expect(store.categoryTree).toEqual([])
      expect(store.categoriesLoading).toBe(false)
      expect(store.categoriesError).toBeNull()
      expect(store.filters).toEqual({})
      expect(store.pagination).toEqual({
        count: 0,
        page: 1,
        pageSize: 20,
        totalPages: 0
      })
    })

    it('should fetch categories successfully', async () => {
      const mockResponse = {
        count: 1,
        next: null,
        previous: null,
        results: [mockCategory]
      }

      mockGetCategories.mockResolvedValue(mockResponse)

      const { useCategoriesStore } = await import('../../store/categories')
      const store = useCategoriesStore.getState()

      await store.fetchCategories({ company: 1 })

      expect(mockGetCategories).toHaveBeenCalledWith({ company: 1 })
      expect(store.categories).toEqual([mockCategory])
      expect(store.pagination.count).toBe(1)
      expect(store.categoriesLoading).toBe(false)
      expect(store.categoriesError).toBeNull()
    })

    it('should handle fetch categories error', async () => {
      const error = new Error('API Error')
      mockGetCategories.mockRejectedValue(error)

      const { useCategoriesStore } = await import('../../store/categories')
      const store = useCategoriesStore.getState()

      await store.fetchCategories({ company: 1 })

      expect(store.categories).toEqual([])
      expect(store.categoriesLoading).toBe(false)
      expect(store.categoriesError).toBe('API Error')
    })

    it('should fetch single category successfully', async () => {
      mockGetCategory.mockResolvedValue(mockCategory)

      const { useCategoriesStore } = await import('../../store/categories')
      const store = useCategoriesStore.getState()

      await store.fetchCategory(1)

      expect(mockGetCategory).toHaveBeenCalledWith(1)
      expect(store.currentCategory).toEqual(mockCategory)
    })

    it('should create category successfully', async () => {
      const createData = {
        company: 1,
        name: 'Nova Categoria',
        color: '#FF5722',
        is_active: true
      }

      mockCreateCategory.mockResolvedValue(mockCategory)

      const { useCategoriesStore } = await import('../../store/categories')
      const store = useCategoriesStore.getState()

      const result = await store.createCategory(createData)

      expect(mockCreateCategory).toHaveBeenCalledWith(createData)
      expect(result).toEqual(mockCategory)
      expect(store.categories).toContain(mockCategory)
    })

    it('should update category successfully', async () => {
      const updateData = { name: 'Categoria Atualizada' }
      const updatedCategory = { ...mockCategory, ...updateData }

      mockUpdateCategory.mockResolvedValue(updatedCategory)

      const { useCategoriesStore } = await import('../../store/categories')
      const store = useCategoriesStore.getState()
      
      // Set initial categories
      store.setCategories([mockCategory])

      const result = await store.updateCategory(1, updateData)

      expect(mockUpdateCategory).toHaveBeenCalledWith(1, updateData)
      expect(result).toEqual(updatedCategory)
      expect(store.categories[0]).toEqual(updatedCategory)
    })

    it('should delete category successfully', async () => {
      mockDeleteCategory.mockResolvedValue(undefined)

      const { useCategoriesStore } = await import('../../store/categories')
      const store = useCategoriesStore.getState()
      
      // Set initial categories
      store.setCategories([mockCategory])

      await store.deleteCategory(1)

      expect(mockDeleteCategory).toHaveBeenCalledWith(1)
      expect(store.categories).toHaveLength(0)
    })

    it('should fetch category tree successfully', async () => {
      const treeData = [mockCategory]
      mockGetCategoryTree.mockResolvedValue(treeData)

      const { useCategoriesStore } = await import('../../store/categories')
      const store = useCategoriesStore.getState()

      await store.fetchCategoryTree(1)

      expect(mockGetCategoryTree).toHaveBeenCalledWith(1)
      expect(store.categoryTree).toEqual(treeData)
    })
  })

  describe('Categorization Rules state management', () => {
    it('should initialize rules state correctly', async () => {
      const { useCategoriesStore } = await import('../../store/categories')
      const store = useCategoriesStore.getState()

      expect(store.rules).toEqual([])
      expect(store.currentRule).toBeNull()
      expect(store.rulesLoading).toBe(false)
      expect(store.rulesError).toBeNull()
      expect(store.rulesFilters).toEqual({})
      expect(store.rulesPagination).toEqual({
        count: 0,
        page: 1,
        pageSize: 20,
        totalPages: 0
      })
    })

    it('should fetch categorization rules successfully', async () => {
      const mockResponse = {
        count: 1,
        next: null,
        previous: null,
        results: [mockRule]
      }

      mockGetCategorizationRules.mockResolvedValue(mockResponse)

      const { useCategoriesStore } = await import('../../store/categories')
      const store = useCategoriesStore.getState()

      await store.fetchCategorizationRules({ company: 1 })

      expect(mockGetCategorizationRules).toHaveBeenCalledWith({ company: 1 })
      expect(store.rules).toEqual([mockRule])
      expect(store.rulesPagination.count).toBe(1)
      expect(store.rulesLoading).toBe(false)
      expect(store.rulesError).toBeNull()
    })

    it('should create categorization rule successfully', async () => {
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

      const { useCategoriesStore } = await import('../../store/categories')
      const store = useCategoriesStore.getState()

      const result = await store.createCategorizationRule(createData)

      expect(mockCreateCategorizationRule).toHaveBeenCalledWith(createData)
      expect(result).toEqual(mockRule)
      expect(store.rules).toContain(mockRule)
    })

    it('should update categorization rule successfully', async () => {
      const updateData = { name: 'Regra Atualizada' }
      const updatedRule = { ...mockRule, ...updateData }

      mockUpdateCategorizationRule.mockResolvedValue(updatedRule)

      const { useCategoriesStore } = await import('../../store/categories')
      const store = useCategoriesStore.getState()
      
      // Set initial rules
      store.setCategorizationRules([mockRule])

      const result = await store.updateCategorizationRule(1, updateData)

      expect(mockUpdateCategorizationRule).toHaveBeenCalledWith(1, updateData)
      expect(result).toEqual(updatedRule)
      expect(store.rules[0]).toEqual(updatedRule)
    })

    it('should delete categorization rule successfully', async () => {
      mockDeleteCategorizationRule.mockResolvedValue(undefined)

      const { useCategoriesStore } = await import('../../store/categories')
      const store = useCategoriesStore.getState()
      
      // Set initial rules
      store.setCategorizationRules([mockRule])

      await store.deleteCategorizationRule(1)

      expect(mockDeleteCategorizationRule).toHaveBeenCalledWith(1)
      expect(store.rules).toHaveLength(0)
    })
  })

  describe('State setters and getters', () => {
    it('should set filters correctly', async () => {
      const filters: CategoriesFilter = { company: 1, is_active: true }

      const { useCategoriesStore } = await import('../../store/categories')
      const store = useCategoriesStore.getState()

      store.setFilters(filters)

      expect(store.filters).toEqual(filters)
    })

    it('should set loading states correctly', async () => {
      const { useCategoriesStore } = await import('../../store/categories')
      const store = useCategoriesStore.getState()

      store.setCategoriesLoading(true)
      store.setRulesLoading(true)

      expect(store.categoriesLoading).toBe(true)
      expect(store.rulesLoading).toBe(true)
    })

    it('should clear errors correctly', async () => {
      const { useCategoriesStore } = await import('../../store/categories')
      const store = useCategoriesStore.getState()

      // Set some errors first
      store.setCategoriesError('Some error')
      store.setRulesError('Another error')

      // Clear errors
      store.clearCategoriesError()
      store.clearRulesError()

      expect(store.categoriesError).toBeNull()
      expect(store.rulesError).toBeNull()
    })

    it('should reset store state correctly', async () => {
      const { useCategoriesStore } = await import('../../store/categories')
      const store = useCategoriesStore.getState()

      // Set some state
      store.setCategories([mockCategory])
      store.setCategorizationRules([mockRule])
      store.setFilters({ company: 1 })

      // Reset
      store.resetState()

      expect(store.categories).toEqual([])
      expect(store.rules).toEqual([])
      expect(store.filters).toEqual({})
      expect(store.currentCategory).toBeNull()
      expect(store.currentRule).toBeNull()
    })
  })
})