import { describe, it, expect, jest, beforeEach } from '@jest/globals'
import type { 
  BankProvider,
  BankAccount,
  Transaction,
  BankAccountsFilter,
  TransactionsFilter
} from '../../types/banking'

// Mock the banking service
const mockGetBankProviders = jest.fn()
const mockGetBankProvider = jest.fn()
const mockGetBankAccounts = jest.fn()
const mockGetBankAccount = jest.fn()
const mockCreateBankAccount = jest.fn()
const mockUpdateBankAccount = jest.fn()
const mockDeleteBankAccount = jest.fn()
const mockSyncBankAccount = jest.fn()
const mockGetTransactions = jest.fn()
const mockGetTransaction = jest.fn()
const mockUpdateTransaction = jest.fn()
const mockConnectBank = jest.fn()
const mockSyncAccounts = jest.fn()
const mockGetSyncStatus = jest.fn()
const mockGetAccountSummary = jest.fn()
const mockGetTransactionSummary = jest.fn()

jest.mock('../../services/banking', () => ({
  bankingService: {
    getBankProviders: mockGetBankProviders,
    getBankProvider: mockGetBankProvider,
    getBankAccounts: mockGetBankAccounts,
    getBankAccount: mockGetBankAccount,
    createBankAccount: mockCreateBankAccount,
    updateBankAccount: mockUpdateBankAccount,
    deleteBankAccount: mockDeleteBankAccount,
    syncBankAccount: mockSyncBankAccount,
    getTransactions: mockGetTransactions,
    getTransaction: mockGetTransaction,
    updateTransaction: mockUpdateTransaction,
    connectBank: mockConnectBank,
    syncAccounts: mockSyncAccounts,
    getSyncStatus: mockGetSyncStatus,
    getAccountSummary: mockGetAccountSummary,
    getTransactionSummary: mockGetTransactionSummary,
  }
}))

