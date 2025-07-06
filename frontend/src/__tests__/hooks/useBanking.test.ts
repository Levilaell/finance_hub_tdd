import { describe, it, expect, jest, beforeEach } from '@jest/globals'
import { renderHook, act } from '@testing-library/react'
import type { 
  BankProvider,
  BankAccount,
  Transaction
} from '../../types/banking'

// Mock the banking store
const mockFetchBankProviders = jest.fn()
const mockFetchBankProvider = jest.fn()
const mockFetchBankAccounts = jest.fn()
const mockFetchBankAccount = jest.fn()
const mockCreateBankAccount = jest.fn()
const mockUpdateBankAccount = jest.fn()
const mockDeleteBankAccount = jest.fn()
const mockSyncBankAccount = jest.fn()
const mockFetchTransactions = jest.fn()
const mockFetchTransaction = jest.fn()
const mockUpdateTransaction = jest.fn()
const mockConnectBank = jest.fn()
const mockSyncAccounts = jest.fn()
const mockGetSyncStatus = jest.fn()
const mockFetchAccountSummary = jest.fn()
const mockFetchTransactionSummary = jest.fn()
const mockSetBankAccountsFilters = jest.fn()
const mockSetTransactionsFilters = jest.fn()
const mockClearBankAccountsError = jest.fn()
const mockClearTransactionsError = jest.fn()
const mockClearSyncError = jest.fn()

const mockStoreState = {
  bankProviders: [],
  currentBankProvider: null,
  bankProvidersLoading: false,
  bankProvidersError: null,
  bankAccounts: [],
  currentBankAccount: null,
  bankAccountsLoading: false,
  bankAccountsError: null,
  bankAccountsFilters: {},
  bankAccountsPagination: {
    count: 0,
    page: 1,
    pageSize: 20,
    totalPages: 0
  },
  transactions: [],
  currentTransaction: null,
  transactionsLoading: false,
  transactionsError: null,
  transactionsFilters: {},
  transactionsPagination: {
    count: 0,
    page: 1,
    pageSize: 20,
    totalPages: 0
  },
  accountSummary: null,
  transactionSummary: null,
  summaryLoading: false,
  summaryError: null,
  syncStatus: null,
  syncLoading: false,
  syncError: null,
  // Computed values
  activeBankAccountsCount: 0,
  totalBalance: 0,
  pendingTransactionsCount: 0,
  hasConnectedAccounts: false,
  // Actions
  fetchBankProviders: mockFetchBankProviders,
  fetchBankProvider: mockFetchBankProvider,
  fetchBankAccounts: mockFetchBankAccounts,
  fetchBankAccount: mockFetchBankAccount,
  createBankAccount: mockCreateBankAccount,
  updateBankAccount: mockUpdateBankAccount,
  deleteBankAccount: mockDeleteBankAccount,
  syncBankAccount: mockSyncBankAccount,
  fetchTransactions: mockFetchTransactions,
  fetchTransaction: mockFetchTransaction,
  updateTransaction: mockUpdateTransaction,
  connectBank: mockConnectBank,
  syncAccounts: mockSyncAccounts,
  getSyncStatus: mockGetSyncStatus,
  fetchAccountSummary: mockFetchAccountSummary,
  fetchTransactionSummary: mockFetchTransactionSummary,
  setBankAccountsFilters: mockSetBankAccountsFilters,
  setTransactionsFilters: mockSetTransactionsFilters,
  clearBankAccountsError: mockClearBankAccountsError,
  clearTransactionsError: mockClearTransactionsError,
  clearSyncError: mockClearSyncError
}

jest.mock('../../store/banking', () => ({
  useBankingStore: () => mockStoreState,
  useBankingSelectors: () => mockStoreState
}))

