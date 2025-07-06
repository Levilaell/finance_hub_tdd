import { describe, it, expect, jest, beforeEach } from '@jest/globals'
import type { 
  Category, 
  CategoryCreate, 
  CategoryUpdate,
  CategorizationRule, 
  CategorizationRuleCreate, 
  CategorizationRuleUpdate,
  CategoriesResponse,
  CategorizationRulesResponse,
  CategoriesFilter,
  CategorizationRulesFilter
} from '../../types/categories'

// Mock the api service
const mockApiGet = jest.fn()
const mockApiPost = jest.fn()
const mockApiPut = jest.fn()
const mockApiPatch = jest.fn()
const mockApiDelete = jest.fn()

jest.mock('../../services/api', () => ({
  api: {
    get: mockApiGet,
    post: mockApiPost,
    put: mockApiPut,
    patch: mockApiPatch,
    delete: mockApiDelete
  }
}))

describe('Categories Service', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

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

  describe('Categories API', () => {
    it('should fetch categories with filters', async () => {
      const mockResponse: CategoriesResponse = {
        count: 1,
        next: null,
        previous: null,
        results: [mockCategory]
      }

      mockApiGet.mockResolvedValue({ data: mockResponse })

      const { categoriesService } = await import('../../services/categories')
      
      const filters: CategoriesFilter = {
        company: 1,
        is_active: true
      }

      const result = await categoriesService.getCategories(filters)

      expect(mockApiGet).toHaveBeenCalledWith('/categories/categories/', {
        params: filters
      })
      expect(result).toEqual(mockResponse)
    })

    it('should fetch single category by id', async () => {
      mockApiGet.mockResolvedValue({ data: mockCategory })

      const { categoriesService } = await import('../../services/categories')
      
      const result = await categoriesService.getCategory(1)

      expect(mockApiGet).toHaveBeenCalledWith('/categories/categories/1/')
      expect(result).toEqual(mockCategory)
    })

    it('should create new category', async () => {
      const createData: CategoryCreate = {
        company: 1,
        name: 'Nova Categoria',
        color: '#FF5722',
        is_active: true
      }

      mockApiPost.mockResolvedValue({ data: mockCategory })

      const { categoriesService } = await import('../../services/categories')
      
      const result = await categoriesService.createCategory(createData)

      expect(mockApiPost).toHaveBeenCalledWith('/categories/categories/', createData)
      expect(result).toEqual(mockCategory)
    })

    it('should update category', async () => {
      const updateData: CategoryUpdate = {
        name: 'Categoria Atualizada',
        color: '#2196F3'
      }

      const updatedCategory = { ...mockCategory, ...updateData }
      mockApiPatch.mockResolvedValue({ data: updatedCategory })

      const { categoriesService } = await import('../../services/categories')
      
      const result = await categoriesService.updateCategory(1, updateData)

      expect(mockApiPatch).toHaveBeenCalledWith('/categories/categories/1/', updateData)
      expect(result).toEqual(updatedCategory)
    })

    it('should delete category', async () => {
      mockApiDelete.mockResolvedValue({ data: null })

      const { categoriesService } = await import('../../services/categories')
      
      await categoriesService.deleteCategory(1)

      expect(mockApiDelete).toHaveBeenCalledWith('/categories/categories/1/')
    })

    it('should fetch category tree', async () => {
      const treeResponse = [mockCategory]
      mockApiGet.mockResolvedValue({ data: treeResponse })

      const { categoriesService } = await import('../../services/categories')
      
      const result = await categoriesService.getCategoryTree(1)

      expect(mockApiGet).toHaveBeenCalledWith('/categories/categories/tree/', {
        params: { company: 1 }
      })
      expect(result).toEqual(treeResponse)
    })
  })

  describe('Categorization Rules API', () => {
    it('should fetch categorization rules with filters', async () => {
      const mockResponse: CategorizationRulesResponse = {
        count: 1,
        next: null,
        previous: null,
        results: [mockRule]
      }

      mockApiGet.mockResolvedValue({ data: mockResponse })

      const { categoriesService } = await import('../../services/categories')
      
      const filters: CategorizationRulesFilter = {
        company: 1,
        is_active: true
      }

      const result = await categoriesService.getCategorizationRules(filters)

      expect(mockApiGet).toHaveBeenCalledWith('/categories/categorization-rules/', {
        params: filters
      })
      expect(result).toEqual(mockResponse)
    })

    it('should fetch single categorization rule by id', async () => {
      mockApiGet.mockResolvedValue({ data: mockRule })

      const { categoriesService } = await import('../../services/categories')
      
      const result = await categoriesService.getCategorizationRule(1)

      expect(mockApiGet).toHaveBeenCalledWith('/categories/categorization-rules/1/')
      expect(result).toEqual(mockRule)
    })

    it('should create new categorization rule', async () => {
      const createData: CategorizationRuleCreate = {
        company: 1,
        category: 1,
        name: 'Nova Regra',
        condition_type: 'CONTAINS',
        field_name: 'description',
        field_value: 'teste',
        priority: 1,
        is_active: true
      }

      mockApiPost.mockResolvedValue({ data: mockRule })

      const { categoriesService } = await import('../../services/categories')
      
      const result = await categoriesService.createCategorizationRule(createData)

      expect(mockApiPost).toHaveBeenCalledWith('/categories/categorization-rules/', createData)
      expect(result).toEqual(mockRule)
    })

    it('should update categorization rule', async () => {
      const updateData: CategorizationRuleUpdate = {
        name: 'Regra Atualizada',
        priority: 2
      }

      const updatedRule = { ...mockRule, ...updateData }
      mockApiPatch.mockResolvedValue({ data: updatedRule })

      const { categoriesService } = await import('../../services/categories')
      
      const result = await categoriesService.updateCategorizationRule(1, updateData)

      expect(mockApiPatch).toHaveBeenCalledWith('/categories/categorization-rules/1/', updateData)
      expect(result).toEqual(updatedRule)
    })

    it('should delete categorization rule', async () => {
      mockApiDelete.mockResolvedValue({ data: null })

      const { categoriesService } = await import('../../services/categories')
      
      await categoriesService.deleteCategorizationRule(1)

      expect(mockApiDelete).toHaveBeenCalledWith('/categories/categorization-rules/1/')
    })
  })

  describe('Service validation', () => {
    it('should handle API errors gracefully', async () => {
      const apiError = new Error('API Error')
      mockApiGet.mockRejectedValue(apiError)

      const { categoriesService } = await import('../../services/categories')
      
      await expect(categoriesService.getCategories({})).rejects.toThrow('API Error')
    })

    it('should build query params correctly', async () => {
      mockApiGet.mockResolvedValue({ data: { results: [] } })

      const { categoriesService } = await import('../../services/categories')
      
      const filters: CategoriesFilter = {
        company: 1,
        parent: null,
        is_active: true,
        search: 'test'
      }

      await categoriesService.getCategories(filters)

      expect(mockApiGet).toHaveBeenCalledWith('/categories/categories/', {
        params: filters
      })
    })
  })
})