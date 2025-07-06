import { describe, it, expect } from '@jest/globals'

describe('Banking Types', () => {
  it('should define BankProvider interface correctly', () => {
    const mockBankProvider = {
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

    // Test that all required fields are present
    expect(mockBankProvider).toHaveProperty('id')
    expect(mockBankProvider).toHaveProperty('name')
    expect(mockBankProvider).toHaveProperty('code')
    expect(mockBankProvider).toHaveProperty('pluggy_connector_id')
    expect(mockBankProvider).toHaveProperty('logo_url')
    expect(mockBankProvider).toHaveProperty('is_active')
    expect(mockBankProvider).toHaveProperty('supports_checking_account')
    expect(mockBankProvider).toHaveProperty('supports_savings_account')
    expect(mockBankProvider).toHaveProperty('supports_credit_card')
    expect(mockBankProvider).toHaveProperty('created_at')
    expect(mockBankProvider).toHaveProperty('updated_at')

    // Test types
    expect(typeof mockBankProvider.id).toBe('number')
    expect(typeof mockBankProvider.name).toBe('string')
    expect(typeof mockBankProvider.code).toBe('string')
    expect(typeof mockBankProvider.pluggy_connector_id).toBe('string')
    expect(typeof mockBankProvider.logo_url).toBe('string')
    expect(typeof mockBankProvider.is_active).toBe('boolean')
    expect(typeof mockBankProvider.supports_checking_account).toBe('boolean')
    expect(typeof mockBankProvider.supports_savings_account).toBe('boolean')
    expect(typeof mockBankProvider.supports_credit_card).toBe('boolean')
    expect(typeof mockBankProvider.created_at).toBe('string')
    expect(typeof mockBankProvider.updated_at).toBe('string')
  })

  it('should define BankAccount interface correctly', () => {
    const mockBankAccount = {
      id: 1,
      company: 1,
      bank_provider: {
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
      },
      pluggy_item_id: 'item_123',
      pluggy_account_id: 'account_456',
      account_type: 'CHECKING' as const,
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

    expect(mockBankAccount).toHaveProperty('id')
    expect(mockBankAccount).toHaveProperty('company')
    expect(mockBankAccount).toHaveProperty('bank_provider')
    expect(mockBankAccount).toHaveProperty('pluggy_item_id')
    expect(mockBankAccount).toHaveProperty('pluggy_account_id')
    expect(mockBankAccount).toHaveProperty('account_type')
    expect(mockBankAccount).toHaveProperty('name')
    expect(mockBankAccount).toHaveProperty('agency')
    expect(mockBankAccount).toHaveProperty('account_number')
    expect(mockBankAccount).toHaveProperty('balance')
    expect(mockBankAccount).toHaveProperty('is_active')
    expect(mockBankAccount).toHaveProperty('last_sync')
    expect(mockBankAccount).toHaveProperty('transactions_count')
    expect(mockBankAccount).toHaveProperty('created_at')
    expect(mockBankAccount).toHaveProperty('updated_at')

    // Test nested bank_provider
    expect(mockBankAccount.bank_provider).toHaveProperty('id')
    expect(mockBankAccount.bank_provider).toHaveProperty('name')
    expect(mockBankAccount.bank_provider).toHaveProperty('code')
  })

  it('should define Transaction interface correctly', () => {
    const mockTransaction = {
      id: 1,
      bank_account: 1,
      bank_account_details: {
        name: 'Conta Corrente Principal',
        bank_provider_name: 'Banco do Brasil',
        account_type: 'CHECKING' as const
      },
      pluggy_transaction_id: 'txn_789',
      transaction_type: 'DEBIT' as const,
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

    expect(mockTransaction).toHaveProperty('id')
    expect(mockTransaction).toHaveProperty('bank_account')
    expect(mockTransaction).toHaveProperty('bank_account_details')
    expect(mockTransaction).toHaveProperty('pluggy_transaction_id')
    expect(mockTransaction).toHaveProperty('transaction_type')
    expect(mockTransaction).toHaveProperty('amount')
    expect(mockTransaction).toHaveProperty('description')
    expect(mockTransaction).toHaveProperty('transaction_date')
    expect(mockTransaction).toHaveProperty('posted_date')
    expect(mockTransaction).toHaveProperty('category')
    expect(mockTransaction).toHaveProperty('subcategory')
    expect(mockTransaction).toHaveProperty('is_pending')
    expect(mockTransaction).toHaveProperty('created_at')
    expect(mockTransaction).toHaveProperty('updated_at')

    // Test bank_account_details nested object
    expect(mockTransaction.bank_account_details).toHaveProperty('name')
    expect(mockTransaction.bank_account_details).toHaveProperty('bank_provider_name')
    expect(mockTransaction.bank_account_details).toHaveProperty('account_type')
  })

  it('should define BankAccountCreate interface correctly', () => {
    const mockCreateAccount = {
      company: 1,
      bank_provider: 1,
      pluggy_item_id: 'item_123',
      pluggy_account_id: 'account_456',
      account_type: 'CHECKING' as const,
      name: 'Nova Conta',
      agency: '1234',
      account_number: '567890',
      balance: 1000.00,
      is_active: true
    }

    expect(mockCreateAccount).toHaveProperty('company')
    expect(mockCreateAccount).toHaveProperty('bank_provider')
    expect(mockCreateAccount).toHaveProperty('pluggy_item_id')
    expect(mockCreateAccount).toHaveProperty('pluggy_account_id')
    expect(mockCreateAccount).toHaveProperty('account_type')
    expect(mockCreateAccount).toHaveProperty('name')
    expect(mockCreateAccount).toHaveProperty('agency')
    expect(mockCreateAccount).toHaveProperty('account_number')
    expect(mockCreateAccount).toHaveProperty('balance')
    expect(mockCreateAccount).toHaveProperty('is_active')
  })

  it('should define account type unions correctly', () => {
    const accountTypes = [
      'CHECKING',
      'SAVINGS',
      'CREDIT_CARD'
    ] as const

    const transactionTypes = [
      'DEBIT',
      'CREDIT'
    ] as const

    expect(accountTypes).toHaveLength(3)
    expect(transactionTypes).toHaveLength(2)
    expect(accountTypes).toContain('CHECKING')
    expect(transactionTypes).toContain('DEBIT')
  })

  it('should define filter interfaces correctly', () => {
    const bankAccountsFilter = {
      company: 1,
      bank_provider: 1,
      account_type: 'CHECKING' as const,
      is_active: true,
      search: 'Conta Corrente'
    }

    const transactionsFilter = {
      bank_account: 1,
      transaction_type: 'DEBIT' as const,
      start_date: '2023-01-01',
      end_date: '2023-01-31',
      category: 'Alimentação',
      is_pending: false,
      search: 'supermercado'
    }

    expect(bankAccountsFilter).toHaveProperty('company')
    expect(bankAccountsFilter).toHaveProperty('bank_provider')
    expect(bankAccountsFilter).toHaveProperty('account_type')
    expect(bankAccountsFilter).toHaveProperty('is_active')
    expect(bankAccountsFilter).toHaveProperty('search')

    expect(transactionsFilter).toHaveProperty('bank_account')
    expect(transactionsFilter).toHaveProperty('transaction_type')
    expect(transactionsFilter).toHaveProperty('start_date')
    expect(transactionsFilter).toHaveProperty('end_date')
    expect(transactionsFilter).toHaveProperty('category')
    expect(transactionsFilter).toHaveProperty('is_pending')
    expect(transactionsFilter).toHaveProperty('search')
  })
})