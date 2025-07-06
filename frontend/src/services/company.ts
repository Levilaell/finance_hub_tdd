/**
 * @file Company service
 * API service for company management
 */
import { apiService } from './api';
import type {
  Company,
  CompanyCreateData,
  CompanyUpdateData,
  CompanyUser,
  CompanyUserInviteData,
  SubscriptionPlan,
  Subscription,
  SubscriptionCreateData,
  SubscriptionUpdateData,
  CompanyListResponse,
  CompanyUserListResponse,
  SubscriptionPlanListResponse
} from '@/types/company';

export class CompanyService {
  /**
   * Get companies list with optional filters
   */
  async getCompanies(params?: Record<string, any>): Promise<CompanyListResponse> {
    return await apiService.get('/companies/', params);
  }

  /**
   * Get a specific company by ID
   */
  async getCompany(id: string): Promise<Company> {
    return await apiService.get(`/companies/${id}/`);
  }

  /**
   * Create a new company
   */
  async createCompany(data: CompanyCreateData): Promise<Company> {
    return await apiService.post('/companies/', data);
  }

  /**
   * Update a company
   */
  async updateCompany(id: string, data: CompanyUpdateData): Promise<Company> {
    return await apiService.patch(`/companies/${id}/`, data);
  }

  /**
   * Delete a company
   */
  async deleteCompany(id: string): Promise<void> {
    await apiService.delete(`/companies/${id}/`);
  }

  /**
   * Get company members
   */
  async getCompanyMembers(companyId: string): Promise<CompanyUserListResponse> {
    return await apiService.get(`/companies/${companyId}/members/`);
  }

  /**
   * Invite user to company
   */
  async inviteUserToCompany(companyId: string, data: CompanyUserInviteData): Promise<CompanyUser> {
    return await apiService.post(`/companies/${companyId}/members/`, data);
  }

  /**
   * Remove user from company
   */
  async removeUserFromCompany(companyId: string, memberId: string): Promise<void> {
    await apiService.delete(`/companies/${companyId}/members/${memberId}/`);
  }

  /**
   * Get available subscription plans
   */
  async getSubscriptionPlans(): Promise<SubscriptionPlanListResponse> {
    return await apiService.get('/subscription-plans/');
  }

  /**
   * Create a subscription
   */
  async createSubscription(data: SubscriptionCreateData): Promise<Subscription> {
    return await apiService.post('/subscriptions/', data);
  }

  /**
   * Update a subscription
   */
  async updateSubscription(id: string, data: SubscriptionUpdateData): Promise<Subscription> {
    return await apiService.patch(`/subscriptions/${id}/`, data);
  }
}

// Export singleton instance
export const companyService = new CompanyService();