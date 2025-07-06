/**
 * Categories Service
 * API client for categories and categorization rules
 */

import { api } from './api'
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
  CategorizationRulesFilter,
  CategoryTree
} from '../types/categories'

class CategoriesService {
  private basePath = '/categories'

  // Categories endpoints
  async getCategories(filters: CategoriesFilter = {}): Promise<CategoriesResponse> {
    const response = await api.get(`${this.basePath}/categories/`, {
      params: filters
    })
    return response.data
  }

  async getCategory(id: number): Promise<Category> {
    const response = await api.get(`${this.basePath}/categories/${id}/`)
    return response.data
  }

  async createCategory(data: CategoryCreate): Promise<Category> {
    const response = await api.post(`${this.basePath}/categories/`, data)
    return response.data
  }

  async updateCategory(id: number, data: CategoryUpdate): Promise<Category> {
    const response = await api.patch(`${this.basePath}/categories/${id}/`, data)
    return response.data
  }

  async deleteCategory(id: number): Promise<void> {
    await api.delete(`${this.basePath}/categories/${id}/`)
  }

  async getCategoryTree(companyId: number): Promise<CategoryTree[]> {
    const response = await api.get(`${this.basePath}/categories/tree/`, {
      params: { company: companyId }
    })
    return response.data
  }

  // Categorization Rules endpoints
  async getCategorizationRules(filters: CategorizationRulesFilter = {}): Promise<CategorizationRulesResponse> {
    const response = await api.get(`${this.basePath}/categorization-rules/`, {
      params: filters
    })
    return response.data
  }

  async getCategorizationRule(id: number): Promise<CategorizationRule> {
    const response = await api.get(`${this.basePath}/categorization-rules/${id}/`)
    return response.data
  }

  async createCategorizationRule(data: CategorizationRuleCreate): Promise<CategorizationRule> {
    const response = await api.post(`${this.basePath}/categorization-rules/`, data)
    return response.data
  }

  async updateCategorizationRule(id: number, data: CategorizationRuleUpdate): Promise<CategorizationRule> {
    const response = await api.patch(`${this.basePath}/categorization-rules/${id}/`, data)
    return response.data
  }

  async deleteCategorizationRule(id: number): Promise<void> {
    await api.delete(`${this.basePath}/categorization-rules/${id}/`)
  }

  // Utility methods
  async testCategorizationRule(ruleId: number, transactionData: any): Promise<boolean> {
    const response = await api.post(`${this.basePath}/categorization-rules/${ruleId}/test/`, {
      transaction_data: transactionData
    })
    return response.data.matches
  }

  async applyCategorization(companyId: number, transactionIds?: number[]): Promise<{
    categorized_count: number
    total_transactions: number
  }> {
    const response = await api.post(`${this.basePath}/apply-categorization/`, {
      company: companyId,
      transaction_ids: transactionIds
    })
    return response.data
  }
}

// Export singleton instance
export const categoriesService = new CategoriesService()
export default categoriesService

// Named export for testing
export { CategoriesService }