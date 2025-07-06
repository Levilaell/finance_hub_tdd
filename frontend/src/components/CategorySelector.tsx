/**
 * CategorySelector Component
 * Dropdown selector for categories with search, filtering, and tree support
 */

import React, { useEffect, useState, useMemo } from 'react'
import { useCategories } from '../hooks/useCategories'
import type { Category, CategoriesFilter } from '../types/categories'

interface CategorySelectorProps {
  value: Category | null
  onChange: (category: Category | null) => void
  companyId: number
  
  // Display options
  label?: string
  placeholder?: string
  disabled?: boolean
  required?: boolean
  clearable?: boolean
  searchable?: boolean
  showColors?: boolean
  showFullPath?: boolean
  treeMode?: boolean
  
  // Filtering options
  parentId?: number | null
  showInactive?: boolean
  excludeSystem?: boolean
  
  // Form integration
  error?: string
  helpText?: string
  
  // Styling
  className?: string
}

interface CategoryOptionProps {
  category: Category
  showColors?: boolean
  showFullPath?: boolean
  isTree?: boolean
  level?: number
  onClick: () => void
}

const CategoryOption: React.FC<CategoryOptionProps> = ({
  category,
  showColors,
  showFullPath,
  isTree,
  level = 0,
  onClick
}) => {
  const displayName = showFullPath ? category.full_path : category.name
  const indentStyle = isTree ? { paddingLeft: `${level * 20}px` } : {}

  return (
    <div
      className="category-option"
      style={indentStyle}
      onClick={onClick}
      role="option"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onClick()}
    >
      {showColors && (
        <div
          className="category-color"
          data-testid={`category-color-${category.id}`}
          style={{
            backgroundColor: category.color,
            width: '12px',
            height: '12px',
            borderRadius: '50%',
            marginRight: '8px',
            display: 'inline-block'
          }}
        />
      )}
      <span>{displayName}</span>
      {!category.is_active && (
        <span className="inactive-label"> (Inativo)</span>
      )}
    </div>
  )
}

export const CategorySelector: React.FC<CategorySelectorProps> = ({
  value,
  onChange,
  companyId,
  label,
  placeholder = 'Selecione uma categoria',
  disabled = false,
  required = false,
  clearable = false,
  searchable = false,
  showColors = false,
  showFullPath = false,
  treeMode = false,
  parentId,
  showInactive = false,
  excludeSystem = false,
  error,
  helpText,
  className = ''
}) => {
  const {
    categories,
    categoryTree,
    categoriesLoading,
    categoriesError,
    fetchCategories,
    fetchCategoryTree,
    clearCategoriesError
  } = useCategories()

  const [isOpen, setIsOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [localError, setLocalError] = useState<string | null>(null)

  // Build filters based on props
  const filters = useMemo((): CategoriesFilter => {
    const baseFilters: CategoriesFilter = {
      company: companyId
    }

    if (!showInactive) {
      baseFilters.is_active = true
    }

    if (excludeSystem) {
      baseFilters.is_system = false
    }

    if (parentId !== undefined) {
      baseFilters.parent = parentId
    }

    return baseFilters
  }, [companyId, showInactive, excludeSystem, parentId])

  // Fetch data on mount and when filters change
  useEffect(() => {
    if (treeMode) {
      fetchCategoryTree(companyId)
    } else {
      fetchCategories(filters)
    }
  }, [treeMode, companyId, filters, fetchCategories, fetchCategoryTree])

  // Clear errors when they change
  useEffect(() => {
    if (categoriesError) {
      setLocalError(categoriesError)
    } else {
      setLocalError(null)
    }
  }, [categoriesError])

  // Get categories to display
  const categoriesToDisplay = treeMode ? categoryTree : categories

  // Filter categories based on search term
  const filteredCategories = useMemo(() => {
    if (!searchTerm) return categoriesToDisplay

    return categoriesToDisplay.filter(category => {
      const searchText = showFullPath ? category.full_path : category.name
      return searchText.toLowerCase().includes(searchTerm.toLowerCase())
    })
  }, [categoriesToDisplay, searchTerm, showFullPath])

  // Handle category selection
  const handleCategorySelect = (category: Category) => {
    onChange(category)
    setIsOpen(false)
    setSearchTerm('')
  }

  // Handle clear selection
  const handleClear = () => {
    onChange(null)
    setSearchTerm('')
  }

  // Handle retry on error
  const handleRetry = () => {
    clearCategoriesError()
    if (treeMode) {
      fetchCategoryTree(companyId)
    } else {
      fetchCategories(filters)
    }
  }

  // Render loading state
  if (categoriesLoading) {
    return (
      <div className={`category-selector loading ${className}`}>
        {label && (
          <label>
            {label} {required && '*'}
          </label>
        )}
        <div className="loading-placeholder">
          Carregando categorias...
        </div>
      </div>
    )
  }

  // Render error state
  if (localError) {
    return (
      <div className={`category-selector error ${className}`}>
        {label && (
          <label>
            {label} {required && '*'}
          </label>
        )}
        <div className="error-state">
          <div className="error-message">{localError}</div>
          <button 
            type="button" 
            onClick={handleRetry}
            className="retry-button"
          >
            Tentar novamente
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className={`category-selector ${className}`}>
      {label && (
        <label>
          {label} {required && '*'}
        </label>
      )}
      
      <div className="selector-container">
        <div className="input-wrapper">
          <input
            type="text"
            role="combobox"
            aria-expanded={isOpen}
            aria-haspopup="listbox"
            placeholder={value ? value.name : placeholder}
            value={searchable && isOpen ? searchTerm : (value?.name || '')}
            disabled={disabled}
            readOnly={!searchable}
            onClick={() => !disabled && setIsOpen(!isOpen)}
            onChange={(e) => {
              if (searchable) {
                setSearchTerm(e.target.value)
                setIsOpen(true) // Keep dropdown open when typing
              }
            }}
            onFocus={() => !disabled && setIsOpen(true)}
            className={error ? 'error' : ''}
          />
          
          {clearable && value && (
            <button
              type="button"
              className="clear-button"
              onClick={handleClear}
              disabled={disabled}
              aria-label="Limpar seleção"
            >
              ×
            </button>
          )}
        </div>

        {isOpen && (
          <div className="dropdown" role="listbox">
            {filteredCategories.length === 0 ? (
              <div className="no-options">
                {searchTerm ? 'Nenhuma categoria encontrada' : 'Nenhuma categoria disponível'}
              </div>
            ) : (
              filteredCategories.map((category) => (
                <CategoryOption
                  key={category.id}
                  category={category}
                  showColors={showColors}
                  showFullPath={showFullPath}
                  isTree={treeMode}
                  onClick={() => handleCategorySelect(category)}
                />
              ))
            )}
          </div>
        )}
      </div>

      {error && (
        <div className="error-message" role="alert">
          {error}
        </div>
      )}

      {helpText && (
        <div className="help-text">
          {helpText}
        </div>
      )}
    </div>
  )
}

export default CategorySelector