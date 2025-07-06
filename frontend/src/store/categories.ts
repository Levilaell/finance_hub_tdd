/**
 * Categories Store
 * State management for categories and categorization rules using Zustand
 */

import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { categoriesService } from '../services/categories'
import type {
  Category,
  CategoryCreate,
  CategoryUpdate,
  CategorizationRule,
  CategorizationRuleCreate,
  CategorizationRuleUpdate,
  CategoriesFilter,
  CategorizationRulesFilter,
  CategoryTree
} from '../types/categories'

interface Pagination {
  count: number
  page: number
  pageSize: number
  totalPages: number
}

interface CategoriesState {
  // Categories state
  categories: Category[]
  currentCategory: Category | null
  categoryTree: CategoryTree[]
  categoriesLoading: boolean
  categoriesError: string | null
  filters: CategoriesFilter
  pagination: Pagination

  // Categorization Rules state
  rules: CategorizationRule[]
  currentRule: CategorizationRule | null
  rulesLoading: boolean
  rulesError: string | null
  rulesFilters: CategorizationRulesFilter
  rulesPagination: Pagination

  // Categories actions
  fetchCategories: (filters?: CategoriesFilter) => Promise<void>
  fetchCategory: (id: number) => Promise<void>
  createCategory: (data: CategoryCreate) => Promise<Category>
  updateCategory: (id: number, data: CategoryUpdate) => Promise<Category>
  deleteCategory: (id: number) => Promise<void>
  fetchCategoryTree: (companyId: number) => Promise<void>
  setCategories: (categories: Category[]) => void
  setCurrentCategory: (category: Category | null) => void
  setCategoriesLoading: (loading: boolean) => void
  setCategoriesError: (error: string | null) => void
  clearCategoriesError: () => void
  setFilters: (filters: CategoriesFilter) => void

  // Categorization Rules actions
  fetchCategorizationRules: (filters?: CategorizationRulesFilter) => Promise<void>
  fetchCategorizationRule: (id: number) => Promise<void>
  createCategorizationRule: (data: CategorizationRuleCreate) => Promise<CategorizationRule>
  updateCategorizationRule: (id: number, data: CategorizationRuleUpdate) => Promise<CategorizationRule>
  deleteCategorizationRule: (id: number) => Promise<void>
  setCategorizationRules: (rules: CategorizationRule[]) => void
  setCurrentRule: (rule: CategorizationRule | null) => void
  setRulesLoading: (loading: boolean) => void
  setRulesError: (error: string | null) => void
  clearRulesError: () => void
  setRulesFilters: (filters: CategorizationRulesFilter) => void

  // Utility actions
  resetState: () => void
}

const initialPagination: Pagination = {
  count: 0,
  page: 1,
  pageSize: 20,
  totalPages: 0
}