describe('useBanking Hook', () => {
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

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Bank Providers operations', () => {
    it('should provide bank providers state and actions', async () => {
      const { useBanking } = await import('../../hooks/useBanking')
      const { result } = renderHook(() => useBanking())

      expect(result.current.bankProviders).toEqual([])
      expect(result.current.currentBankProvider).toBeNull()
      expect(result.current.bankProvidersLoading).toBe(false)
      expect(result.current.bankProvidersError).toBeNull()

      // Check actions are available
      expect(typeof result.current.fetchBankProviders).toBe('function')
      expect(typeof result.current.fetchBankProvider).toBe('function')
    })

    it('should call fetchBankProviders with correct parameters', async () => {
      const { useBanking } = await import('../../hooks/useBanking')
      const { result } = renderHook(() => useBanking())

      const filters = { is_active: true }

      await act(async () => {
        await result.current.fetchBankProviders(filters)
      })

      expect(mockFetchBankProviders).toHaveBeenCalledWith(filters)
    })

    it('should call fetchBankProvider with correct id', async () => {
      const { useBanking } = await import('../../hooks/useBanking')
      const { result } = renderHook(() => useBanking())

      await act(async () => {
        await result.current.fetchBankProvider(1)
      })

      expect(mockFetchBankProvider).toHaveBeenCalledWith(1)
    })
  })

  describe('Bank Accounts operations', () => {
    it('should provide bank accounts state and actions', async () => {
      const { useBanking } = await import('../../hooks/useBanking')
      const { result } = renderHook(() => useBanking())

      expect(result.current.bankAccounts).toEqual([])
      expect(result.current.currentBankAccount).toBeNull()
      expect(result.current.bankAccountsLoading).toBe(false)
      expect(result.current.bankAccountsError).toBeNull()
      expect(result.current.bankAccountsFilters).toEqual({})
      expect(result.current.bankAccountsPagination).toBeDefined()

      // Check actions are available
      expect(typeof result.current.fetchBankAccounts).toBe('function')
      expect(typeof result.current.createBankAccount).toBe('function')
      expect(typeof result.current.updateBankAccount).toBe('function')
      expect(typeof result.current.deleteBankAccount).toBe('function')
      expect(typeof result.current.syncBankAccount).toBe('function')
    })

    it('should call fetchBankAccounts with correct parameters', async () => {
      const { useBanking } = await import('../../hooks/useBanking')
      const { result } = renderHook(() => useBanking())

      const filters = { company: 1, is_active: true }

      await act(async () => {
        await result.current.fetchBankAccounts(filters)
      })

      expect(mockFetchBankAccounts).toHaveBeenCalledWith(filters)
    })

    it('should call createBankAccount with correct data', async () => {
      const { useBanking } = await import('../../hooks/useBanking')
      const { result } = renderHook(() => useBanking())

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

      let createdAccount: BankAccount | undefined

      await act(async () => {
        createdAccount = await result.current.createBankAccount(createData)
      })

      expect(mockCreateBankAccount).toHaveBeenCalledWith(createData)
      expect(createdAccount).toEqual(mockBankAccount)
    })

    it('should call updateBankAccount with correct parameters', async () => {
      const { useBanking } = await import('../../hooks/useBanking')
      const { result } = renderHook(() => useBanking())

      const updateData = { name: 'Conta Atualizada' }
      const updatedAccount = { ...mockBankAccount, ...updateData }

      mockUpdateBankAccount.mockResolvedValue(updatedAccount)

      let updated: BankAccount | undefined

      await act(async () => {
        updated = await result.current.updateBankAccount(1, updateData)
      })

      expect(mockUpdateBankAccount).toHaveBeenCalledWith(1, updateData)
      expect(updated).toEqual(updatedAccount)
    })

    it('should call deleteBankAccount with correct id', async () => {
      const { useBanking } = await import('../../hooks/useBanking')
      const { result } = renderHook(() => useBanking())

      await act(async () => {
        await result.current.deleteBankAccount(1)
      })

      expect(mockDeleteBankAccount).toHaveBeenCalledWith(1)
    })

    it('should call syncBankAccount with correct id', async () => {
      const { useBanking } = await import('../../hooks/useBanking')
      const { result } = renderHook(() => useBanking())

      const syncResult = { synced_transactions: 25, synced_at: '2023-01-15T15:00:00Z' }
      mockSyncBankAccount.mockResolvedValue(syncResult)

      let syncResponse: any

      await act(async () => {
        syncResponse = await result.current.syncBankAccount(1)
      })

      expect(mockSyncBankAccount).toHaveBeenCalledWith(1)
      expect(syncResponse).toEqual(syncResult)
    })
  })

  describe('Transactions operations', () => {
    it('should provide transactions state and actions', async () => {
      const { useBanking } = await import('../../hooks/useBanking')
      const { result } = renderHook(() => useBanking())

      expect(result.current.transactions).toEqual([])
      expect(result.current.currentTransaction).toBeNull()
      expect(result.current.transactionsLoading).toBe(false)
      expect(result.current.transactionsError).toBeNull()
      expect(result.current.transactionsFilters).toEqual({})
      expect(result.current.transactionsPagination).toBeDefined()

      // Check actions are available
      expect(typeof result.current.fetchTransactions).toBe('function')
      expect(typeof result.current.updateTransaction).toBe('function')
    })

    it('should call fetchTransactions with correct parameters', async () => {
      const { useBanking } = await import('../../hooks/useBanking')
      const { result } = renderHook(() => useBanking())

      const filters = { bank_account: 1, start_date: '2023-01-01' }

      await act(async () => {
        await result.current.fetchTransactions(filters)
      })

      expect(mockFetchTransactions).toHaveBeenCalledWith(filters)
    })

    it('should call updateTransaction with correct parameters', async () => {
      const { useBanking } = await import('../../hooks/useBanking')
      const { result } = renderHook(() => useBanking())

      const updateData = { category: 'Nova Categoria' }
      const updatedTransaction = { ...mockTransaction, ...updateData }

      mockUpdateTransaction.mockResolvedValue(updatedTransaction)

      let updated: Transaction | undefined

      await act(async () => {
        updated = await result.current.updateTransaction(1, updateData)
      })

      expect(mockUpdateTransaction).toHaveBeenCalledWith(1, updateData)
      expect(updated).toEqual(updatedTransaction)
    })
  })

  describe('Pluggy Integration operations', () => {
    it('should provide Pluggy integration actions', async () => {
      const { useBanking } = await import('../../hooks/useBanking')
      const { result } = renderHook(() => useBanking())

      expect(typeof result.current.connectBank).toBe('function')
      expect(typeof result.current.syncAccounts).toBe('function')
      expect(typeof result.current.getSyncStatus).toBe('function')
      expect(result.current.syncLoading).toBe(false)
      expect(result.current.syncError).toBeNull()
    })

    it('should call connectBank with correct data', async () => {
      const { useBanking } = await import('../../hooks/useBanking')
      const { result } = renderHook(() => useBanking())

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

      let result_: any

      await act(async () => {
        result_ = await result.current.connectBank(connectData)
      })

      expect(mockConnectBank).toHaveBeenCalledWith(connectData)
      expect(result_).toEqual(connectResult)
    })

    it('should call syncAccounts with correct data', async () => {
      const { useBanking } = await import('../../hooks/useBanking')
      const { result } = renderHook(() => useBanking())

      const syncData = { company: 1, item_id: 'item_123' }
      const syncResult = {
        synced_accounts: 2,
        synced_transactions: 150,
        synced_at: '2023-01-15T15:00:00Z'
      }

      mockSyncAccounts.mockResolvedValue(syncResult)

      let syncResponse: any

      await act(async () => {
        syncResponse = await result.current.syncAccounts(syncData)
      })

      expect(mockSyncAccounts).toHaveBeenCalledWith(syncData)
      expect(syncResponse).toEqual(syncResult)
    })
  })

  describe('Summary operations', () => {
    it('should provide summary state and actions', async () => {
      const { useBanking } = await import('../../hooks/useBanking')
      const { result } = renderHook(() => useBanking())

      expect(result.current.accountSummary).toBeNull()
      expect(result.current.transactionSummary).toBeNull()
      expect(result.current.summaryLoading).toBe(false)
      expect(result.current.summaryError).toBeNull()

      expect(typeof result.current.fetchAccountSummary).toBe('function')
      expect(typeof result.current.fetchTransactionSummary).toBe('function')
    })

    it('should call fetchAccountSummary with correct company id', async () => {
      const { useBanking } = await import('../../hooks/useBanking')
      const { result } = renderHook(() => useBanking())

      await act(async () => {
        await result.current.fetchAccountSummary(1)
      })

      expect(mockFetchAccountSummary).toHaveBeenCalledWith(1)
    })

    it('should call fetchTransactionSummary with correct parameters', async () => {
      const { useBanking } = await import('../../hooks/useBanking')
      const { result } = renderHook(() => useBanking())

      await act(async () => {
        await result.current.fetchTransactionSummary(1, '2023-01-01', '2023-01-31')
      })

      expect(mockFetchTransactionSummary).toHaveBeenCalledWith(1, '2023-01-01', '2023-01-31')
    })
  })

  describe('Filter operations', () => {
    it('should set filters correctly', async () => {
      const { useBanking } = await import('../../hooks/useBanking')
      const { result } = renderHook(() => useBanking())

      const accountsFilter = { company: 1, is_active: true }
      const transactionsFilter = { bank_account: 1 }

      act(() => {
        result.current.setBankAccountsFilters(accountsFilter)
        result.current.setTransactionsFilters(transactionsFilter)
      })

      expect(mockSetBankAccountsFilters).toHaveBeenCalledWith(accountsFilter)
      expect(mockSetTransactionsFilters).toHaveBeenCalledWith(transactionsFilter)
    })

    it('should clear errors correctly', async () => {
      const { useBanking } = await import('../../hooks/useBanking')
      const { result } = renderHook(() => useBanking())

      act(() => {
        result.current.clearBankAccountsError()
        result.current.clearTransactionsError()
        result.current.clearSyncError()
      })

      expect(mockClearBankAccountsError).toHaveBeenCalled()
      expect(mockClearTransactionsError).toHaveBeenCalled()
      expect(mockClearSyncError).toHaveBeenCalled()
    })
  })

  describe('Computed values', () => {
    it('should provide computed selectors', async () => {
      const { useBanking } = await import('../../hooks/useBanking')
      const { result } = renderHook(() => useBanking())

      expect(typeof result.current.activeBankAccountsCount).toBe('number')
      expect(typeof result.current.totalBalance).toBe('number')
      expect(typeof result.current.pendingTransactionsCount).toBe('number')
      expect(typeof result.current.hasConnectedAccounts).toBe('boolean')
    })
  })
})