/**
 * @file Company service tests
 * TDD: Test first, then implement service
 */
import { CompanyService } from '@/services/company';
import { apiService } from '@/services/api';
import type { 
  Company, 
  CompanyCreateData, 
  CompanyUpdateData,
  CompanyUserInviteData,
  SubscriptionCreateData,
  SubscriptionUpdateData,
  CompanyListResponse,
  CompanyUserListResponse,
  SubscriptionPlanListResponse
} from '@/types/company';

// Mock the API service
jest.mock('@/services/api');
const mockedApiService = apiService as jest.Mocked<typeof apiService>;

describe('CompanyService', () => {
  let companyService: CompanyService;

  beforeEach(() => {
    companyService = new CompanyService();
    jest.clearAllMocks();
  });

  describe('getCompanies', () => {
    it('should fetch companies list', async () => {
      // Arrange
      const mockResponse: CompanyListResponse = {
        count: 1,
        next: null,
        previous: null,
        results: [
          {
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
          }
        ]
      };
      mockedApiService.get.mockResolvedValue(mockResponse);

      // Act
      const result = await companyService.getCompanies();

      // Assert
      expect(mockedApiService.get).toHaveBeenCalledWith('/companies/', undefined);
      expect(result).toEqual(mockResponse);
    });

    it('should handle query parameters', async () => {
      // Arrange
      const mockResponse: CompanyListResponse = {
        count: 0,
        next: null,
        previous: null,
        results: []
      };
      mockedApiService.get.mockResolvedValue(mockResponse);

      // Act
      await companyService.getCompanies({ is_active: true });

      // Assert
      expect(mockedApiService.get).toHaveBeenCalledWith('/companies/', { is_active: true });
    });
  });

  describe('getCompany', () => {
    it('should fetch a specific company', async () => {
      // Arrange
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
      mockedApiService.get.mockResolvedValue(mockCompany);

      // Act
      const result = await companyService.getCompany('uuid-123');

      // Assert
      expect(mockedApiService.get).toHaveBeenCalledWith('/companies/uuid-123/');
      expect(result).toEqual(mockCompany);
    });
  });

  describe('createCompany', () => {
    it('should create a new company', async () => {
      // Arrange
      const createData: CompanyCreateData = {
        name: 'Nova Empresa',
        legal_name: 'Nova Empresa LTDA',
        cnpj: '11.222.333/0001-99',
        company_type: 'LTDA',
        business_sector: 'Tecnologia'
      };

      const mockCreatedCompany: Company = {
        id: 'uuid-456',
        ...createData,
        slug: 'nova-empresa',
        is_active: true,
        subscription: null,
        members_count: 1,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      };

      mockedApiService.post.mockResolvedValue(mockCreatedCompany);

      // Act
      const result = await companyService.createCompany(createData);

      // Assert
      expect(mockedApiService.post).toHaveBeenCalledWith('/companies/', createData);
      expect(result).toEqual(mockCreatedCompany);
    });
  });

  describe('updateCompany', () => {
    it('should update a company', async () => {
      // Arrange
      const updateData: CompanyUpdateData = {
        name: 'Nome Atualizado',
        business_sector: 'Financeiro'
      };

      const mockUpdatedCompany: Company = {
        id: 'uuid-123',
        name: 'Nome Atualizado',
        legal_name: 'Test Company LTDA',
        slug: 'test-company',
        cnpj: '11.222.333/0001-80',
        company_type: 'LTDA',
        business_sector: 'Financeiro',
        is_active: true,
        subscription: null,
        members_count: 1,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      };

      mockedApiService.patch.mockResolvedValue(mockUpdatedCompany);

      // Act
      const result = await companyService.updateCompany('uuid-123', updateData);

      // Assert
      expect(mockedApiService.patch).toHaveBeenCalledWith('/companies/uuid-123/', updateData);
      expect(result).toEqual(mockUpdatedCompany);
    });
  });

  describe('deleteCompany', () => {
    it('should delete a company', async () => {
      // Arrange
      mockedApiService.delete.mockResolvedValue(null);

      // Act
      await companyService.deleteCompany('uuid-123');

      // Assert
      expect(mockedApiService.delete).toHaveBeenCalledWith('/companies/uuid-123/');
    });
  });
});