export const useCategoriesStore = create<CategoriesState>()(
  devtools(
    (set, get) => ({
      // Initial state
      categories: [],
      currentCategory: null,
      categoryTree: [],
      categoriesLoading: false,
      categoriesError: null,
      filters: {},
      pagination: initialPagination,

      rules: [],
      currentRule: null,
      rulesLoading: false,
      rulesError: null,
      rulesFilters: {},
      rulesPagination: initialPagination,

      // Categories actions
      fetchCategories: async (filters = {}) => {
        set({ categoriesLoading: true, categoriesError: null })
        
        try {
          const response = await categoriesService.getCategories(filters)
          
          set({
            categories: response.results,
            pagination: {
              count: response.count,
              page: filters.page || 1,
              pageSize: 20,
              totalPages: Math.ceil(response.count / 20)
            },
            filters,
            categoriesLoading: false
          })
        } catch (error) {
          set({
            categoriesError: error instanceof Error ? error.message : 'Unknown error',
            categoriesLoading: false
          })
        }
      },

      fetchCategory: async (id: number) => {
        try {
          const category = await categoriesService.getCategory(id)
          set({ currentCategory: category })
        } catch (error) {
          set({
            categoriesError: error instanceof Error ? error.message : 'Unknown error'
          })
        }
      },

      createCategory: async (data: CategoryCreate) => {
        try {
          const newCategory = await categoriesService.createCategory(data)
          
          set(state => ({
            categories: [...state.categories, newCategory]
          }))
          
          return newCategory
        } catch (error) {
          set({
            categoriesError: error instanceof Error ? error.message : 'Unknown error'
          })
          throw error
        }
      },

      updateCategory: async (id: number, data: CategoryUpdate) => {
        try {
          const updatedCategory = await categoriesService.updateCategory(id, data)
          
          set(state => ({
            categories: state.categories.map(cat => 
              cat.id === id ? updatedCategory : cat
            ),
            currentCategory: state.currentCategory?.id === id ? updatedCategory : state.currentCategory
          }))
          
          return updatedCategory
        } catch (error) {
          set({
            categoriesError: error instanceof Error ? error.message : 'Unknown error'
          })
          throw error
        }
      },

      deleteCategory: async (id: number) => {
        try {
          await categoriesService.deleteCategory(id)
          
          set(state => ({
            categories: state.categories.filter(cat => cat.id !== id),
            currentCategory: state.currentCategory?.id === id ? null : state.currentCategory
          }))
        } catch (error) {
          set({
            categoriesError: error instanceof Error ? error.message : 'Unknown error'
          })
          throw error
        }
      },

      fetchCategoryTree: async (companyId: number) => {
        try {
          const tree = await categoriesService.getCategoryTree(companyId)
          set({ categoryTree: tree })
        } catch (error) {
          set({
            categoriesError: error instanceof Error ? error.message : 'Unknown error'
          })
        }
      },

      setCategories: (categories: Category[]) => set({ categories }),
      setCurrentCategory: (category: Category | null) => set({ currentCategory: category }),
      setCategoriesLoading: (loading: boolean) => set({ categoriesLoading: loading }),
      setCategoriesError: (error: string | null) => set({ categoriesError: error }),
      clearCategoriesError: () => set({ categoriesError: null }),
      setFilters: (filters: CategoriesFilter) => set({ filters }),

      // Categorization Rules actions
      fetchCategorizationRules: async (filters = {}) => {
        set({ rulesLoading: true, rulesError: null })
        
        try {
          const response = await categoriesService.getCategorizationRules(filters)
          
          set({
            rules: response.results,
            rulesPagination: {
              count: response.count,
              page: filters.page || 1,
              pageSize: 20,
              totalPages: Math.ceil(response.count / 20)
            },
            rulesFilters: filters,
            rulesLoading: false
          })
        } catch (error) {
          set({
            rulesError: error instanceof Error ? error.message : 'Unknown error',
            rulesLoading: false
          })
        }
      },

      fetchCategorizationRule: async (id: number) => {
        try {
          const rule = await categoriesService.getCategorizationRule(id)
          set({ currentRule: rule })
        } catch (error) {
          set({
            rulesError: error instanceof Error ? error.message : 'Unknown error'
          })
        }
      },

      createCategorizationRule: async (data: CategorizationRuleCreate) => {
        try {
          const newRule = await categoriesService.createCategorizationRule(data)
          
          set(state => ({
            rules: [...state.rules, newRule]
          }))
          
          return newRule
        } catch (error) {
          set({
            rulesError: error instanceof Error ? error.message : 'Unknown error'
          })
          throw error
        }
      },

      updateCategorizationRule: async (id: number, data: CategorizationRuleUpdate) => {
        try {
          const updatedRule = await categoriesService.updateCategorizationRule(id, data)
          
          set(state => ({
            rules: state.rules.map(rule => 
              rule.id === id ? updatedRule : rule
            ),
            currentRule: state.currentRule?.id === id ? updatedRule : state.currentRule
          }))
          
          return updatedRule
        } catch (error) {
          set({
            rulesError: error instanceof Error ? error.message : 'Unknown error'
          })
          throw error
        }
      },

      deleteCategorizationRule: async (id: number) => {
        try {
          await categoriesService.deleteCategorizationRule(id)
          
          set(state => ({
            rules: state.rules.filter(rule => rule.id !== id),
            currentRule: state.currentRule?.id === id ? null : state.currentRule
          }))
        } catch (error) {
          set({
            rulesError: error instanceof Error ? error.message : 'Unknown error'
          })
          throw error
        }
      },

      setCategorizationRules: (rules: CategorizationRule[]) => set({ rules }),
      setCurrentRule: (rule: CategorizationRule | null) => set({ currentRule: rule }),
      setRulesLoading: (loading: boolean) => set({ rulesLoading: loading }),
      setRulesError: (error: string | null) => set({ rulesError: error }),
      clearRulesError: () => set({ rulesError: null }),
      setRulesFilters: (filters: CategorizationRulesFilter) => set({ rulesFilters: filters }),

      // Utility actions
      resetState: () => set({
        categories: [],
        currentCategory: null,
        categoryTree: [],
        categoriesLoading: false,
        categoriesError: null,
        filters: {},
        pagination: initialPagination,
        rules: [],
        currentRule: null,
        rulesLoading: false,
        rulesError: null,
        rulesFilters: {},
        rulesPagination: initialPagination
      })
    }),
    {
      name: 'categories-store'
    }
  )
)

// Export selectors for easier usage
export const useCategoriesSelectors = () => {
  const store = useCategoriesStore()
  
  return {
    // Categories selectors
    categories: store.categories,
    currentCategory: store.currentCategory,
    categoryTree: store.categoryTree,
    categoriesLoading: store.categoriesLoading,
    categoriesError: store.categoriesError,
    filters: store.filters,
    pagination: store.pagination,
    
    // Rules selectors
    rules: store.rules,
    currentRule: store.currentRule,
    rulesLoading: store.rulesLoading,
    rulesError: store.rulesError,
    rulesFilters: store.rulesFilters,
    rulesPagination: store.rulesPagination,
    
    // Computed selectors
    activeCategoriesCount: store.categories.filter(cat => cat.is_active).length,
    systemCategoriesCount: store.categories.filter(cat => cat.is_system).length,
    activeRulesCount: store.rules.filter(rule => rule.is_active).length
  }
}

export default useCategoriesStore