describe('Banking Store', () => {
  beforeEach(async () => {
    jest.clearAllMocks()
    // Reset store state before each test
    const { useBankingStore } = await import('../../store/banking')
    useBankingStore.getState().resetState()
  })

  const mockBankProvider: BankProvider = {
    id: 1,
    name: 'Banco do Brasil',
    code: 'BB',
    pluggy_connector_id: 'bb-connector',
    logo_url: 'https://example.com/bb-logo.png',
    is_active: true,
    supports_checking_account: true,
    supports_savings_account: true,
    supports_credit_card: false,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  }

  const mockBankAccount: BankAccount = {
    id: 1,
    company: 1,
    bank_provider: mockBankProvider,
    pluggy_item_id: 'item_123',
    pluggy_account_id: 'account_456',
    account_type: 'CHECKING',
    name: 'Conta Corrente Principal',
    agency: '1234',
    account_number: '567890',
    balance: 1500.75,
    is_active: true,
    last_sync: '2023-01-01T12:00:00Z',
    transactions_count: 50,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  }

  const mockTransaction: Transaction = {
    id: 1,
    bank_account: 1,
    bank_account_details: {
      name: 'Conta Corrente Principal',
      bank_provider_name: 'Banco do Brasil',
      account_type: 'CHECKING'
    },
    pluggy_transaction_id: 'txn_789',
    transaction_type: 'DEBIT',
    amount: -150.50,
    description: 'Compra no supermercado',
    transaction_date: '2023-01-15',
    posted_date: '2023-01-16',
    category: 'Alimentação',
    subcategory: 'Supermercado',
    is_pending: false,
    created_at: '2023-01-15T10:30:00Z',
    updated_at: '2023-01-15T10:30:00Z'
  }

  describe('Bank Providers state management', () => {
    it('should initialize with default state', async () => {
      const { useBankingStore } = await import('../../store/banking')
      const store = useBankingStore.getState()

      expect(store.bankProviders).toEqual([])
      expect(store.currentBankProvider).toBeNull()
      expect(store.bankProvidersLoading).toBe(false)
      expect(store.bankProvidersError).toBeNull()
    })

    it('should fetch bank providers successfully', async () => {
      const mockResponse = {
        count: 1,
        next: null,
        previous: null,
        results: [mockBankProvider]
      }

      mockGetBankProviders.mockResolvedValue(mockResponse)

      const { useBankingStore } = await import('../../store/banking')
      const store = useBankingStore.getState()

      await store.fetchBankProviders({ is_active: true })

      expect(mockGetBankProviders).toHaveBeenCalledWith({ is_active: true })
      expect(store.bankProviders).toEqual([mockBankProvider])
      expect(store.bankProvidersLoading).toBe(false)
      expect(store.bankProvidersError).toBeNull()
    })

    it('should handle fetch bank providers error', async () => {
      const error = new Error('API Error')
      mockGetBankProviders.mockRejectedValue(error)

      const { useBankingStore } = await import('../../store/banking')
      const store = useBankingStore.getState()

      await store.fetchBankProviders({})

      expect(store.bankProviders).toEqual([])
      expect(store.bankProvidersLoading).toBe(false)
      expect(store.bankProvidersError).toBe('API Error')
    })

    it('should fetch single bank provider successfully', async () => {
      mockGetBankProvider.mockResolvedValue(mockBankProvider)

      const { useBankingStore } = await import('../../store/banking')
      const store = useBankingStore.getState()

      await store.fetchBankProvider(1)

      expect(mockGetBankProvider).toHaveBeenCalledWith(1)
      expect(store.currentBankProvider).toEqual(mockBankProvider)
    })
  })

  describe('Bank Accounts state management', () => {
    it('should initialize bank accounts state correctly', async () => {
      const { useBankingStore } = await import('../../store/banking')
      const store = useBankingStore.getState()

      expect(store.bankAccounts).toEqual([])
      expect(store.currentBankAccount).toBeNull()
      expect(store.bankAccountsLoading).toBe(false)
      expect(store.bankAccountsError).toBeNull()
      expect(store.bankAccountsFilters).toEqual({})
      expect(store.bankAccountsPagination).toEqual({
        count: 0,
        page: 1,
        pageSize: 20,
        totalPages: 0
      })
    })

    it('should fetch bank accounts successfully', async () => {
      const mockResponse = {
        count: 1,
        next: null,
        previous: null,
        results: [mockBankAccount]
      }

      mockGetBankAccounts.mockResolvedValue(mockResponse)

      const { useBankingStore } = await import('../../store/banking')
      const store = useBankingStore.getState()

      await store.fetchBankAccounts({ company: 1 })

      expect(mockGetBankAccounts).toHaveBeenCalledWith({ company: 1 })
      expect(store.bankAccounts).toEqual([mockBankAccount])
      expect(store.bankAccountsPagination.count).toBe(1)
      expect(store.bankAccountsLoading).toBe(false)
      expect(store.bankAccountsError).toBeNull()
    })

    it('should create bank account successfully', async () => {
      const createData = {
        company: 1,
        bank_provider: 1,
        pluggy_item_id: 'item_123',
        pluggy_account_id: 'account_456',
        account_type: 'CHECKING' as const,
        name: 'Nova Conta',
        balance: 1000.00,
        is_active: true
      }

      mockCreateBankAccount.mockResolvedValue(mockBankAccount)

      const { useBankingStore } = await import('../../store/banking')
      const store = useBankingStore.getState()

      const result = await store.createBankAccount(createData)

      expect(mockCreateBankAccount).toHaveBeenCalledWith(createData)
      expect(result).toEqual(mockBankAccount)
      expect(store.bankAccounts).toContain(mockBankAccount)
    })

    it('should update bank account successfully', async () => {
      const updateData = { name: 'Conta Atualizada' }
      const updatedAccount = { ...mockBankAccount, ...updateData }

      mockUpdateBankAccount.mockResolvedValue(updatedAccount)

      const { useBankingStore } = await import('../../store/banking')
      const store = useBankingStore.getState()
      
      // Set initial accounts
      store.setBankAccounts([mockBankAccount])

      const result = await store.updateBankAccount(1, updateData)

      expect(mockUpdateBankAccount).toHaveBeenCalledWith(1, updateData)
      expect(result).toEqual(updatedAccount)
      expect(store.bankAccounts[0]).toEqual(updatedAccount)
    })

    it('should delete bank account successfully', async () => {
      mockDeleteBankAccount.mockResolvedValue(undefined)

      const { useBankingStore } = await import('../../store/banking')
      const store = useBankingStore.getState()
      
      // Set initial accounts
      store.setBankAccounts([mockBankAccount])

      await store.deleteBankAccount(1)

      expect(mockDeleteBankAccount).toHaveBeenCalledWith(1)
      expect(store.bankAccounts).toHaveLength(0)
    })

    it('should sync bank account successfully', async () => {
      const syncResult = { synced_transactions: 25, synced_at: '2023-01-15T15:00:00Z' }
      mockSyncBankAccount.mockResolvedValue(syncResult)

      const { useBankingStore } = await import('../../store/banking')
      const store = useBankingStore.getState()

      const result = await store.syncBankAccount(1)

      expect(mockSyncBankAccount).toHaveBeenCalledWith(1)
      expect(result).toEqual(syncResult)
    })
  })

  describe('Transactions state management', () => {
    it('should initialize transactions state correctly', async () => {
      const { useBankingStore } = await import('../../store/banking')
      const store = useBankingStore.getState()

      expect(store.transactions).toEqual([])
      expect(store.currentTransaction).toBeNull()
      expect(store.transactionsLoading).toBe(false)
      expect(store.transactionsError).toBeNull()
      expect(store.transactionsFilters).toEqual({})
      expect(store.transactionsPagination).toEqual({
        count: 0,
        page: 1,
        pageSize: 20,
        totalPages: 0
      })
    })

    it('should fetch transactions successfully', async () => {
      const mockResponse = {
        count: 1,
        next: null,
        previous: null,
        results: [mockTransaction]
      }

      mockGetTransactions.mockResolvedValue(mockResponse)

      const { useBankingStore } = await import('../../store/banking')
      const store = useBankingStore.getState()

      await store.fetchTransactions({ bank_account: 1 })

      expect(mockGetTransactions).toHaveBeenCalledWith({ bank_account: 1 })
      expect(store.transactions).toEqual([mockTransaction])
      expect(store.transactionsPagination.count).toBe(1)
      expect(store.transactionsLoading).toBe(false)
      expect(store.transactionsError).toBeNull()
    })

    it('should update transaction successfully', async () => {
      const updateData = { category: 'Nova Categoria' }
      const updatedTransaction = { ...mockTransaction, ...updateData }

      mockUpdateTransaction.mockResolvedValue(updatedTransaction)

      const { useBankingStore } = await import('../../store/banking')
      const store = useBankingStore.getState()
      
      // Set initial transactions
      store.setTransactions([mockTransaction])

      const result = await store.updateTransaction(1, updateData)

      expect(mockUpdateTransaction).toHaveBeenCalledWith(1, updateData)
      expect(result).toEqual(updatedTransaction)
      expect(store.transactions[0]).toEqual(updatedTransaction)
    })
  })

  describe('Pluggy Integration', () => {
    it('should connect bank successfully', async () => {
      const connectData = {
        company: 1,
        connector_id: 'bb-connector',
        credentials: { user: 'test', password: 'pass' }
      }

      const connectResult = {
        item_id: 'item_123',
        status: 'UPDATED',
        accounts: [mockBankAccount]
      }

      mockConnectBank.mockResolvedValue(connectResult)

      const { useBankingStore } = await import('../../store/banking')
      const store = useBankingStore.getState()

      const result = await store.connectBank(connectData)

      expect(mockConnectBank).toHaveBeenCalledWith(connectData)
      expect(result).toEqual(connectResult)
    })

    it('should sync accounts successfully', async () => {
      const syncData = { company: 1, item_id: 'item_123' }
      const syncResult = {
        synced_accounts: 2,
        synced_transactions: 150,
        synced_at: '2023-01-15T15:00:00Z'
      }

      mockSyncAccounts.mockResolvedValue(syncResult)

      const { useBankingStore } = await import('../../store/banking')
      const store = useBankingStore.getState()

      const result = await store.syncAccounts(syncData)

      expect(mockSyncAccounts).toHaveBeenCalledWith(syncData)
      expect(result).toEqual(syncResult)
    })
  })

  describe('State setters and getters', () => {
    it('should set filters correctly', async () => {
      const accountsFilter: BankAccountsFilter = { company: 1, is_active: true }
      const transactionsFilter: TransactionsFilter = { bank_account: 1 }

      const { useBankingStore } = await import('../../store/banking')
      const store = useBankingStore.getState()

      store.setBankAccountsFilters(accountsFilter)
      store.setTransactionsFilters(transactionsFilter)

      expect(store.bankAccountsFilters).toEqual(accountsFilter)
      expect(store.transactionsFilters).toEqual(transactionsFilter)
    })

    it('should set loading states correctly', async () => {
      const { useBankingStore } = await import('../../store/banking')
      const store = useBankingStore.getState()

      store.setBankAccountsLoading(true)
      store.setTransactionsLoading(true)

      expect(store.bankAccountsLoading).toBe(true)
      expect(store.transactionsLoading).toBe(true)
    })

    it('should clear errors correctly', async () => {
      const { useBankingStore } = await import('../../store/banking')
      const store = useBankingStore.getState()

      // Set some errors first
      store.setBankAccountsError('Some error')
      store.setTransactionsError('Another error')

      // Clear errors
      store.clearBankAccountsError()
      store.clearTransactionsError()

      expect(store.bankAccountsError).toBeNull()
      expect(store.transactionsError).toBeNull()
    })

    it('should reset store state correctly', async () => {
      const { useBankingStore } = await import('../../store/banking')
      const store = useBankingStore.getState()

      // Set some state
      store.setBankAccounts([mockBankAccount])
      store.setTransactions([mockTransaction])
      store.setBankAccountsFilters({ company: 1 })

      // Reset
      store.resetState()

      expect(store.bankAccounts).toEqual([])
      expect(store.transactions).toEqual([])
      expect(store.bankAccountsFilters).toEqual({})
      expect(store.currentBankAccount).toBeNull()
      expect(store.currentTransaction).toBeNull()
    })
  })
})