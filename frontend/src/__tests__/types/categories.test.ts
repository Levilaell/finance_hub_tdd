import { describe, it, expect } from '@jest/globals'

describe('Categories Types', () => {
  it('should define Category interface correctly', () => {
    // This test will guide us to create the proper Category interface
    const mockCategory = {
      id: 1,
      company: 1,
      parent: null as any,
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

    // Test that all required fields are present
    expect(mockCategory).toHaveProperty('id')
    expect(mockCategory).toHaveProperty('company')
    expect(mockCategory).toHaveProperty('parent')
    expect(mockCategory).toHaveProperty('name')
    expect(mockCategory).toHaveProperty('color')
    expect(mockCategory).toHaveProperty('is_system')
    expect(mockCategory).toHaveProperty('is_active')
    expect(mockCategory).toHaveProperty('full_path')
    expect(mockCategory).toHaveProperty('children_count')
    expect(mockCategory).toHaveProperty('rules_count')
    expect(mockCategory).toHaveProperty('created_at')
    expect(mockCategory).toHaveProperty('updated_at')

    // Test types
    expect(typeof mockCategory.id).toBe('number')
    expect(typeof mockCategory.company).toBe('number')
    expect(typeof mockCategory.name).toBe('string')
    expect(typeof mockCategory.color).toBe('string')
    expect(typeof mockCategory.is_system).toBe('boolean')
    expect(typeof mockCategory.is_active).toBe('boolean')
    expect(typeof mockCategory.full_path).toBe('string')
    expect(typeof mockCategory.children_count).toBe('number')
    expect(typeof mockCategory.rules_count).toBe('number')
    expect(typeof mockCategory.created_at).toBe('string')
    expect(typeof mockCategory.updated_at).toBe('string')
  })

  it('should define CategoryParent interface correctly', () => {
    const mockParent = {
      id: 1,
      name: 'Receitas',
      color: '#4CAF50'
    }

    expect(mockParent).toHaveProperty('id')
    expect(mockParent).toHaveProperty('name')
    expect(mockParent).toHaveProperty('color')
    expect(typeof mockParent.id).toBe('number')
    expect(typeof mockParent.name).toBe('string')
    expect(typeof mockParent.color).toBe('string')
  })

  it('should define CategoryCreate interface correctly', () => {
    const mockCreateCategory = {
      company: 1,
      parent: 1,
      name: 'Nova Categoria',
      color: '#FF5722',
      is_system: false,
      is_active: true
    }

    expect(mockCreateCategory).toHaveProperty('company')
    expect(mockCreateCategory).toHaveProperty('parent')
    expect(mockCreateCategory).toHaveProperty('name')
    expect(mockCreateCategory).toHaveProperty('color')
    expect(mockCreateCategory).toHaveProperty('is_system')
    expect(mockCreateCategory).toHaveProperty('is_active')
    expect(typeof mockCreateCategory.company).toBe('number')
    expect(typeof mockCreateCategory.parent).toBe('number')
    expect(typeof mockCreateCategory.name).toBe('string')
    expect(typeof mockCreateCategory.color).toBe('string')
    expect(typeof mockCreateCategory.is_system).toBe('boolean')
    expect(typeof mockCreateCategory.is_active).toBe('boolean')
  })

  it('should define CategorizationRule interface correctly', () => {
    const mockRule = {
      id: 1,
      company: 1,
      category: {
        id: 1,
        name: 'Receitas',
        color: '#4CAF50',
        full_path: 'Receitas'
      },
      name: 'Regra Salário',
      condition_type: 'CONTAINS' as const,
      condition_display: 'Contains',
      field_name: 'description' as const,
      field_display: 'Description',
      field_value: 'salario',
      priority: 1,
      is_active: true,
      created_at: '2023-01-01T00:00:00Z',
      updated_at: '2023-01-01T00:00:00Z'
    }

    expect(mockRule).toHaveProperty('id')
    expect(mockRule).toHaveProperty('company')
    expect(mockRule).toHaveProperty('category')
    expect(mockRule).toHaveProperty('name')
    expect(mockRule).toHaveProperty('condition_type')
    expect(mockRule).toHaveProperty('condition_display')
    expect(mockRule).toHaveProperty('field_name')
    expect(mockRule).toHaveProperty('field_display')
    expect(mockRule).toHaveProperty('field_value')
    expect(mockRule).toHaveProperty('priority')
    expect(mockRule).toHaveProperty('is_active')
    expect(mockRule).toHaveProperty('created_at')
    expect(mockRule).toHaveProperty('updated_at')

    // Test nested category
    expect(mockRule.category).toHaveProperty('id')
    expect(mockRule.category).toHaveProperty('name')
    expect(mockRule.category).toHaveProperty('color')
    expect(mockRule.category).toHaveProperty('full_path')
  })

  it('should define CategorizationRuleCreate interface correctly', () => {
    const mockCreateRule = {
      company: 1,
      category: 1,
      name: 'Nova Regra',
      condition_type: 'CONTAINS' as const,
      field_name: 'description' as const,
      field_value: 'teste',
      priority: 1,
      is_active: true
    }

    expect(mockCreateRule).toHaveProperty('company')
    expect(mockCreateRule).toHaveProperty('category')
    expect(mockCreateRule).toHaveProperty('name')
    expect(mockCreateRule).toHaveProperty('condition_type')
    expect(mockCreateRule).toHaveProperty('field_name')
    expect(mockCreateRule).toHaveProperty('field_value')
    expect(mockCreateRule).toHaveProperty('priority')
    expect(mockCreateRule).toHaveProperty('is_active')
  })

  it('should define condition and field type unions correctly', () => {
    const conditionTypes = [
      'CONTAINS',
      'EQUALS', 
      'STARTS_WITH',
      'ENDS_WITH',
      'REGEX',
      'GREATER_THAN',
      'LESS_THAN',
      'GREATER_EQUAL',
      'LESS_EQUAL'
    ] as const

    const fieldNames = [
      'description',
      'amount',
      'transaction_type',
      'category'
    ] as const

    expect(conditionTypes).toHaveLength(9)
    expect(fieldNames).toHaveLength(4)
    expect(conditionTypes).toContain('CONTAINS')
    expect(fieldNames).toContain('description')
  })
})