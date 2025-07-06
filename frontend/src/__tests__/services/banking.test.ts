import { describe, it, expect, jest, beforeEach } from '@jest/globals'
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
  SyncAccountsRequest
} from '../../types/banking'

// Mock the api service
const mockApiGet = jest.fn()
const mockApiPost = jest.fn()
const mockApiPut = jest.fn()
const mockApiPatch = jest.fn()
const mockApiDelete = jest.fn()

jest.mock('../../services/api', () => ({
  api: {
    get: mockApiGet,
    post: mockApiPost,
    put: mockApiPut,
    patch: mockApiPatch,
    delete: mockApiDelete
  }
}))

describe('Banking Service', () => {
  beforeEach(() => {
    jest.clearAllMocks()
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

  describe('Bank Providers API', () => {
    it('should fetch bank providers with filters', async () => {
      const mockResponse: BankProvidersResponse = {
        count: 1,
        next: null,
        previous: null,
        results: [mockBankProvider]
      }

      mockApiGet.mockResolvedValue({ data: mockResponse })

      const { bankingService } = await import('../../services/banking')
      
      const filters: BankProvidersFilter = {
        is_active: true,
        supports_checking_account: true
      }

      const result = await bankingService.getBankProviders(filters)

      expect(mockApiGet).toHaveBeenCalledWith('/banking/bank-providers/', {
        params: filters
      })
      expect(result).toEqual(mockResponse)
    })

    it('should fetch single bank provider by id', async () => {
      mockApiGet.mockResolvedValue({ data: mockBankProvider })

      const { bankingService } = await import('../../services/banking')
      
      const result = await bankingService.getBankProvider(1)

      expect(mockApiGet).toHaveBeenCalledWith('/banking/bank-providers/1/')
      expect(result).toEqual(mockBankProvider)
    })
  })

  describe('Bank Accounts API', () => {
    it('should fetch bank accounts with filters', async () => {
      const mockResponse: BankAccountsResponse = {
        count: 1,
        next: null,
        previous: null,
        results: [mockBankAccount]
      }

      mockApiGet.mockResolvedValue({ data: mockResponse })

      const { bankingService } = await import('../../services/banking')
      
      const filters: BankAccountsFilter = {
        company: 1,
        is_active: true
      }

      const result = await bankingService.getBankAccounts(filters)

      expect(mockApiGet).toHaveBeenCalledWith('/banking/bank-accounts/', {
        params: filters
      })
      expect(result).toEqual(mockResponse)
    })

    it('should fetch single bank account by id', async () => {
      mockApiGet.mockResolvedValue({ data: mockBankAccount })

      const { bankingService } = await import('../../services/banking')
      
      const result = await bankingService.getBankAccount(1)

      expect(mockApiGet).toHaveBeenCalledWith('/banking/bank-accounts/1/')
      expect(result).toEqual(mockBankAccount)
    })

    it('should create new bank account', async () => {
      const createData: BankAccountCreate = {
        company: 1,
        bank_provider: 1,
        pluggy_item_id: 'item_123',
        pluggy_account_id: 'account_456',
        account_type: 'CHECKING',
        name: 'Nova Conta',
        agency: '1234',
        account_number: '567890',
        balance: 1000.00,
        is_active: true
      }

      mockApiPost.mockResolvedValue({ data: mockBankAccount })

      const { bankingService } = await import('../../services/banking')
      
      const result = await bankingService.createBankAccount(createData)

      expect(mockApiPost).toHaveBeenCalledWith('/banking/bank-accounts/', createData)
      expect(result).toEqual(mockBankAccount)
    })

    it('should update bank account', async () => {
      const updateData: BankAccountUpdate = {
        name: 'Conta Atualizada',
        balance: 2000.00
      }

      const updatedAccount = { ...mockBankAccount, ...updateData }
      mockApiPatch.mockResolvedValue({ data: updatedAccount })

      const { bankingService } = await import('../../services/banking')
      
      const result = await bankingService.updateBankAccount(1, updateData)

      expect(mockApiPatch).toHaveBeenCalledWith('/banking/bank-accounts/1/', updateData)
      expect(result).toEqual(updatedAccount)
    })

    it('should delete bank account', async () => {
      mockApiDelete.mockResolvedValue({ data: null })

      const { bankingService } = await import('../../services/banking')
      
      await bankingService.deleteBankAccount(1)

      expect(mockApiDelete).toHaveBeenCalledWith('/banking/bank-accounts/1/')
    })

    it('should sync bank account', async () => {
      const syncResult = { synced_transactions: 25, synced_at: '2023-01-15T15:00:00Z' }
      mockApiPost.mockResolvedValue({ data: syncResult })

      const { bankingService } = await import('../../services/banking')
      
      const result = await bankingService.syncBankAccount(1)

      expect(mockApiPost).toHaveBeenCalledWith('/banking/bank-accounts/1/sync/')
      expect(result).toEqual(syncResult)
    })
  })

  describe('Transactions API', () => {
    it('should fetch transactions with filters', async () => {
      const mockResponse: TransactionsResponse = {
        count: 1,
        next: null,
        previous: null,
        results: [mockTransaction]
      }

      mockApiGet.mockResolvedValue({ data: mockResponse })

      const { bankingService } = await import('../../services/banking')
      
      const filters: TransactionsFilter = {
        bank_account: 1,
        start_date: '2023-01-01',
        end_date: '2023-01-31'
      }

      const result = await bankingService.getTransactions(filters)

      expect(mockApiGet).toHaveBeenCalledWith('/banking/transactions/', {
        params: filters
      })
      expect(result).toEqual(mockResponse)
    })

    it('should fetch single transaction by id', async () => {
      mockApiGet.mockResolvedValue({ data: mockTransaction })

      const { bankingService } = await import('../../services/banking')
      
      const result = await bankingService.getTransaction(1)

      expect(mockApiGet).toHaveBeenCalledWith('/banking/transactions/1/')
      expect(result).toEqual(mockTransaction)
    })

    it('should update transaction', async () => {
      const updateData: TransactionUpdate = {
        category: 'Nova Categoria',
        subcategory: 'Nova Subcategoria'
      }

      const updatedTransaction = { ...mockTransaction, ...updateData }
      mockApiPatch.mockResolvedValue({ data: updatedTransaction })

      const { bankingService } = await import('../../services/banking')
      
      const result = await bankingService.updateTransaction(1, updateData)

      expect(mockApiPatch).toHaveBeenCalledWith('/banking/transactions/1/', updateData)
      expect(result).toEqual(updatedTransaction)
    })
  })

  describe('Pluggy Integration', () => {
    it('should connect bank account via Pluggy', async () => {
      const connectData: ConnectBankRequest = {
        company: 1,
        connector_id: 'bb-connector',
        credentials: {
          user: 'test@example.com',
          password: 'password123'
        }
      }

      const connectResult = {
        item_id: 'item_123',
        status: 'UPDATED',
        accounts: [mockBankAccount]
      }

      mockApiPost.mockResolvedValue({ data: connectResult })

      const { bankingService } = await import('../../services/banking')
      
      const result = await bankingService.connectBank(connectData)

      expect(mockApiPost).toHaveBeenCalledWith('/banking/connect/', connectData)
      expect(result).toEqual(connectResult)
    })

    it('should sync accounts from Pluggy', async () => {
      const syncData: SyncAccountsRequest = {
        company: 1,
        item_id: 'item_123'
      }

      const syncResult = {
        synced_accounts: 2,
        synced_transactions: 150,
        synced_at: '2023-01-15T15:00:00Z'
      }

      mockApiPost.mockResolvedValue({ data: syncResult })

      const { bankingService } = await import('../../services/banking')
      
      const result = await bankingService.syncAccounts(syncData)

      expect(mockApiPost).toHaveBeenCalledWith('/banking/sync/', syncData)
      expect(result).toEqual(syncResult)
    })

    it('should get sync status', async () => {
      const statusResult = {
        item_id: 'item_123',
        status: 'UPDATED',
        last_sync: '2023-01-15T15:00:00Z',
        accounts_count: 2,
        transactions_count: 150
      }

      mockApiGet.mockResolvedValue({ data: statusResult })

      const { bankingService } = await import('../../services/banking')
      
      const result = await bankingService.getSyncStatus('item_123')

      expect(mockApiGet).toHaveBeenCalledWith('/banking/sync-status/item_123/')
      expect(result).toEqual(statusResult)
    })
  })

  describe('Dashboard/Summary', () => {
    it('should fetch account summary', async () => {
      const summaryResult = {
        total_accounts: 3,
        total_balance: 5500.75,
        checking_accounts: 2,
        savings_accounts: 1,
        credit_cards: 0,
        last_sync: '2023-01-15T15:00:00Z'
      }

      mockApiGet.mockResolvedValue({ data: summaryResult })

      const { bankingService } = await import('../../services/banking')
      
      const result = await bankingService.getAccountSummary(1)

      expect(mockApiGet).toHaveBeenCalledWith('/banking/accounts-summary/', {
        params: { company: 1 }
      })
      expect(result).toEqual(summaryResult)
    })

    it('should fetch transaction summary', async () => {
      const summaryResult = {
        total_transactions: 150,
        total_credits: 5000.00,
        total_debits: -3500.00,
        pending_transactions: 5,
        period_start: '2023-01-01',
        period_end: '2023-01-31'
      }

      mockApiGet.mockResolvedValue({ data: summaryResult })

      const { bankingService } = await import('../../services/banking')
      
      const result = await bankingService.getTransactionSummary(1, '2023-01-01', '2023-01-31')

      expect(mockApiGet).toHaveBeenCalledWith('/banking/transactions-summary/', {
        params: { 
          company: 1,
          start_date: '2023-01-01',
          end_date: '2023-01-31'
        }
      })
      expect(result).toEqual(summaryResult)
    })
  })

  describe('Service validation', () => {
    it('should handle API errors gracefully', async () => {
      const apiError = new Error('API Error')
      mockApiGet.mockRejectedValue(apiError)

      const { bankingService } = await import('../../services/banking')
      
      await expect(bankingService.getBankProviders({})).rejects.toThrow('API Error')
    })

    it('should build query params correctly', async () => {
      mockApiGet.mockResolvedValue({ data: { results: [] } })

      const { bankingService } = await import('../../services/banking')
      
      const filters: BankAccountsFilter = {
        company: 1,
        bank_provider: 1,
        account_type: 'CHECKING',
        is_active: true,
        search: 'test'
      }

      await bankingService.getBankAccounts(filters)

      expect(mockApiGet).toHaveBeenCalledWith('/banking/bank-accounts/', {
        params: filters
      })
    })
  })
})