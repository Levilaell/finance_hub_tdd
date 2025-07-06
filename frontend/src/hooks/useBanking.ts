/**
 * useBanking Hook
 * Custom hook for banking operations, wrapping the banking store
 */

import { useCallback } from 'react'
import { useBankingStore, useBankingSelectors } from '../store/banking'
import type {
  BankAccountCreate,
  BankAccountUpdate,
  TransactionUpdate,
  BankProvidersFilter,
  BankAccountsFilter,
  TransactionsFilter,
  ConnectBankRequest,
  SyncAccountsRequest,
  BankProvider,
  BankAccount,
  Transaction
} from '../types/banking'

export const useBanking = () => {
  const store = useBankingStore()
  const selectors = useBankingSelectors()

  // Bank Providers operations
  const fetchBankProviders = useCallback(
    async (filters?: BankProvidersFilter) => {
      return store.fetchBankProviders(filters)
    },
    [store.fetchBankProviders]
  )

  const fetchBankProvider = useCallback(
    async (id: number) => {
      return store.fetchBankProvider(id)
    },
    [store.fetchBankProvider]
  )

  // Bank Accounts operations
  const fetchBankAccounts = useCallback(
    async (filters?: BankAccountsFilter) => {
      return store.fetchBankAccounts(filters)
    },
    [store.fetchBankAccounts]
  )

  const fetchBankAccount = useCallback(
    async (id: number) => {
      return store.fetchBankAccount(id)
    },
    [store.fetchBankAccount]
  )

  const createBankAccount = useCallback(
    async (data: BankAccountCreate): Promise<BankAccount> => {
      return store.createBankAccount(data)
    },
    [store.createBankAccount]
  )

  const updateBankAccount = useCallback(
    async (id: number, data: BankAccountUpdate): Promise<BankAccount> => {
      return store.updateBankAccount(id, data)
    },
    [store.updateBankAccount]
  )

  const deleteBankAccount = useCallback(
    async (id: number) => {
      return store.deleteBankAccount(id)
    },
    [store.deleteBankAccount]
  )

  const syncBankAccount = useCallback(
    async (id: number) => {
      return store.syncBankAccount(id)
    },
    [store.syncBankAccount]
  )

  // Transactions operations
  const fetchTransactions = useCallback(
    async (filters?: TransactionsFilter) => {
      return store.fetchTransactions(filters)
    },
    [store.fetchTransactions]
  )

  const fetchTransaction = useCallback(
    async (id: number) => {
      return store.fetchTransaction(id)
    },
    [store.fetchTransaction]
  )

  const updateTransaction = useCallback(
    async (id: number, data: TransactionUpdate): Promise<Transaction> => {
      return store.updateTransaction(id, data)
    },
    [store.updateTransaction]
  )

  // Pluggy Integration operations
  const connectBank = useCallback(
    async (data: ConnectBankRequest) => {
      return store.connectBank(data)
    },
    [store.connectBank]
  )

  const syncAccounts = useCallback(
    async (data: SyncAccountsRequest) => {
      return store.syncAccounts(data)
    },
    [store.syncAccounts]
  )

  const getSyncStatus = useCallback(
    async (itemId: string) => {
      return store.getSyncStatus(itemId)
    },
    [store.getSyncStatus]
  )

  // Summary operations
  const fetchAccountSummary = useCallback(
    async (companyId: number) => {
      return store.fetchAccountSummary(companyId)
    },
    [store.fetchAccountSummary]
  )

  const fetchTransactionSummary = useCallback(
    async (companyId: number, startDate: string, endDate: string) => {
      return store.fetchTransactionSummary(companyId, startDate, endDate)
    },
    [store.fetchTransactionSummary]
  )

  // Filter operations
  const setBankAccountsFilters = useCallback(
    (filters: BankAccountsFilter) => {
      return store.setBankAccountsFilters(filters)
    },
    [store.setBankAccountsFilters]
  )

  const setTransactionsFilters = useCallback(
    (filters: TransactionsFilter) => {
      return store.setTransactionsFilters(filters)
    },
    [store.setTransactionsFilters]
  )

  // Error clearing operations
  const clearBankAccountsError = useCallback(() => {
    return store.clearBankAccountsError()
  }, [store.clearBankAccountsError])

  const clearTransactionsError = useCallback(() => {
    return store.clearTransactionsError()
  }, [store.clearTransactionsError])

  const clearSyncError = useCallback(() => {
    return store.clearSyncError()
  }, [store.clearSyncError])

  // Return all state, actions, and computed values
  return {
    // Bank Providers state
    bankProviders: selectors.bankProviders,
    currentBankProvider: selectors.currentBankProvider,
    bankProvidersLoading: selectors.bankProvidersLoading,
    bankProvidersError: selectors.bankProvidersError,

    // Bank Accounts state
    bankAccounts: selectors.bankAccounts,
    currentBankAccount: selectors.currentBankAccount,
    bankAccountsLoading: selectors.bankAccountsLoading,
    bankAccountsError: selectors.bankAccountsError,
    bankAccountsFilters: selectors.bankAccountsFilters,
    bankAccountsPagination: selectors.bankAccountsPagination,

    // Transactions state
    transactions: selectors.transactions,
    currentTransaction: selectors.currentTransaction,
    transactionsLoading: selectors.transactionsLoading,
    transactionsError: selectors.transactionsError,
    transactionsFilters: selectors.transactionsFilters,
    transactionsPagination: selectors.transactionsPagination,

    // Summary state
    accountSummary: selectors.accountSummary,
    transactionSummary: selectors.transactionSummary,
    summaryLoading: selectors.summaryLoading,
    summaryError: selectors.summaryError,

    // Sync state
    syncStatus: selectors.syncStatus,
    syncLoading: selectors.syncLoading,
    syncError: selectors.syncError,

    // Computed values
    activeBankAccountsCount: selectors.activeBankAccountsCount,
    totalBalance: selectors.totalBalance,
    pendingTransactionsCount: selectors.pendingTransactionsCount,
    hasConnectedAccounts: selectors.hasConnectedAccounts,

    // Bank Providers actions
    fetchBankProviders,
    fetchBankProvider,

    // Bank Accounts actions
    fetchBankAccounts,
    fetchBankAccount,
    createBankAccount,
    updateBankAccount,
    deleteBankAccount,
    syncBankAccount,

    // Transactions actions
    fetchTransactions,
    fetchTransaction,
    updateTransaction,

    // Pluggy Integration actions
    connectBank,
    syncAccounts,
    getSyncStatus,

    // Summary actions
    fetchAccountSummary,
    fetchTransactionSummary,

    // Filter actions
    setBankAccountsFilters,
    setTransactionsFilters,

    // Error clearing actions
    clearBankAccountsError,
    clearTransactionsError,
    clearSyncError
  }
}

