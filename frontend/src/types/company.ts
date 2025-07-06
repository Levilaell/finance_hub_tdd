/**
 * @file Company related types
 * Types for company management, subscriptions, and user roles
 */

// User basic info for company context
export interface UserBasic {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
}

// Company user roles
export type CompanyUserRole = 'owner' | 'admin' | 'member' | 'viewer';

// Company user relationship
export interface CompanyUser {
  id: string;
  role: CompanyUserRole;
  is_active: boolean;
  joined_at: string;
  user: UserBasic;
}

// Subscription plan
export interface SubscriptionPlan {
  id: string;
  name: string;
  slug: string;
  description?: string;
  price: string; // Decimal as string from API
  max_companies: number;
  max_bank_accounts: number;
  max_transactions_per_month: number;
  features: string[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Subscription status
export type SubscriptionStatus = 'trial' | 'active' | 'past_due' | 'cancelled' | 'expired';

// Subscription
export interface Subscription {
  id: string;
  status: SubscriptionStatus;
  trial_days: number;
  started_at: string;
  next_billing_date: string | null;
  cancelled_at: string | null;
  created_at: string;
  updated_at: string;
  plan: SubscriptionPlan;
}

// Company types
export type CompanyType = 'MEI' | 'LTDA' | 'SA' | 'EIRELI' | 'SLU';

// Main company interface
export interface Company {
  id: string;
  name: string;
  legal_name: string;
  slug: string;
  cnpj: string;
  company_type: CompanyType;
  business_sector: string;
  website?: string;
  phone?: string;
  email?: string;
  is_active: boolean;
  subscription: Subscription | null;
  members_count: number;
  created_at: string;
  updated_at: string;
}

// Data for creating a new company
export interface CompanyCreateData {
  name: string;
  legal_name: string;
  cnpj: string;
  company_type: CompanyType;
  business_sector: string;
  website?: string;
  phone?: string;
  email?: string;
}

// Data for updating a company (all fields optional)
export interface CompanyUpdateData {
  name?: string;
  legal_name?: string;
  cnpj?: string;
  company_type?: CompanyType;
  business_sector?: string;
  website?: string;
  phone?: string;
  email?: string;
}

// Company user invitation data
export interface CompanyUserInviteData {
  email: string;
  role: CompanyUserRole;
}

// Subscription creation data
export interface SubscriptionCreateData {
  company_id: string;
  plan_id: string;
  status?: SubscriptionStatus;
  trial_days?: number;
}

// Subscription update data
export interface SubscriptionUpdateData {
  status?: SubscriptionStatus;
  trial_days?: number;
}

// API response types
export interface CompanyListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Company[];
}

export interface CompanyUserListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: CompanyUser[];
}

export interface SubscriptionPlanListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: SubscriptionPlan[];
}