/**
 * Banking Store
 * State management for banking operations using Zustand
 */

import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { bankingService } from '../services/banking'
import type {
  BankProvider,
  BankAccount,
  Transaction,
  BankAccountCreate,
  BankAccountUpdate,
  TransactionUpdate,
  BankProvidersFilter,
  BankAccountsFilter,
  TransactionsFilter,
  ConnectBankRequest,
  SyncAccountsRequest,
  AccountSummary,
  TransactionSummary
} from '../types/banking'

interface Pagination {
  count: number
  page: number
  pageSize: number
  totalPages: number
}

interface BankingState {
  // Bank Providers state
  bankProviders: BankProvider[]
  currentBankProvider: BankProvider | null
  bankProvidersLoading: boolean
  bankProvidersError: string | null

  // Bank Accounts state
  bankAccounts: BankAccount[]
  currentBankAccount: BankAccount | null
  bankAccountsLoading: boolean
  bankAccountsError: string | null
  bankAccountsFilters: BankAccountsFilter
  bankAccountsPagination: Pagination

  // Transactions state
  transactions: Transaction[]
  currentTransaction: Transaction | null
  transactionsLoading: boolean
  transactionsError: string | null
  transactionsFilters: TransactionsFilter
  transactionsPagination: Pagination

  // Summary state
  accountSummary: AccountSummary | null
  transactionSummary: TransactionSummary | null
  summaryLoading: boolean
  summaryError: string | null

  // Sync state
  syncStatus: {
    item_id: string
    status: string
    last_sync: string
    accounts_count: number
    transactions_count: number
  } | null
  syncLoading: boolean
  syncError: string | null

  // Bank Providers actions
  fetchBankProviders: (filters?: BankProvidersFilter) => Promise<void>
  fetchBankProvider: (id: number) => Promise<void>
  setBankProviders: (providers: BankProvider[]) => void
  setCurrentBankProvider: (provider: BankProvider | null) => void
  setBankProvidersLoading: (loading: boolean) => void
  setBankProvidersError: (error: string | null) => void
  clearBankProvidersError: () => void

  // Bank Accounts actions
  fetchBankAccounts: (filters?: BankAccountsFilter) => Promise<void>
  fetchBankAccount: (id: number) => Promise<void>
  createBankAccount: (data: BankAccountCreate) => Promise<BankAccount>
  updateBankAccount: (id: number, data: BankAccountUpdate) => Promise<BankAccount>
  deleteBankAccount: (id: number) => Promise<void>
  syncBankAccount: (id: number) => Promise<{ synced_transactions: number; synced_at: string }>
  setBankAccounts: (accounts: BankAccount[]) => void
  setCurrentBankAccount: (account: BankAccount | null) => void
  setBankAccountsLoading: (loading: boolean) => void
  setBankAccountsError: (error: string | null) => void
  clearBankAccountsError: () => void
  setBankAccountsFilters: (filters: BankAccountsFilter) => void

  // Transactions actions
  fetchTransactions: (filters?: TransactionsFilter) => Promise<void>
  fetchTransaction: (id: number) => Promise<void>
  updateTransaction: (id: number, data: TransactionUpdate) => Promise<Transaction>
  setTransactions: (transactions: Transaction[]) => void
  setCurrentTransaction: (transaction: Transaction | null) => void
  setTransactionsLoading: (loading: boolean) => void
  setTransactionsError: (error: string | null) => void
  clearTransactionsError: () => void
  setTransactionsFilters: (filters: TransactionsFilter) => void

  // Pluggy Integration actions
  connectBank: (data: ConnectBankRequest) => Promise<{ item_id: string; status: string; accounts: BankAccount[] }>
  syncAccounts: (data: SyncAccountsRequest) => Promise<{ synced_accounts: number; synced_transactions: number; synced_at: string }>
  getSyncStatus: (itemId: string) => Promise<void>
  setSyncLoading: (loading: boolean) => void
  setSyncError: (error: string | null) => void
  clearSyncError: () => void

  // Summary actions
  fetchAccountSummary: (companyId: number) => Promise<void>
  fetchTransactionSummary: (companyId: number, startDate: string, endDate: string) => Promise<void>
  setSummaryLoading: (loading: boolean) => void
  setSummaryError: (error: string | null) => void
  clearSummaryError: () => void

