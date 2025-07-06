/**
 * AccountSelector Component
 * Dropdown selector for bank accounts with filtering, search, and multiple selection
 */

import React, { useState, useEffect, useMemo, useCallback } from 'react'
import { ChevronDownIcon, CheckIcon, ExclamationTriangleIcon, ArrowPathIcon } from '@heroicons/react/24/outline'
import { useBanking, useBankingHelpers } from '../hooks/useBanking'
import type { BankAccount, BankAccountsFilter } from '../types/banking'

interface AccountSelectorProps {
  companyId: number
  value?: number | number[]
  onChange?: (value: number | number[], accounts: BankAccount | BankAccount[]) => void
  onBlur?: () => void
  onFocus?: () => void
  placeholder?: string
  multiple?: boolean
  searchable?: boolean
  accountTypes?: string[]
  showInactive?: boolean
  filters?: Partial<BankAccountsFilter>
  disabled?: boolean
  error?: string
  register?: any
  className?: string
}

export const AccountSelector: React.FC<AccountSelectorProps> = ({
  companyId,
  value,
  onChange,
  onBlur,
  onFocus,
  placeholder = 'Selecione uma conta',
  multiple = false,
  searchable = false,
  accountTypes,
  showInactive = false,
  filters = {},
  disabled = false,
  error,
  register,
  className = ''
}) => {
  const [isOpen, setIsOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')

  const {
    bankAccounts,
    bankAccountsLoading,
    bankAccountsError,
    fetchBankAccounts,
    clearBankAccountsError
  } = useBanking()

  const { getBankAccountById, getActiveAccounts } = useBankingHelpers()

  // Fetch accounts on mount and when companyId or filters change
  useEffect(() => {
    const fetchFilters: BankAccountsFilter = {
      company: companyId,
      is_active: !showInactive,
      ...filters
    }

    fetchBankAccounts(fetchFilters)
  }, [companyId, showInactive, filters, fetchBankAccounts])

  // Filter accounts based on criteria
  const filteredAccounts = useMemo(() => {
    let accounts = showInactive ? bankAccounts : getActiveAccounts()

    // Filter by account types
    if (accountTypes && accountTypes.length > 0) {
      accounts = accounts.filter(account => accountTypes.includes(account.account_type))
    }

    // Filter by search term
    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase()
      accounts = accounts.filter(account => 
        account.name.toLowerCase().includes(term) ||
        account.account_number.toLowerCase().includes(term) ||
        account.agency.toLowerCase().includes(term) ||
        account.bank_provider.name.toLowerCase().includes(term)
      )
    }

    return accounts
  }, [bankAccounts, getActiveAccounts, showInactive, accountTypes, searchTerm])

  // Get selected account(s)
  const selectedAccounts = useMemo(() => {
    if (!value) return multiple ? [] : null

    if (multiple && Array.isArray(value)) {
      return value.map(id => getBankAccountById(id)).filter(Boolean) as BankAccount[]
    }

    if (!multiple && typeof value === 'number') {
      return getBankAccountById(value) || null
    }

    return multiple ? [] : null
  }, [value, multiple, getBankAccountById])

  // Handle account selection
  const handleAccountSelect = useCallback((account: BankAccount) => {
    if (multiple) {
      const currentValues = Array.isArray(value) ? value : []
      const currentAccounts = Array.isArray(selectedAccounts) ? selectedAccounts : []

      if (currentValues.includes(account.id)) {
        // Remove from selection
        const newValues = currentValues.filter(id => id !== account.id)
        const newAccounts = currentAccounts.filter(acc => acc.id !== account.id)
        onChange?.(newValues, newAccounts)
      } else {
        // Add to selection
        const newValues = [...currentValues, account.id]
        const newAccounts = [...currentAccounts, account]
        onChange?.(newValues, newAccounts)
      }
    } else {
      onChange?.(account.id, account)
      setIsOpen(false)
    }
  }, [multiple, value, selectedAccounts, onChange])

  // Handle retry on error
  const handleRetry = useCallback(() => {
    clearBankAccountsError()
    const fetchFilters: BankAccountsFilter = {
      company: companyId,
      is_active: !showInactive,
      ...filters
    }
    fetchBankAccounts(fetchFilters)
  }, [clearBankAccountsError, companyId, showInactive, filters, fetchBankAccounts])

  // Format balance
  const formatBalance = (balance: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(balance)
  }

  // Get display text for button
  const getDisplayText = () => {
    if (multiple && Array.isArray(selectedAccounts)) {
      if (selectedAccounts.length === 0) return placeholder
      return `${selectedAccounts.length} contas selecionadas`
    }

    if (!multiple && selectedAccounts) {
      return (selectedAccounts as BankAccount).name
    }

    return placeholder
  }

  // Check if we have a selected account to show its name
  const hasSelectedAccount = () => {
    if (multiple && Array.isArray(selectedAccounts)) {
      return selectedAccounts.length > 0
    }
    return selectedAccounts !== null
  }

  // Handle keyboard navigation
  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      setIsOpen(!isOpen)
    } else if (event.key === 'Escape') {
      setIsOpen(false)
    } else if (isOpen && (event.key === 'ArrowDown' || event.key === 'ArrowUp')) {
      // Basic keyboard navigation - could be enhanced
      event.preventDefault()
    }
  }

  // Render loading state
  if (bankAccountsLoading) {
    return (
      <div className={`w-full ${className}`}>
        <button
          type="button"
          disabled
          className="w-full px-3 py-2 text-left bg-gray-50 border border-gray-300 rounded-md text-gray-500"
        >
          Carregando contas...
        </button>
      </div>
    )
  }

  // Render error state
  if (bankAccountsError) {
    return (
      <div className={`w-full ${className}`}>
        <div className="w-full px-3 py-2 text-left bg-red-50 border border-red-300 rounded-md text-red-700 text-sm">
          <div className="flex items-center space-x-2">
            <ExclamationTriangleIcon className="h-4 w-4" />
            <span>Erro ao carregar contas</span>
          </div>
          <button
            type="button"
            onClick={handleRetry}
            className="mt-2 inline-flex items-center space-x-1 text-red-600 hover:text-red-800"
          >
            <ArrowPathIcon className="h-3 w-3" />
            <span>Tentar novamente</span>
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className={`relative w-full ${className}`}>
      {/* Main button */}
      <button
        type="button"
        disabled={disabled}
        onClick={() => setIsOpen(!isOpen)}
        onFocus={onFocus}
        onBlur={onBlur}
        onKeyDown={handleKeyDown}
        aria-expanded={isOpen}
        aria-haspopup="listbox"
        className={`
          w-full px-3 py-2 text-left bg-white border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
          ${disabled ? 'bg-gray-50 text-gray-500' : 'text-gray-900'}
          ${error ? 'border-red-300' : 'border-gray-300'}
        `}
      >
        <div className="flex items-center justify-between">
          <span className={hasSelectedAccount() ? 'text-gray-900' : 'text-gray-500'}>
            {getDisplayText()}
          </span>
          <ChevronDownIcon 
            className={`h-4 w-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} 
          />
        </div>
      </button>

      {/* Error message */}
      {error && (
        <p className="mt-1 text-sm text-red-600">{error}</p>
      )}

      {/* Dropdown */}
      {isOpen && (
        <div 
          className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto"
          role="listbox"
        >
          {/* Search input */}
          {searchable && (
            <div className="p-2 border-b border-gray-200">
              <input
                type="text"
                placeholder="Buscar contas..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                onClick={(e) => e.stopPropagation()}
              />
            </div>
          )}

          {/* Account list */}
          {filteredAccounts.length === 0 ? (
            <div className="px-3 py-2 text-sm text-gray-500">
              Nenhuma conta encontrada
            </div>
          ) : (
            filteredAccounts.map((account) => {
              const isSelected = multiple 
                ? Array.isArray(value) && value.includes(account.id)
                : value === account.id

              return (
                <div
                  key={account.id}
                  onClick={() => handleAccountSelect(account)}
                  className={`
                    px-3 py-2 cursor-pointer hover:bg-gray-50 border-b border-gray-100 last:border-b-0
                    ${isSelected ? 'bg-blue-50' : ''}
                  `}
                  role="option"
                  aria-selected={isSelected}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {account.name}
                        </p>
                        <span className={`
                          px-2 py-1 text-xs rounded-full
                          ${account.account_type === 'CHECKING' ? 'bg-blue-100 text-blue-800' : ''}
                          ${account.account_type === 'SAVINGS' ? 'bg-green-100 text-green-800' : ''}
                          ${account.account_type === 'CREDIT_CARD' ? 'bg-purple-100 text-purple-800' : ''}
                        `}>
                          {account.account_type}
                        </span>
                      </div>
                      <p className="text-xs text-gray-500">
                        {account.bank_provider.code} - Ag: {account.agency} CC: {account.account_number}
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-gray-900">
                        {formatBalance(account.balance)}
                      </span>
                      {isSelected && multiple && (
                        <CheckIcon className="h-4 w-4 text-blue-600" />
                      )}
                    </div>
                  </div>
                  {!account.is_active && (
                    <p className="text-xs text-red-500 mt-1">Conta inativa</p>
                  )}
                </div>
              )
            })
          )}
        </div>
      )}

      {/* Hidden input for form libraries */}
      {register && (
        <input
          type="hidden"
          {...register}
          value={multiple && Array.isArray(value) ? value.join(',') : value || ''}
        />
      )}
    </div>
  )
}

export default AccountSelector