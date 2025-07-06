/**
 * Types for Banking module
 * Based on Django backend models and serializers
 */

// Account types
export type AccountType = 'CHECKING' | 'SAVINGS' | 'CREDIT_CARD'

// Transaction types
export type TransactionType = 'DEBIT' | 'CREDIT'

// Bank Provider interface (from BankProviderSerializer)
export interface BankProvider {
  id: number
  name: string
  code: string
  pluggy_connector_id: string
  logo_url: string
  is_active: boolean
  supports_checking_account: boolean
  supports_savings_account: boolean
  supports_credit_card: boolean
  created_at: string
  updated_at: string
}

// Bank Account Details for nested display
export interface BankAccountDetails {
  name: string
  bank_provider_name: string
  account_type: AccountType
}

// Bank Account interface (from BankAccountSerializer)
export interface BankAccount {
  id: number
  company: number
  bank_provider: BankProvider
  pluggy_item_id: string
  pluggy_account_id: string
  account_type: AccountType
  name: string
  agency: string
  account_number: string
  balance: number
  is_active: boolean
  last_sync: string | null
  transactions_count: number
  created_at: string
  updated_at: string
}

// Bank Account creation interface (from BankAccountCreateSerializer)
export interface BankAccountCreate {
  company: number
  bank_provider: number
  pluggy_item_id: string
  pluggy_account_id: string
  account_type: AccountType
  name: string
  agency?: string
  account_number?: string
  balance?: number
  is_active?: boolean
}

// Bank Account update interface
export interface BankAccountUpdate {
  name?: string
  agency?: string
  account_number?: string
  balance?: number
  is_active?: boolean
}

// Transaction interface (from TransactionSerializer)
export interface Transaction {
  id: number
  bank_account: number
  bank_account_details: BankAccountDetails
  pluggy_transaction_id: string
  transaction_type: TransactionType
  amount: number
  description: string
  transaction_date: string
  posted_date: string | null
  category: string
  subcategory: string
  is_pending: boolean
  created_at: string
  updated_at: string
}

// Transaction creation interface
export interface TransactionCreate {
  bank_account: number
  pluggy_transaction_id: string
  transaction_type: TransactionType
  amount: number
  description: string
  transaction_date: string
  posted_date?: string | null
  category?: string
  subcategory?: string
  is_pending?: boolean
}

// Transaction update interface
export interface TransactionUpdate {
  description?: string
  category?: string
  subcategory?: string
  is_pending?: boolean
}

// API Response types
export interface BankProvidersResponse {
  count: number
  next: string | null
  previous: string | null
  results: BankProvider[]
}

export interface BankAccountsResponse {
  count: number
  next: string | null
  previous: string | null
  results: BankAccount[]
}

export interface TransactionsResponse {
  count: number
  next: string | null
  previous: string | null
  results: Transaction[]
}

// Filter interfaces
export interface BankProvidersFilter {
  is_active?: boolean
  supports_checking_account?: boolean
  supports_savings_account?: boolean
  supports_credit_card?: boolean
  search?: string
}

export interface BankAccountsFilter {
  company?: number
  bank_provider?: number
  account_type?: AccountType
  is_active?: boolean
  search?: string
  page?: number
}

export interface TransactionsFilter {
  bank_account?: number
  transaction_type?: TransactionType
  start_date?: string
  end_date?: string
  category?: string
  subcategory?: string
  is_pending?: boolean
  search?: string
  page?: number
}

// Sort options
export type BankProvidersSortField = 'name' | 'code' | 'created_at'
export type BankAccountsSortField = 'name' | 'balance' | 'last_sync' | 'created_at'
export type TransactionsSortField = 'transaction_date' | 'amount' | 'description' | 'created_at'

// Display options for dropdowns/selects
export interface AccountTypeOption {
  value: AccountType
  label: string
}

export interface TransactionTypeOption {
  value: TransactionType
  label: string
}

// Constants for dropdowns
export const ACCOUNT_TYPE_OPTIONS: AccountTypeOption[] = [
  { value: 'CHECKING', label: 'Conta Corrente' },
  { value: 'SAVINGS', label: 'Conta Poupança' },
  { value: 'CREDIT_CARD', label: 'Cartão de Crédito' }
]

export const TRANSACTION_TYPE_OPTIONS: TransactionTypeOption[] = [
  { value: 'DEBIT', label: 'Débito' },
  { value: 'CREDIT', label: 'Crédito' }
]

// Connection interfaces for Pluggy integration
export interface BankConnection {
  item_id: string
  connector_id: string
  status: 'UPDATED' | 'OUTDATED' | 'LOGIN_ERROR' | 'WAITING_USER_INPUT'
  created_at: string
  updated_at: string
}

export interface ConnectBankRequest {
  company: number
  connector_id: string
  credentials: Record<string, any>
}

export interface SyncAccountsRequest {
  company: number
  item_id: string
}

// Dashboard/Summary interfaces
export interface AccountSummary {
  total_accounts: number
  total_balance: number
  checking_accounts: number
  savings_accounts: number
  credit_cards: number
  last_sync: string | null
}

export interface TransactionSummary {
  total_transactions: number
  total_credits: number
  total_debits: number
  pending_transactions: number
  period_start: string
  period_end: string
}

// Utility types
export interface BankAccountOption {
  value: number
  label: string
  bank_provider: string
  account_type: AccountType
  balance: number
}

// Error types
export interface BankingError {
  field: string
  message: string
}

export interface PluggyError {
  code: string
  message: string
  parameter?: string
}

// Export all types
export type {
  BankProvider,
  BankAccount,
  Transaction,
  BankAccountCreate,
  BankAccountUpdate,
  TransactionCreate,
  TransactionUpdate,
  BankProvidersResponse,
  BankAccountsResponse,
  TransactionsResponse,
  BankProvidersFilter,
  BankAccountsFilter,
  TransactionsFilter,
  BankConnection,
  ConnectBankRequest,
  SyncAccountsRequest,
  AccountSummary,
  TransactionSummary,
  BankAccountOption,
  BankingError,
  PluggyError
}