  // Utility actions
  resetState: () => void
}

const initialPagination: Pagination = {
  count: 0,
  page: 1,
  pageSize: 20,
  totalPages: 0
}

export const useBankingStore = create<BankingState>()(
  devtools(
    (set, get) => ({
      // Initial state
      bankProviders: [],
      currentBankProvider: null,
      bankProvidersLoading: false,
      bankProvidersError: null,

      bankAccounts: [],
      currentBankAccount: null,
      bankAccountsLoading: false,
      bankAccountsError: null,
      bankAccountsFilters: {},
      bankAccountsPagination: initialPagination,

      transactions: [],
      currentTransaction: null,
      transactionsLoading: false,
      transactionsError: null,
      transactionsFilters: {},
      transactionsPagination: initialPagination,

      accountSummary: null,
      transactionSummary: null,
      summaryLoading: false,
      summaryError: null,

      syncStatus: null,
      syncLoading: false,
      syncError: null,

      // Bank Providers actions
      fetchBankProviders: async (filters = {}) => {
        set({ bankProvidersLoading: true, bankProvidersError: null })
        
        try {
          const response = await bankingService.getBankProviders(filters)
          set({
            bankProviders: response.results,
            bankProvidersLoading: false
          })
        } catch (error) {
          set({
            bankProvidersError: error instanceof Error ? error.message : 'Unknown error',
            bankProvidersLoading: false
          })
        }
      },

      fetchBankProvider: async (id: number) => {
        try {
          const provider = await bankingService.getBankProvider(id)
          set({ currentBankProvider: provider })
        } catch (error) {
          set({
            bankProvidersError: error instanceof Error ? error.message : 'Unknown error'
          })
        }
      },

      setBankProviders: (providers: BankProvider[]) => set({ bankProviders: providers }),
      setCurrentBankProvider: (provider: BankProvider | null) => set({ currentBankProvider: provider }),
      setBankProvidersLoading: (loading: boolean) => set({ bankProvidersLoading: loading }),
      setBankProvidersError: (error: string | null) => set({ bankProvidersError: error }),
      clearBankProvidersError: () => set({ bankProvidersError: null }),

      // Bank Accounts actions
      fetchBankAccounts: async (filters = {}) => {
        set({ bankAccountsLoading: true, bankAccountsError: null })
        
        try {
          const response = await bankingService.getBankAccounts(filters)
          
          set({
            bankAccounts: response.results,
            bankAccountsPagination: {
              count: response.count,
              page: filters.page || 1,
              pageSize: 20,
              totalPages: Math.ceil(response.count / 20)
            },
            bankAccountsFilters: filters,
            bankAccountsLoading: false
          })
        } catch (error) {
          set({
            bankAccountsError: error instanceof Error ? error.message : 'Unknown error',
            bankAccountsLoading: false
          })
        }
      },

      fetchBankAccount: async (id: number) => {
        try {
          const account = await bankingService.getBankAccount(id)
          set({ currentBankAccount: account })
        } catch (error) {
          set({
            bankAccountsError: error instanceof Error ? error.message : 'Unknown error'
          })
        }
      },

      createBankAccount: async (data: BankAccountCreate) => {
        try {
          const newAccount = await bankingService.createBankAccount(data)
          
          set(state => ({
            bankAccounts: [...state.bankAccounts, newAccount]
          }))
          
          return newAccount
        } catch (error) {
          set({
            bankAccountsError: error instanceof Error ? error.message : 'Unknown error'
          })
          throw error
        }
      },

      updateBankAccount: async (id: number, data: BankAccountUpdate) => {
        try {
          const updatedAccount = await bankingService.updateBankAccount(id, data)
          
          set(state => ({
            bankAccounts: state.bankAccounts.map(account => 
              account.id === id ? updatedAccount : account
            ),
            currentBankAccount: state.currentBankAccount?.id === id ? updatedAccount : state.currentBankAccount
          }))
          
          return updatedAccount
        } catch (error) {
          set({
            bankAccountsError: error instanceof Error ? error.message : 'Unknown error'
          })
          throw error
        }
      },

      deleteBankAccount: async (id: number) => {
        try {
          await bankingService.deleteBankAccount(id)
          
          set(state => ({
            bankAccounts: state.bankAccounts.filter(account => account.id !== id),
            currentBankAccount: state.currentBankAccount?.id === id ? null : state.currentBankAccount
          }))
        } catch (error) {
          set({
            bankAccountsError: error instanceof Error ? error.message : 'Unknown error'
          })
          throw error
        }
      },

      syncBankAccount: async (id: number) => {
        try {
          const result = await bankingService.syncBankAccount(id)
          
          // Update the account's last_sync timestamp
          set(state => ({
            bankAccounts: state.bankAccounts.map(account => 
              account.id === id ? { ...account, last_sync: result.synced_at } : account
            )
          }))
          
          return result
        } catch (error) {
          set({
            bankAccountsError: error instanceof Error ? error.message : 'Unknown error'
          })
          throw error
        }
      },

      setBankAccounts: (accounts: BankAccount[]) => set({ bankAccounts: accounts }),
      setCurrentBankAccount: (account: BankAccount | null) => set({ currentBankAccount: account }),
      setBankAccountsLoading: (loading: boolean) => set({ bankAccountsLoading: loading }),
      setBankAccountsError: (error: string | null) => set({ bankAccountsError: error }),
      clearBankAccountsError: () => set({ bankAccountsError: null }),
      setBankAccountsFilters: (filters: BankAccountsFilter) => set({ bankAccountsFilters: filters }),

      // Transactions actions
      fetchTransactions: async (filters = {}) => {
        set({ transactionsLoading: true, transactionsError: null })
        
        try {
          const response = await bankingService.getTransactions(filters)
          
          set({
            transactions: response.results,
            transactionsPagination: {
              count: response.count,
              page: filters.page || 1,
              pageSize: 20,
              totalPages: Math.ceil(response.count / 20)
            },
            transactionsFilters: filters,
            transactionsLoading: false
          })
        } catch (error) {
          set({
            transactionsError: error instanceof Error ? error.message : 'Unknown error',
            transactionsLoading: false
          })
        }
      },

      fetchTransaction: async (id: number) => {
        try {
          const transaction = await bankingService.getTransaction(id)
          set({ currentTransaction: transaction })
        } catch (error) {
          set({
            transactionsError: error instanceof Error ? error.message : 'Unknown error'
          })
        }
      },

      updateTransaction: async (id: number, data: TransactionUpdate) => {
        try {
          const updatedTransaction = await bankingService.updateTransaction(id, data)
          
          set(state => ({
            transactions: state.transactions.map(transaction => 
              transaction.id === id ? updatedTransaction : transaction
            ),
            currentTransaction: state.currentTransaction?.id === id ? updatedTransaction : state.currentTransaction
          }))
          
          return updatedTransaction
        } catch (error) {
          set({
            transactionsError: error instanceof Error ? error.message : 'Unknown error'
          })
          throw error
        }
      },

      setTransactions: (transactions: Transaction[]) => set({ transactions }),
      setCurrentTransaction: (transaction: Transaction | null) => set({ currentTransaction: transaction }),
      setTransactionsLoading: (loading: boolean) => set({ transactionsLoading: loading }),
      setTransactionsError: (error: string | null) => set({ transactionsError: error }),
      clearTransactionsError: () => set({ transactionsError: null }),
      setTransactionsFilters: (filters: TransactionsFilter) => set({ transactionsFilters: filters }),

      // Pluggy Integration actions
      connectBank: async (data: ConnectBankRequest) => {
        set({ syncLoading: true, syncError: null })
        
        try {
          const result = await bankingService.connectBank(data)
          
          // Add new accounts to the store
          set(state => ({
            bankAccounts: [...state.bankAccounts, ...result.accounts],
            syncLoading: false
          }))
          
          return result
        } catch (error) {
          set({
            syncError: error instanceof Error ? error.message : 'Unknown error',
            syncLoading: false
          })
          throw error
        }
      },

      syncAccounts: async (data: SyncAccountsRequest) => {
        set({ syncLoading: true, syncError: null })
        
        try {
          const result = await bankingService.syncAccounts(data)
          set({ syncLoading: false })
          return result
        } catch (error) {
          set({
            syncError: error instanceof Error ? error.message : 'Unknown error',
            syncLoading: false
          })
          throw error
        }
      },

      getSyncStatus: async (itemId: string) => {
        try {
          const status = await bankingService.getSyncStatus(itemId)
          set({ syncStatus: status })
        } catch (error) {
          set({
            syncError: error instanceof Error ? error.message : 'Unknown error'
          })
        }
      },

      setSyncLoading: (loading: boolean) => set({ syncLoading: loading }),
      setSyncError: (error: string | null) => set({ syncError: error }),
      clearSyncError: () => set({ syncError: null }),

      // Summary actions
      fetchAccountSummary: async (companyId: number) => {
        set({ summaryLoading: true, summaryError: null })
        
        try {
          const summary = await bankingService.getAccountSummary(companyId)
          set({ accountSummary: summary, summaryLoading: false })
        } catch (error) {
          set({
            summaryError: error instanceof Error ? error.message : 'Unknown error',
            summaryLoading: false
          })
        }
      },

      fetchTransactionSummary: async (companyId: number, startDate: string, endDate: string) => {
        set({ summaryLoading: true, summaryError: null })
        
        try {
          const summary = await bankingService.getTransactionSummary(companyId, startDate, endDate)
          set({ transactionSummary: summary, summaryLoading: false })
        } catch (error) {
          set({
            summaryError: error instanceof Error ? error.message : 'Unknown error',
            summaryLoading: false
          })
        }
      },

      setSummaryLoading: (loading: boolean) => set({ summaryLoading: loading }),
      setSummaryError: (error: string | null) => set({ summaryError: error }),
      clearSummaryError: () => set({ summaryError: null }),

      // Utility actions
      resetState: () => set({
        bankProviders: [],
        currentBankProvider: null,
        bankProvidersLoading: false,
        bankProvidersError: null,
        bankAccounts: [],
        currentBankAccount: null,
        bankAccountsLoading: false,
        bankAccountsError: null,
        bankAccountsFilters: {},
        bankAccountsPagination: initialPagination,
        transactions: [],
        currentTransaction: null,
        transactionsLoading: false,
        transactionsError: null,
        transactionsFilters: {},
        transactionsPagination: initialPagination,
        accountSummary: null,
        transactionSummary: null,
        summaryLoading: false,
        summaryError: null,
        syncStatus: null,
        syncLoading: false,
        syncError: null
      })
    }),
    {
      name: 'banking-store'
    }
  )
)

