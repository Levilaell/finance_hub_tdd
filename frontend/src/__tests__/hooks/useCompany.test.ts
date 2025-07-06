/**
 * @file useCompany hook tests
 * TDD: Test first, then implement hook
 */
import { renderHook, act } from '@testing-library/react';
import { useCompany } from '@/hooks/useCompany';
import { useCompanyStore } from '@/store/company';
import type { Company, CompanyCreateData, CompanyUpdateData } from '@/types/company';

// Mock the store
jest.mock('@/store/company');
const mockedUseCompanyStore = useCompanyStore as jest.MockedFunction<typeof useCompanyStore>;

describe('useCompany', () => {
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

  const mockStoreActions = {
    fetchCompanies: jest.fn(),
    createCompany: jest.fn(),
    updateCompany: jest.fn(),
    deleteCompany: jest.fn(),
    setSelectedCompany: jest.fn(),
    setCurrentCompany: jest.fn(),
    reset: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Default mock implementation
    mockedUseCompanyStore.mockReturnValue({
      companies: [],
      selectedCompany: null,
      currentCompany: null,
      loading: false,
      error: null,
      ...mockStoreActions,
      setCompanies: jest.fn(),
      setLoading: jest.fn(),
      setError: jest.fn(),
    });
  });

  describe('state access', () => {
    it('should return companies from store', () => {
      const mockCompanies = [mockCompany];
      mockedUseCompanyStore.mockReturnValue({
        companies: mockCompanies,
        selectedCompany: null,
        currentCompany: null,
        loading: false,
        error: null,
        ...mockStoreActions,
        setCompanies: jest.fn(),
        setLoading: jest.fn(),
        setError: jest.fn(),
      });

      const { result } = renderHook(() => useCompany());

      expect(result.current.companies).toEqual(mockCompanies);
    });

    it('should return selectedCompany from store', () => {
      mockedUseCompanyStore.mockReturnValue({
        companies: [],
        selectedCompany: mockCompany,
        currentCompany: null,
        loading: false,
        error: null,
        ...mockStoreActions,
        setCompanies: jest.fn(),
        setLoading: jest.fn(),
        setError: jest.fn(),
      });

      const { result } = renderHook(() => useCompany());

      expect(result.current.selectedCompany).toEqual(mockCompany);
    });

    it('should return loading state from store', () => {
      mockedUseCompanyStore.mockReturnValue({
        companies: [],
        selectedCompany: null,
        currentCompany: null,
        loading: true,
        error: null,
        ...mockStoreActions,
        setCompanies: jest.fn(),
        setLoading: jest.fn(),
        setError: jest.fn(),
      });

      const { result } = renderHook(() => useCompany());

      expect(result.current.loading).toBe(true);
    });

    it('should return error state from store', () => {
      const mockError = 'Something went wrong';
      mockedUseCompanyStore.mockReturnValue({
        companies: [],
        selectedCompany: null,
        currentCompany: null,
        loading: false,
        error: mockError,
        ...mockStoreActions,
        setCompanies: jest.fn(),
        setLoading: jest.fn(),
        setError: jest.fn(),
      });

      const { result } = renderHook(() => useCompany());

      expect(result.current.error).toBe(mockError);
    });
  });

  describe('actions', () => {
    it('should call fetchCompanies from store', async () => {
      const { result } = renderHook(() => useCompany());

      await act(async () => {
        await result.current.fetchCompanies();
      });

      expect(mockStoreActions.fetchCompanies).toHaveBeenCalled();
    });

    it('should call fetchCompanies with parameters', async () => {
      const { result } = renderHook(() => useCompany());
      const params = { is_active: true };

      await act(async () => {
        await result.current.fetchCompanies(params);
      });

      expect(mockStoreActions.fetchCompanies).toHaveBeenCalledWith(params);
    });

    it('should call createCompany from store', async () => {
      const createData: CompanyCreateData = {
        name: 'Nova Empresa',
        legal_name: 'Nova Empresa LTDA',
        cnpj: '11.222.333/0001-99',
        company_type: 'LTDA',
        business_sector: 'Tecnologia'
      };

      mockStoreActions.createCompany.mockResolvedValue(mockCompany);

      const { result } = renderHook(() => useCompany());

      let returnedCompany: Company;
      await act(async () => {
        returnedCompany = await result.current.createCompany(createData);
      });

      expect(mockStoreActions.createCompany).toHaveBeenCalledWith(createData);
      expect(returnedCompany!).toEqual(mockCompany);
    });

    it('should call updateCompany from store', async () => {
      const updateData: CompanyUpdateData = {
        name: 'Nome Atualizado'
      };

      const updatedCompany = { ...mockCompany, ...updateData };
      mockStoreActions.updateCompany.mockResolvedValue(updatedCompany);

      const { result } = renderHook(() => useCompany());

      let returnedCompany: Company;
      await act(async () => {
        returnedCompany = await result.current.updateCompany('uuid-123', updateData);
      });

      expect(mockStoreActions.updateCompany).toHaveBeenCalledWith('uuid-123', updateData);
      expect(returnedCompany!).toEqual(updatedCompany);
    });

    it('should call deleteCompany from store', async () => {
      const { result } = renderHook(() => useCompany());

      await act(async () => {
        await result.current.deleteCompany('uuid-123');
      });

      expect(mockStoreActions.deleteCompany).toHaveBeenCalledWith('uuid-123');
    });

    it('should call setSelectedCompany from store', () => {
      const { result } = renderHook(() => useCompany());

      act(() => {
        result.current.setSelectedCompany(mockCompany);
      });

      expect(mockStoreActions.setSelectedCompany).toHaveBeenCalledWith(mockCompany);
    });

    it('should call setCurrentCompany from store', () => {
      const { result } = renderHook(() => useCompany());

      act(() => {
        result.current.setCurrentCompany(mockCompany);
      });

      expect(mockStoreActions.setCurrentCompany).toHaveBeenCalledWith(mockCompany);
    });
  });

  describe('computed values', () => {
    it('should return hasCompanies as true when companies exist', () => {
      mockedUseCompanyStore.mockReturnValue({
        companies: [mockCompany],
        selectedCompany: null,
        currentCompany: null,
        loading: false,
        error: null,
        ...mockStoreActions,
        setCompanies: jest.fn(),
        setLoading: jest.fn(),
        setError: jest.fn(),
      });

      const { result } = renderHook(() => useCompany());

      expect(result.current.hasCompanies).toBe(true);
    });

    it('should return hasCompanies as false when no companies exist', () => {
      mockedUseCompanyStore.mockReturnValue({
        companies: [],
        selectedCompany: null,
        currentCompany: null,
        loading: false,
        error: null,
        ...mockStoreActions,
        setCompanies: jest.fn(),
        setLoading: jest.fn(),
        setError: jest.fn(),
      });

      const { result } = renderHook(() => useCompany());

      expect(result.current.hasCompanies).toBe(false);
    });

    it('should return hasSelectedCompany as true when company is selected', () => {
      mockedUseCompanyStore.mockReturnValue({
        companies: [],
        selectedCompany: mockCompany,
        currentCompany: null,
        loading: false,
        error: null,
        ...mockStoreActions,
        setCompanies: jest.fn(),
        setLoading: jest.fn(),
        setError: jest.fn(),
      });

      const { result } = renderHook(() => useCompany());

      expect(result.current.hasSelectedCompany).toBe(true);
    });

    it('should return hasSelectedCompany as false when no company is selected', () => {
      const { result } = renderHook(() => useCompany());

      expect(result.current.hasSelectedCompany).toBe(false);
    });

    it('should return isLoading correctly', () => {
      mockedUseCompanyStore.mockReturnValue({
        companies: [],
        selectedCompany: null,
        currentCompany: null,
        loading: true,
        error: null,
        ...mockStoreActions,
        setCompanies: jest.fn(),
        setLoading: jest.fn(),
        setError: jest.fn(),
      });

      const { result } = renderHook(() => useCompany());

      expect(result.current.isLoading).toBe(true);
    });

    it('should return hasError correctly', () => {
      mockedUseCompanyStore.mockReturnValue({
        companies: [],
        selectedCompany: null,
        currentCompany: null,
        loading: false,
        error: 'Some error',
        ...mockStoreActions,
        setCompanies: jest.fn(),
        setLoading: jest.fn(),
        setError: jest.fn(),
      });

      const { result } = renderHook(() => useCompany());

      expect(result.current.hasError).toBe(true);
    });
  });

  describe('helper methods', () => {
    it('should find company by id', () => {
      const company1 = { ...mockCompany, id: 'uuid-1' };
      const company2 = { ...mockCompany, id: 'uuid-2' };
      
      mockedUseCompanyStore.mockReturnValue({
        companies: [company1, company2],
        selectedCompany: null,
        currentCompany: null,
        loading: false,
        error: null,
        ...mockStoreActions,
        setCompanies: jest.fn(),
        setLoading: jest.fn(),
        setError: jest.fn(),
      });

      const { result } = renderHook(() => useCompany());

      expect(result.current.findCompanyById('uuid-2')).toEqual(company2);
      expect(result.current.findCompanyById('non-existent')).toBeUndefined();
    });

    it('should check if company is selected', () => {
      mockedUseCompanyStore.mockReturnValue({
        companies: [],
        selectedCompany: mockCompany,
        currentCompany: null,
        loading: false,
        error: null,
        ...mockStoreActions,
        setCompanies: jest.fn(),
        setLoading: jest.fn(),
        setError: jest.fn(),
      });

      const { result } = renderHook(() => useCompany());

      expect(result.current.isCompanySelected('uuid-123')).toBe(true);
      expect(result.current.isCompanySelected('other-id')).toBe(false);
    });

    it('should clear selection', () => {
      const { result } = renderHook(() => useCompany());

      act(() => {
        result.current.clearSelection();
      });

      expect(mockStoreActions.setSelectedCompany).toHaveBeenCalledWith(null);
    });
  });
});