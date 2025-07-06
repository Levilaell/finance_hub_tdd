/**
 * Types for Categories module
 * Based on Django backend models and serializers
 */

// Condition types for categorization rules
export type ConditionType = 
  | 'CONTAINS'
  | 'EQUALS'
  | 'STARTS_WITH'
  | 'ENDS_WITH'
  | 'REGEX'
  | 'GREATER_THAN'
  | 'LESS_THAN'
  | 'GREATER_EQUAL'
  | 'LESS_EQUAL'

// Field names for categorization rules
export type FieldName = 
  | 'description'
  | 'amount'
  | 'transaction_type'
  | 'category'

// Simplified parent category interface
export interface CategoryParent {
  id: number
  name: string
  color: string
}

// Nested category interface for rules
export interface CategoryNested {
  id: number
  name: string
  color: string
  full_path: string
}

// Main Category interface (from CategorySerializer)
export interface Category {
  id: number
  company: number
  parent: CategoryParent | null
  name: string
  color: string
  is_system: boolean
  is_active: boolean
  full_path: string
  children_count: number
  rules_count: number
  created_at: string
  updated_at: string
}

// Category creation interface (from CategoryCreateSerializer)
export interface CategoryCreate {
  company: number
  parent?: number | null
  name: string
  color: string
  is_system?: boolean
  is_active?: boolean
}

// Category update interface
export interface CategoryUpdate {
  parent?: number | null
  name?: string
  color?: string
  is_active?: boolean
}

// CategorizationRule interface (from CategorizationRuleSerializer)
export interface CategorizationRule {
  id: number
  company: number
  category: CategoryNested
  name: string
  condition_type: ConditionType
  condition_display: string
  field_name: FieldName
  field_display: string
  field_value: string
  priority: number
  is_active: boolean
  created_at: string
  updated_at: string
}

// CategorizationRule creation interface (from CategorizationRuleCreateSerializer)
export interface CategorizationRuleCreate {
  company: number
  category: number
  name: string
  condition_type: ConditionType
  field_name: FieldName
  field_value: string
  priority?: number
  is_active?: boolean
}

// CategorizationRule update interface
export interface CategorizationRuleUpdate {
  category?: number
  name?: string
  condition_type?: ConditionType
  field_name?: FieldName
  field_value?: string
  priority?: number
  is_active?: boolean
}

// API Response types
export interface CategoriesResponse {
  count: number
  next: string | null
  previous: string | null
  results: Category[]
}

export interface CategorizationRulesResponse {
  count: number
  next: string | null
  previous: string | null
  results: CategorizationRule[]
}

// Filter and sort options
export interface CategoriesFilter {
  company?: number
  parent?: number | null
  is_active?: boolean
  is_system?: boolean
  search?: string
}

export interface CategorizationRulesFilter {
  company?: number
  category?: number
  is_active?: boolean
  search?: string
}

export type CategoriesSortField = 'name' | 'created_at' | 'updated_at'
export type CategorizationRulesSortField = 'name' | 'priority' | 'created_at' | 'updated_at'

// Display options for dropdowns/selects
export interface ConditionTypeOption {
  value: ConditionType
  label: string
}

export interface FieldNameOption {
  value: FieldName
  label: string
}

// Constants for dropdowns
export const CONDITION_TYPE_OPTIONS: ConditionTypeOption[] = [
  { value: 'CONTAINS', label: 'Contains' },
  { value: 'EQUALS', label: 'Equals' },
  { value: 'STARTS_WITH', label: 'Starts with' },
  { value: 'ENDS_WITH', label: 'Ends with' },
  { value: 'REGEX', label: 'Regular expression' },
  { value: 'GREATER_THAN', label: 'Greater than' },
  { value: 'LESS_THAN', label: 'Less than' },
  { value: 'GREATER_EQUAL', label: 'Greater than or equal' },
  { value: 'LESS_EQUAL', label: 'Less than or equal' }
]

export const FIELD_NAME_OPTIONS: FieldNameOption[] = [
  { value: 'description', label: 'Description' },
  { value: 'amount', label: 'Amount' },
  { value: 'transaction_type', label: 'Transaction Type' },
  { value: 'category', label: 'Category' }
]

// Utility types
export type CategoryTree = Category & {
  children?: CategoryTree[]
}

// Error types
export interface CategoryError {
  field: string
  message: string
}

export interface CategorizationRuleError {
  field: string
  message: string
}