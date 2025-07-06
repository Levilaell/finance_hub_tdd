/**
 * useCategories Hook
 * Custom hook for managing categories and categorization rules
 */

import { useCallback } from 'react'
import { useCategoriesStore, useCategoriesSelectors } from '../store/categories'
import type {
  CategoriesFilter,
  CategorizationRulesFilter,
  CategoryCreate,
  CategoryUpdate,
  CategorizationRuleCreate,
  CategorizationRuleUpdate
} from '../types/categories'

export const useCategories = () => {
  // Get state and actions from store
  const store = useCategoriesStore()
  const selectors = useCategoriesSelectors()

  // Categories actions with useCallback for performance
  const fetchCategories = useCallback(
    (filters?: CategoriesFilter) => store.fetchCategories(filters),
    [store.fetchCategories]
  )

  const fetchCategory = useCallback(
    (id: number) => store.fetchCategory(id),
    [store.fetchCategory]
  )

  const createCategory = useCallback(
    (data: CategoryCreate) => store.createCategory(data),
    [store.createCategory]
  )

  const updateCategory = useCallback(
    (id: number, data: CategoryUpdate) => store.updateCategory(id, data),
    [store.updateCategory]
  )

  const deleteCategory = useCallback(
    (id: number) => store.deleteCategory(id),
    [store.deleteCategory]
  )

  const fetchCategoryTree = useCallback(
    (companyId: number) => store.fetchCategoryTree(companyId),
    [store.fetchCategoryTree]
  )

  const setFilters = useCallback(
    (filters: CategoriesFilter) => store.setFilters(filters),
    [store.setFilters]
  )

  const clearCategoriesError = useCallback(
    () => store.clearCategoriesError(),
    [store.clearCategoriesError]
  )

  // Categorization Rules actions
  const fetchCategorizationRules = useCallback(
    (filters?: CategorizationRulesFilter) => store.fetchCategorizationRules(filters),
    [store.fetchCategorizationRules]
  )

  const fetchCategorizationRule = useCallback(
    (id: number) => store.fetchCategorizationRule(id),
    [store.fetchCategorizationRule]
  )

  const createCategorizationRule = useCallback(
    (data: CategorizationRuleCreate) => store.createCategorizationRule(data),
    [store.createCategorizationRule]
  )

  const updateCategorizationRule = useCallback(
    (id: number, data: CategorizationRuleUpdate) => store.updateCategorizationRule(id, data),
    [store.updateCategorizationRule]
  )

  const deleteCategorizationRule = useCallback(
    (id: number) => store.deleteCategorizationRule(id),
    [store.deleteCategorizationRule]
  )

  const setRulesFilters = useCallback(
    (filters: CategorizationRulesFilter) => store.setRulesFilters(filters),
    [store.setRulesFilters]
  )

  const clearRulesError = useCallback(
    () => store.clearRulesError(),
    [store.clearRulesError]
  )

  // Helper functions
  const getCategoryById = useCallback(
    (id: number) => store.categories.find(cat => cat.id === id) || null,
    [store.categories]
  )

  const getRuleById = useCallback(
    (id: number) => store.rules.find(rule => rule.id === id) || null,
    [store.rules]
  )

  const getCategoriesByParent = useCallback(
    (parentId: number | null) => {
      return store.categories.filter(cat => {
        if (parentId === null) {
          return cat.parent === null
        }
        return cat.parent?.id === parentId
      })
    },
    [store.categories]
  )

  const getRulesByCategory = useCallback(
    (categoryId: number) => {
      return store.rules.filter(rule => rule.category.id === categoryId)
    },
    [store.rules]
  )

  const getActiveCategoriesOnly = useCallback(
    () => store.categories.filter(cat => cat.is_active),
    [store.categories]
  )

  const getActiveRulesOnly = useCallback(
    () => store.rules.filter(rule => rule.is_active),
    [store.rules]
  )

  // Validation helpers
  const isCategoryNameUnique = useCallback(
    (name: string, excludeId?: number) => {
      return !store.categories.some(cat => 
        cat.name.toLowerCase() === name.toLowerCase() && cat.id !== excludeId
      )
    },
    [store.categories]
  )

  const isRuleNameUnique = useCallback(
    (name: string, excludeId?: number) => {
      return !store.rules.some(rule => 
        rule.name.toLowerCase() === name.toLowerCase() && rule.id !== excludeId
      )
    },
    [store.rules]
  )

  return {
    // Categories state
    categories: selectors.categories,
    currentCategory: selectors.currentCategory,
    categoryTree: selectors.categoryTree,
    categoriesLoading: selectors.categoriesLoading,
    categoriesError: selectors.categoriesError,
    filters: selectors.filters,
    pagination: selectors.pagination,

    // Categorization Rules state
    rules: selectors.rules,
    currentRule: selectors.currentRule,
    rulesLoading: selectors.rulesLoading,
    rulesError: selectors.rulesError,
    rulesFilters: selectors.rulesFilters,
    rulesPagination: selectors.rulesPagination,

    // Computed values
    activeCategoriesCount: selectors.activeCategoriesCount,
    systemCategoriesCount: selectors.systemCategoriesCount,
    activeRulesCount: selectors.activeRulesCount,

    // Categories actions
    fetchCategories,
    fetchCategory,
    createCategory,
    updateCategory,
    deleteCategory,
    fetchCategoryTree,
    setFilters,
    clearCategoriesError,

    // Categorization Rules actions
    fetchCategorizationRules,
    fetchCategorizationRule,
    createCategorizationRule,
    updateCategorizationRule,
    deleteCategorizationRule,
    setRulesFilters,
    clearRulesError,

    // Helper functions
    getCategoryById,
    getRuleById,
    getCategoriesByParent,
    getRulesByCategory,
    getActiveCategoriesOnly,
    getActiveRulesOnly,

    // Validation helpers
    isCategoryNameUnique,
    isRuleNameUnique
  }
}

export default useCategories