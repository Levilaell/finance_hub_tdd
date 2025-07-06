/**
 * @file Company store tests
 * TDD: Test first, then implement store
 */
import { useCompanyStore } from '@/store/company';
import { companyService } from '@/services/company';
import type { Company, CompanyCreateData, CompanyUpdateData } from '@/types/company';

// Mock the company service
jest.mock('@/services/company');
const mockedCompanyService = companyService as jest.Mocked<typeof companyService>;

describe('CompanyStore', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset store state
    useCompanyStore.getState().reset();
  });

  describe('initial state', () => {
    it('should have correct initial state', () => {
      const state = useCompanyStore.getState();
      
      expect(state.companies).toEqual([]);
      expect(state.selectedCompany).toBeNull();
      expect(state.currentCompany).toBeNull();
      expect(state.loading).toBe(false);
      expect(state.error).toBeNull();
    });
  });

  describe('setSelectedCompany', () => {
    it('should set selected company', () => {
      const mockCompany: Company = {
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

      const { setSelectedCompany } = useCompanyStore.getState();
      setSelectedCompany(mockCompany);

      const state = useCompanyStore.getState();
      expect(state.selectedCompany).toEqual(mockCompany);
    });

    it('should set selected company to null', () => {
      const { setSelectedCompany } = useCompanyStore.getState();
      setSelectedCompany(null);

      const state = useCompanyStore.getState();
      expect(state.selectedCompany).toBeNull();
    });
  });

  describe('setCurrentCompany', () => {
    it('should set current company', () => {
      const mockCompany: Company = {
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

      const { setCurrentCompany } = useCompanyStore.getState();
      setCurrentCompany(mockCompany);

      const state = useCompanyStore.getState();
      expect(state.currentCompany).toEqual(mockCompany);
    });
  });

  describe('fetchCompanies', () => {
    it('should fetch companies successfully', async () => {
      // Arrange
      const mockCompanies = [
        {
          id: 'uuid-123',
          name: 'Test Company 1',
          legal_name: 'Test Company 1 LTDA',
          slug: 'test-company-1',
          cnpj: '11.222.333/0001-80',
          company_type: 'LTDA' as const,
          business_sector: 'Tecnologia',
          is_active: true,
          subscription: null,
          members_count: 1,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        },
        {
          id: 'uuid-456',
          name: 'Test Company 2',
          legal_name: 'Test Company 2 LTDA',
          slug: 'test-company-2',
          cnpj: '11.222.333/0001-81',
          company_type: 'LTDA' as const,
          business_sector: 'Financeiro',
          is_active: true,
          subscription: null,
          members_count: 2,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        }
      ];

      const mockResponse = {
        count: 2,
        next: null,
        previous: null,
        results: mockCompanies
      };

      mockedCompanyService.getCompanies.mockResolvedValue(mockResponse);

      // Act
      const { fetchCompanies } = useCompanyStore.getState();
      await fetchCompanies();

      // Assert
      const state = useCompanyStore.getState();
      expect(state.companies).toEqual(mockCompanies);
      expect(state.loading).toBe(false);
      expect(state.error).toBeNull();
      expect(mockedCompanyService.getCompanies).toHaveBeenCalled();
    });

    it('should handle fetch companies error', async () => {
      // Arrange
      const mockError = new Error('Network error');
      mockedCompanyService.getCompanies.mockRejectedValue(mockError);

      // Act
      const { fetchCompanies } = useCompanyStore.getState();
      await fetchCompanies();

      // Assert
      const state = useCompanyStore.getState();
      expect(state.companies).toEqual([]);
      expect(state.loading).toBe(false);
      expect(state.error).toBe('Network error');
    });

    it('should set loading state during fetch', async () => {
      // Arrange
      let resolvePromise: (value: any) => void;
      const promise = new Promise((resolve) => {
        resolvePromise = resolve;
      });
      mockedCompanyService.getCompanies.mockReturnValue(promise);

      // Act
      const { fetchCompanies } = useCompanyStore.getState();
      const fetchPromise = fetchCompanies();

      // Assert - loading should be true during fetch
      let state = useCompanyStore.getState();
      expect(state.loading).toBe(true);

      // Complete the promise
      resolvePromise!({
        count: 0,
        next: null,
        previous: null,
        results: []
      });
      await fetchPromise;

      // Assert - loading should be false after fetch
      state = useCompanyStore.getState();
      expect(state.loading).toBe(false);
    });
  });

  describe('createCompany', () => {
    it('should create company successfully', async () => {
      // Arrange
      const createData: CompanyCreateData = {
        name: 'Nova Empresa',
        legal_name: 'Nova Empresa LTDA',
        cnpj: '11.222.333/0001-99',
        company_type: 'LTDA',
        business_sector: 'Tecnologia'
      };

      const mockCreatedCompany: Company = {
        id: 'uuid-789',
        ...createData,
        slug: 'nova-empresa',
        is_active: true,
        subscription: null,
        members_count: 1,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      };

      mockedCompanyService.createCompany.mockResolvedValue(mockCreatedCompany);

      // Act
      const { createCompany } = useCompanyStore.getState();
      const result = await createCompany(createData);

      // Assert
      expect(result).toEqual(mockCreatedCompany);
      expect(mockedCompanyService.createCompany).toHaveBeenCalledWith(createData);
      
      const state = useCompanyStore.getState();
      expect(state.companies).toContain(mockCreatedCompany);
      expect(state.error).toBeNull();
    });

    it('should handle create company error', async () => {
      // Arrange
      const createData: CompanyCreateData = {
        name: 'Nova Empresa',
        legal_name: 'Nova Empresa LTDA',
        cnpj: '11.222.333/0001-99',
        company_type: 'LTDA',
        business_sector: 'Tecnologia'
      };

      const mockError = new Error('CNPJ já existe');
      mockedCompanyService.createCompany.mockRejectedValue(mockError);

      // Act
      const { createCompany } = useCompanyStore.getState();
      await expect(createCompany(createData)).rejects.toThrow('CNPJ já existe');

      // Assert
      const state = useCompanyStore.getState();
      expect(state.error).toBe('CNPJ já existe');
    });
  });

  describe('updateCompany', () => {
    it('should update company successfully', async () => {
      // Arrange
      const existingCompany: Company = {
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

      // Set existing company in store
      const { setCompanies } = useCompanyStore.getState();
      setCompanies([existingCompany]);

      const updateData: CompanyUpdateData = {
        name: 'Nome Atualizado',
        business_sector: 'Financeiro'
      };

      const mockUpdatedCompany: Company = {
        ...existingCompany,
        ...updateData,
        updated_at: '2024-01-02T00:00:00Z'
      };

      mockedCompanyService.updateCompany.mockResolvedValue(mockUpdatedCompany);

      // Act
      const { updateCompany } = useCompanyStore.getState();
      const result = await updateCompany('uuid-123', updateData);

      // Assert
      expect(result).toEqual(mockUpdatedCompany);
      expect(mockedCompanyService.updateCompany).toHaveBeenCalledWith('uuid-123', updateData);
      
      const state = useCompanyStore.getState();
      expect(state.companies[0]).toEqual(mockUpdatedCompany);
      expect(state.error).toBeNull();
    });

    it('should handle update company error', async () => {
      // Arrange
      const updateData: CompanyUpdateData = {
        name: 'Nome Atualizado'
      };

      const mockError = new Error('Company not found');
      mockedCompanyService.updateCompany.mockRejectedValue(mockError);

      // Act
      const { updateCompany } = useCompanyStore.getState();
      await expect(updateCompany('uuid-123', updateData)).rejects.toThrow('Company not found');

      // Assert
      const state = useCompanyStore.getState();
      expect(state.error).toBe('Company not found');
    });
  });

  describe('deleteCompany', () => {
    it('should delete company successfully', async () => {
      // Arrange
      const existingCompany: Company = {
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

      // Set existing company in store
      const { setCompanies } = useCompanyStore.getState();
      setCompanies([existingCompany]);

      mockedCompanyService.deleteCompany.mockResolvedValue();

      // Act
      const { deleteCompany } = useCompanyStore.getState();
      await deleteCompany('uuid-123');

      // Assert
      expect(mockedCompanyService.deleteCompany).toHaveBeenCalledWith('uuid-123');
      
      const state = useCompanyStore.getState();
      expect(state.companies).toEqual([]);
      expect(state.error).toBeNull();
    });

    it('should handle delete company error', async () => {
      // Arrange
      const mockError = new Error('Cannot delete company');
      mockedCompanyService.deleteCompany.mockRejectedValue(mockError);

      // Act
      const { deleteCompany } = useCompanyStore.getState();
      await expect(deleteCompany('uuid-123')).rejects.toThrow('Cannot delete company');

      // Assert
      const state = useCompanyStore.getState();
      expect(state.error).toBe('Cannot delete company');
    });
  });
});