// Export selectors for easier usage
export const useBankingSelectors = () => {
  const store = useBankingStore()
  
  return {
    // Bank Providers selectors
    bankProviders: store.bankProviders,
    currentBankProvider: store.currentBankProvider,
    bankProvidersLoading: store.bankProvidersLoading,
    bankProvidersError: store.bankProvidersError,
    
    // Bank Accounts selectors
    bankAccounts: store.bankAccounts,
    currentBankAccount: store.currentBankAccount,
    bankAccountsLoading: store.bankAccountsLoading,
    bankAccountsError: store.bankAccountsError,
    bankAccountsFilters: store.bankAccountsFilters,
    bankAccountsPagination: store.bankAccountsPagination,
    
    // Transactions selectors
    transactions: store.transactions,
    currentTransaction: store.currentTransaction,
    transactionsLoading: store.transactionsLoading,
    transactionsError: store.transactionsError,
    transactionsFilters: store.transactionsFilters,
    transactionsPagination: store.transactionsPagination,
    
    // Summary selectors
    accountSummary: store.accountSummary,
    transactionSummary: store.transactionSummary,
    summaryLoading: store.summaryLoading,
    summaryError: store.summaryError,
    
    // Sync selectors
    syncStatus: store.syncStatus,
    syncLoading: store.syncLoading,
    syncError: store.syncError,
    
    // Computed selectors
    activeBankAccountsCount: store.bankAccounts.filter(account => account.is_active).length,
    totalBalance: store.bankAccounts.reduce((sum, account) => sum + account.balance, 0),
    pendingTransactionsCount: store.transactions.filter(transaction => transaction.is_pending).length,
    hasConnectedAccounts: store.bankAccounts.length > 0
  }
}

export default useBankingStore