// Helper functions for common operations
export const useBankingHelpers = () => {
  const banking = useBanking()

  const getBankAccountById = useCallback(
    (id: number) => {
      return banking.bankAccounts.find(account => account.id === id)
    },
    [banking.bankAccounts]
  )

  const getTransactionById = useCallback(
    (id: number) => {
      return banking.transactions.find(transaction => transaction.id === id)
    },
    [banking.transactions]
  )

  const getBankProviderById = useCallback(
    (id: number) => {
      return banking.bankProviders.find(provider => provider.id === id)
    },
    [banking.bankProviders]
  )

  const getAccountsByProvider = useCallback(
    (providerId: number) => {
      return banking.bankAccounts.filter(
        account => account.bank_provider.id === providerId
      )
    },
    [banking.bankAccounts]
  )

  const getTransactionsByAccount = useCallback(
    (accountId: number) => {
      return banking.transactions.filter(
        transaction => transaction.bank_account === accountId
      )
    },
    [banking.transactions]
  )

  const getActiveAccounts = useCallback(() => {
    return banking.bankAccounts.filter(account => account.is_active)
  }, [banking.bankAccounts])

  const getPendingTransactions = useCallback(() => {
    return banking.transactions.filter(transaction => transaction.is_pending)
  }, [banking.transactions])

  const getTotalBalanceByAccountType = useCallback(
    (accountType: string) => {
      return banking.bankAccounts
        .filter(account => account.account_type === accountType && account.is_active)
        .reduce((sum, account) => sum + account.balance, 0)
    },
    [banking.bankAccounts]
  )

  return {
    getBankAccountById,
    getTransactionById,
    getBankProviderById,
    getAccountsByProvider,
    getTransactionsByAccount,
    getActiveAccounts,
    getPendingTransactions,
    getTotalBalanceByAccountType
  }
}

export default useBanking