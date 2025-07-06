/**
 * Banking Service
 * API client for banking operations, accounts, and transactions
 */

import { api } from './api'
import type {
  BankProvider,
  BankAccount,
  Transaction,
  BankAccountCreate,
  BankAccountUpdate,
  TransactionUpdate,
  BankProvidersResponse,
  BankAccountsResponse,
  TransactionsResponse,
  BankProvidersFilter,
  BankAccountsFilter,
  TransactionsFilter,
  ConnectBankRequest,
  SyncAccountsRequest,
  AccountSummary,
  TransactionSummary
} from '../types/banking'

class BankingService {
  private basePath = '/banking'

  // Bank Providers endpoints
  async getBankProviders(filters: BankProvidersFilter = {}): Promise<BankProvidersResponse> {
    const response = await api.get(`${this.basePath}/bank-providers/`, {
      params: filters
    })
    return response.data
  }

  async getBankProvider(id: number): Promise<BankProvider> {
    const response = await api.get(`${this.basePath}/bank-providers/${id}/`)
    return response.data
  }

  // Bank Accounts endpoints
  async getBankAccounts(filters: BankAccountsFilter = {}): Promise<BankAccountsResponse> {
    const response = await api.get(`${this.basePath}/bank-accounts/`, {
      params: filters
    })
    return response.data
  }

  async getBankAccount(id: number): Promise<BankAccount> {
    const response = await api.get(`${this.basePath}/bank-accounts/${id}/`)
    return response.data
  }

  async createBankAccount(data: BankAccountCreate): Promise<BankAccount> {
    const response = await api.post(`${this.basePath}/bank-accounts/`, data)
    return response.data
  }

  async updateBankAccount(id: number, data: BankAccountUpdate): Promise<BankAccount> {
    const response = await api.patch(`${this.basePath}/bank-accounts/${id}/`, data)
    return response.data
  }

  async deleteBankAccount(id: number): Promise<void> {
    await api.delete(`${this.basePath}/bank-accounts/${id}/`)
  }

  async syncBankAccount(id: number): Promise<{
    synced_transactions: number
    synced_at: string
  }> {
    const response = await api.post(`${this.basePath}/bank-accounts/${id}/sync/`)
    return response.data
  }

  // Transactions endpoints
  async getTransactions(filters: TransactionsFilter = {}): Promise<TransactionsResponse> {
    const response = await api.get(`${this.basePath}/transactions/`, {
      params: filters
    })
    return response.data
  }

  async getTransaction(id: number): Promise<Transaction> {
    const response = await api.get(`${this.basePath}/transactions/${id}/`)
    return response.data
  }

  async updateTransaction(id: number, data: TransactionUpdate): Promise<Transaction> {
    const response = await api.patch(`${this.basePath}/transactions/${id}/`, data)
    return response.data
  }

  // Pluggy Integration endpoints
  async connectBank(data: ConnectBankRequest): Promise<{
    item_id: string
    status: string
    accounts: BankAccount[]
  }> {
    const response = await api.post(`${this.basePath}/connect/`, data)
    return response.data
  }

  async syncAccounts(data: SyncAccountsRequest): Promise<{
    synced_accounts: number
    synced_transactions: number
    synced_at: string
  }> {
    const response = await api.post(`${this.basePath}/sync/`, data)
    return response.data
  }

  async getSyncStatus(itemId: string): Promise<{
    item_id: string
    status: string
    last_sync: string
    accounts_count: number
    transactions_count: number
  }> {
    const response = await api.get(`${this.basePath}/sync-status/${itemId}/`)
    return response.data
  }

  // Dashboard/Summary endpoints
  async getAccountSummary(companyId: number): Promise<AccountSummary> {
    const response = await api.get(`${this.basePath}/accounts-summary/`, {
      params: { company: companyId }
    })
    return response.data
  }

  async getTransactionSummary(
    companyId: number, 
    startDate: string, 
    endDate: string
  ): Promise<TransactionSummary> {
    const response = await api.get(`${this.basePath}/transactions-summary/`, {
      params: { 
        company: companyId,
        start_date: startDate,
        end_date: endDate
      }
    })
    return response.data
  }

