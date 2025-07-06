/**
 * @file Company types tests
 * TDD: Test first, then implement types
 */
import { Company, CompanyUser, SubscriptionPlan, Subscription, CompanyCreateData, CompanyUpdateData } from '@/types/company';

describe('Company Types', () => {
  describe('Company', () => {
    it('should have all required properties', () => {
      const company: Company = {
        id: 'uuid-123',
        name: 'Test Company',
        legal_name: 'Test Company LTDA',
        slug: 'test-company',
        cnpj: '11.222.333/0001-80',
        company_type: 'LTDA',
        business_sector: 'Tecnologia',
        website: 'https://test.com',
        phone: '+5511999999999',
        email: 'contact@test.com',
        is_active: true,
        subscription: null,
        members_count: 1,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      };

      expect(company.id).toBe('uuid-123');
      expect(company.name).toBe('Test Company');
      expect(company.cnpj).toBe('11.222.333/0001-80');
      expect(company.is_active).toBe(true);
      expect(company.subscription).toBeNull();
    });

    it('should allow optional fields to be undefined', () => {
      const company: Company = {
        id: 'uuid-123',
        name: 'Test Company',
        legal_name: 'Test Company LTDA',
        slug: 'test-company',
        cnpj: '11.222.333/0001-80',
        company_type: 'LTDA',
        business_sector: 'Tecnologia',
        is_active: true,
        subscription: null,
        members_count: 1,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      };

      expect(company.website).toBeUndefined();
      expect(company.phone).toBeUndefined();
      expect(company.email).toBeUndefined();
    });

    it('should support company with subscription', () => {
      const subscription: Subscription = {
        id: 'sub-123',
        status: 'active',
        trial_days: 0,
        started_at: '2024-01-01T00:00:00Z',
        next_billing_date: '2024-02-01T00:00:00Z',
        cancelled_at: null,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        plan: {
          id: 'plan-123',
          name: 'Pro',
          slug: 'pro',
          description: 'Plano profissional',
          price: '59.90',
          max_companies: 3,
          max_bank_accounts: 10,
          max_transactions_per_month: 10000,
          features: ['basic_reports', 'advanced_reports'],
          is_active: true,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        }
      };

      const company: Company = {
        id: 'uuid-123',
        name: 'Test Company',
        legal_name: 'Test Company LTDA',
        slug: 'test-company',
        cnpj: '11.222.333/0001-80',
        company_type: 'LTDA',
        business_sector: 'Tecnologia',
        is_active: true,
        subscription,
        members_count: 1,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      };

      expect(company.subscription).toBe(subscription);
      expect(company.subscription?.plan.name).toBe('Pro');
    });
  });

  describe('CompanyUser', () => {
    it('should have all required properties', () => {
      const companyUser: CompanyUser = {
        id: 'cu-123',
        role: 'admin',
        is_active: true,
        joined_at: '2024-01-01T00:00:00Z',
        user: {
          id: 'user-123',
          email: 'admin@test.com',
          first_name: 'Admin',
          last_name: 'User'
        }
      };

      expect(companyUser.id).toBe('cu-123');
      expect(companyUser.role).toBe('admin');
      expect(companyUser.user.email).toBe('admin@test.com');
    });

    it('should support different roles', () => {
      const roles: CompanyUser['role'][] = ['owner', 'admin', 'member', 'viewer'];
      
      roles.forEach(role => {
        const companyUser: CompanyUser = {
          id: 'cu-123',
          role,
          is_active: true,
          joined_at: '2024-01-01T00:00:00Z',
          user: {
            id: 'user-123',
            email: 'test@test.com',
            first_name: 'Test',
            last_name: 'User'
          }
        };

        expect(companyUser.role).toBe(role);
      });
    });
  });

  describe('SubscriptionPlan', () => {
    it('should have all required properties', () => {
      const plan: SubscriptionPlan = {
        id: 'plan-123',
        name: 'Starter',
        slug: 'starter',
        description: 'Plano inicial',
        price: '29.90',
        max_companies: 1,
        max_bank_accounts: 5,
        max_transactions_per_month: 1000,
        features: ['basic_reports'],
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      };

      expect(plan.name).toBe('Starter');
      expect(plan.price).toBe('29.90');
      expect(plan.max_companies).toBe(1);
      expect(plan.features).toContain('basic_reports');
    });

    it('should allow optional description', () => {
      const plan: SubscriptionPlan = {
        id: 'plan-123',
        name: 'Starter',
        slug: 'starter',
        price: '29.90',
        max_companies: 1,
        max_bank_accounts: 5,
        max_transactions_per_month: 1000,
        features: ['basic_reports'],
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      };

      expect(plan.description).toBeUndefined();
    });
  });

  describe('Subscription', () => {
    it('should have all required properties', () => {
      const subscription: Subscription = {
        id: 'sub-123',
        status: 'trial',
        trial_days: 14,
        started_at: '2024-01-01T00:00:00Z',
        next_billing_date: null,
        cancelled_at: null,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        plan: {
          id: 'plan-123',
          name: 'Pro',
          slug: 'pro',
          price: '59.90',
          max_companies: 3,
          max_bank_accounts: 10,
          max_transactions_per_month: 10000,
          features: ['basic_reports', 'advanced_reports'],
          is_active: true,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        }
      };

      expect(subscription.status).toBe('trial');
      expect(subscription.trial_days).toBe(14);
      expect(subscription.plan.name).toBe('Pro');
    });

    it('should support different statuses', () => {
      const statuses: Subscription['status'][] = ['trial', 'active', 'past_due', 'cancelled', 'expired'];
      
      statuses.forEach(status => {
        const subscription: Subscription = {
          id: 'sub-123',
          status,
          trial_days: 0,
          started_at: '2024-01-01T00:00:00Z',
          next_billing_date: null,
          cancelled_at: null,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          plan: {
            id: 'plan-123',
            name: 'Pro',
            slug: 'pro',
            price: '59.90',
            max_companies: 3,
            max_bank_accounts: 10,
            max_transactions_per_month: 10000,
            features: ['basic_reports'],
            is_active: true,
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z'
          }
        };

        expect(subscription.status).toBe(status);
      });
    });
  });

  describe('CompanyCreateData', () => {
    it('should have required fields for creation', () => {
      const createData: CompanyCreateData = {
        name: 'Nova Empresa',
        legal_name: 'Nova Empresa LTDA',
        cnpj: '11.222.333/0001-99',
        company_type: 'LTDA',
        business_sector: 'Tecnologia'
      };

      expect(createData.name).toBe('Nova Empresa');
      expect(createData.cnpj).toBe('11.222.333/0001-99');
    });

    it('should allow optional fields', () => {
      const createData: CompanyCreateData = {
        name: 'Nova Empresa',
        legal_name: 'Nova Empresa LTDA',
        cnpj: '11.222.333/0001-99',
        company_type: 'LTDA',
        business_sector: 'Tecnologia',
        website: 'https://nova.com',
        phone: '+5511888888888',
        email: 'contato@nova.com'
      };

      expect(createData.website).toBe('https://nova.com');
      expect(createData.phone).toBe('+5511888888888');
      expect(createData.email).toBe('contato@nova.com');
    });
  });

  describe('CompanyUpdateData', () => {
    it('should allow partial updates', () => {
      const updateData: CompanyUpdateData = {
        name: 'Nome Atualizado'
      };

      expect(updateData.name).toBe('Nome Atualizado');
      expect(updateData.cnpj).toBeUndefined();
    });

    it('should allow updating multiple fields', () => {
      const updateData: CompanyUpdateData = {
        name: 'Nome Atualizado',
        business_sector: 'Financeiro',
        website: 'https://atualizada.com'
      };

      expect(updateData.name).toBe('Nome Atualizado');
      expect(updateData.business_sector).toBe('Financeiro');
      expect(updateData.website).toBe('https://atualizada.com');
    });
  });
});