  // Utility methods
  async getAccountsByProvider(companyId: number, providerId: number): Promise<BankAccount[]> {
    const response = await this.getBankAccounts({
      company: companyId,
      bank_provider: providerId,
      is_active: true
    })
    return response.results
  }

  async getTransactionsByAccount(
    accountId: number, 
    startDate?: string, 
    endDate?: string
  ): Promise<Transaction[]> {
    const filters: TransactionsFilter = {
      bank_account: accountId
    }
    
    if (startDate) filters.start_date = startDate
    if (endDate) filters.end_date = endDate

    const response = await this.getTransactions(filters)
    return response.results
  }

  async getTransactionsByCategory(
    companyId: number,
    category: string,
    startDate?: string,
    endDate?: string
  ): Promise<Transaction[]> {
    const filters: TransactionsFilter = {
      category
    }
    
    if (startDate) filters.start_date = startDate
    if (endDate) filters.end_date = endDate

    // Get all accounts for company first
    const accountsResponse = await this.getBankAccounts({
      company: companyId,
      is_active: true
    })

    // Get transactions for all accounts with category filter
    const allTransactions: Transaction[] = []
    
    for (const account of accountsResponse.results) {
      const transactionFilters = {
        ...filters,
        bank_account: account.id
      }
      
      const transactionsResponse = await this.getTransactions(transactionFilters)
      allTransactions.push(...transactionsResponse.results)
    }

    return allTransactions
  }

  // Bulk operations
  async bulkUpdateTransactions(
    transactionIds: number[],
    data: TransactionUpdate
  ): Promise<{ updated_count: number }> {
    const response = await api.patch(`${this.basePath}/transactions/bulk-update/`, {
      transaction_ids: transactionIds,
      ...data
    })
    return response.data
  }

  async categorizeTransactions(
    transactionIds: number[],
    categoryId: number
  ): Promise<{ categorized_count: number }> {
    const response = await api.post(`${this.basePath}/transactions/categorize/`, {
      transaction_ids: transactionIds,
      category_id: categoryId
    })
    return response.data
  }

  // Export operations
  async exportTransactions(
    filters: TransactionsFilter,
    format: 'csv' | 'excel' = 'csv'
  ): Promise<Blob> {
    const response = await api.get(`${this.basePath}/transactions/export/`, {
      params: { ...filters, format },
      responseType: 'blob'
    })
    return response.data
  }

  async exportAccountStatement(
    accountId: number,
    startDate: string,
    endDate: string,
    format: 'pdf' | 'csv' = 'pdf'
  ): Promise<Blob> {
    const response = await api.get(`${this.basePath}/bank-accounts/${accountId}/statement/`, {
      params: { start_date: startDate, end_date: endDate, format },
      responseType: 'blob'
    })
    return response.data
  }

  // Search and filtering helpers
  async searchTransactions(
    companyId: number,
    searchTerm: string,
    filters?: Partial<TransactionsFilter>
  ): Promise<Transaction[]> {
    // Get all accounts for company
    const accountsResponse = await this.getBankAccounts({
      company: companyId,
      is_active: true
    })

    const allTransactions: Transaction[] = []
    
    for (const account of accountsResponse.results) {
      const transactionFilters: TransactionsFilter = {
        bank_account: account.id,
        search: searchTerm,
        ...filters
      }
      
      const transactionsResponse = await this.getTransactions(transactionFilters)
      allTransactions.push(...transactionsResponse.results)
    }

    return allTransactions
  }

  // Error handling wrapper
  private async handleApiCall<T>(apiCall: () => Promise<T>): Promise<T> {
    try {
      return await apiCall()
    } catch (error) {
      console.error('Banking API Error:', error)
      throw error
    }
  }
}

// Export singleton instance
export const bankingService = new BankingService()
export default bankingService

// Named export for testing
export { BankingService }