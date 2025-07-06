/**
 * @file CompanySelector component tests
 * TDD: Test first, then implement component
 */
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { CompanySelector } from '@/components/CompanySelector';
import { useCompany } from '@/hooks/useCompany';
import type { Company } from '@/types/company';

// Mock the useCompany hook
jest.mock('@/hooks/useCompany');
const mockedUseCompany = useCompany as jest.MockedFunction<typeof useCompany>;

describe('CompanySelector', () => {
  const mockCompany1: Company = {
    id: 'uuid-123',
    name: 'Test Company 1',
    legal_name: 'Test Company 1 LTDA',
    slug: 'test-company-1',
    cnpj: '11.222.333/0001-80',
    company_type: 'LTDA',
    business_sector: 'Tecnologia',
    is_active: true,
    subscription: null,
    members_count: 1,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z'
  };

  const mockCompany2: Company = {
    id: 'uuid-456',
    name: 'Test Company 2',
    legal_name: 'Test Company 2 LTDA',
    slug: 'test-company-2',
    cnpj: '11.222.333/0001-81',
    company_type: 'LTDA',
    business_sector: 'Financeiro',
    is_active: true,
    subscription: null,
    members_count: 2,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z'
  };

  const mockUseCompanyReturn = {
    companies: [],
    selectedCompany: null,
    currentCompany: null,
    loading: false,
    error: null,
    hasCompanies: false,
    hasSelectedCompany: false,
    isLoading: false,
    hasError: false,
    fetchCompanies: jest.fn(),
    createCompany: jest.fn(),
    updateCompany: jest.fn(),
    deleteCompany: jest.fn(),
    setSelectedCompany: jest.fn(),
    setCurrentCompany: jest.fn(),
    findCompanyById: jest.fn(),
    isCompanySelected: jest.fn(),
    clearSelection: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockedUseCompany.mockReturnValue(mockUseCompanyReturn);
  });

  describe('basic rendering', () => {
    it('should render with no companies message when no companies exist', () => {
      render(<CompanySelector />);
      
      expect(screen.getByText('Selecionar Empresa')).toBeInTheDocument();
      
      // Open dropdown to see the message
      fireEvent.click(screen.getByText('Selecionar Empresa'));
      expect(screen.getByText('Nenhuma empresa encontrada')).toBeInTheDocument();
    });

    it('should render with companies when they exist', () => {
      mockedUseCompany.mockReturnValue({
        ...mockUseCompanyReturn,
        companies: [mockCompany1, mockCompany2],
        hasCompanies: true,
      });

      render(<CompanySelector />);
      
      expect(screen.getByText('Selecionar Empresa')).toBeInTheDocument();
      expect(screen.queryByText('Nenhuma empresa encontrada')).not.toBeInTheDocument();
    });

    it('should show selected company when one is selected', () => {
      mockedUseCompany.mockReturnValue({
        ...mockUseCompanyReturn,
        companies: [mockCompany1, mockCompany2],
        selectedCompany: mockCompany1,
        hasCompanies: true,
        hasSelectedCompany: true,
      });

      render(<CompanySelector />);
      
      expect(screen.getByText('Test Company 1')).toBeInTheDocument();
    });

    it('should show loading state', () => {
      mockedUseCompany.mockReturnValue({
        ...mockUseCompanyReturn,
        loading: true,
        isLoading: true,
      });

      render(<CompanySelector />);
      
      expect(screen.getByText('Carregando...')).toBeInTheDocument();
    });

    it('should show error state', () => {
      mockedUseCompany.mockReturnValue({
        ...mockUseCompanyReturn,
        error: 'Erro ao carregar empresas',
        hasError: true,
      });

      render(<CompanySelector />);
      
      expect(screen.getByText('Erro: Erro ao carregar empresas')).toBeInTheDocument();
    });
  });

  describe('interactions', () => {
    it('should call fetchCompanies on mount', () => {
      render(<CompanySelector />);
      
      expect(mockUseCompanyReturn.fetchCompanies).toHaveBeenCalled();
    });

    it('should call setSelectedCompany when company is clicked', async () => {
      mockedUseCompany.mockReturnValue({
        ...mockUseCompanyReturn,
        companies: [mockCompany1, mockCompany2],
        hasCompanies: true,
      });

      render(<CompanySelector />);
      
      // Open dropdown
      fireEvent.click(screen.getByText('Selecionar Empresa'));
      
      // Click on company
      fireEvent.click(screen.getByText('Test Company 1'));
      
      expect(mockUseCompanyReturn.setSelectedCompany).toHaveBeenCalledWith(mockCompany1);
    });

    it('should toggle dropdown when trigger is clicked', () => {
      mockedUseCompany.mockReturnValue({
        ...mockUseCompanyReturn,
        companies: [mockCompany1, mockCompany2],
        hasCompanies: true,
      });

      render(<CompanySelector />);
      
      // Initially closed
      expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
      
      // Open dropdown
      fireEvent.click(screen.getByText('Selecionar Empresa'));
      expect(screen.getByRole('listbox')).toBeInTheDocument();
      
      // Close dropdown
      fireEvent.click(screen.getByText('Selecionar Empresa'));
      expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
    });

    it('should close dropdown when clicking outside', async () => {
      mockedUseCompany.mockReturnValue({
        ...mockUseCompanyReturn,
        companies: [mockCompany1, mockCompany2],
        hasCompanies: true,
      });

      render(<CompanySelector />);
      
      // Open dropdown
      fireEvent.click(screen.getByText('Selecionar Empresa'));
      expect(screen.getByRole('listbox')).toBeInTheDocument();
      
      // Click outside
      fireEvent.mouseDown(document.body);
      
      await waitFor(() => {
        expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
      });
    });

    it('should show company details in dropdown', () => {
      mockedUseCompany.mockReturnValue({
        ...mockUseCompanyReturn,
        companies: [mockCompany1, mockCompany2],
        hasCompanies: true,
      });

      render(<CompanySelector />);
      
      // Open dropdown
      fireEvent.click(screen.getByText('Selecionar Empresa'));
      
      // Check company details
      expect(screen.getByText('Test Company 1')).toBeInTheDocument();
      expect(screen.getByText('Test Company 2')).toBeInTheDocument();
      expect(screen.getByText('11.222.333/0001-80')).toBeInTheDocument();
      expect(screen.getByText('11.222.333/0001-81')).toBeInTheDocument();
    });
  });

  describe('custom props', () => {
    it('should apply custom className', () => {
      const { container } = render(<CompanySelector className="custom-class" />);
      
      expect(container.firstChild).toHaveClass('custom-class');
    });

    it('should call onSelect callback when provided', () => {
      const onSelectMock = jest.fn();
      
      mockedUseCompany.mockReturnValue({
        ...mockUseCompanyReturn,
        companies: [mockCompany1],
        hasCompanies: true,
      });

      render(<CompanySelector onSelect={onSelectMock} />);
      
      // Open dropdown
      fireEvent.click(screen.getByText('Selecionar Empresa'));
      
      // Click on company
      fireEvent.click(screen.getByText('Test Company 1'));
      
      expect(onSelectMock).toHaveBeenCalledWith(mockCompany1);
    });

    it('should use custom placeholder', () => {
      render(<CompanySelector placeholder="Escolha uma empresa" />);
      
      expect(screen.getByText('Escolha uma empresa')).toBeInTheDocument();
    });

    it('should be disabled when disabled prop is true', () => {
      render(<CompanySelector disabled />);
      
      const trigger = screen.getByRole('button');
      expect(trigger).toBeDisabled();
    });
  });

  describe('accessibility', () => {
    it('should have proper ARIA attributes', () => {
      render(<CompanySelector />);
      
      const trigger = screen.getByRole('button');
      expect(trigger).toHaveAttribute('aria-haspopup', 'listbox');
      expect(trigger).toHaveAttribute('aria-expanded', 'false');
    });

    it('should update aria-expanded when dropdown is opened', () => {
      mockedUseCompany.mockReturnValue({
        ...mockUseCompanyReturn,
        companies: [mockCompany1],
        hasCompanies: true,
      });

      render(<CompanySelector />);
      
      const trigger = screen.getByRole('button');
      
      // Open dropdown
      fireEvent.click(trigger);
      expect(trigger).toHaveAttribute('aria-expanded', 'true');
    });

    it('should support keyboard navigation', () => {
      mockedUseCompany.mockReturnValue({
        ...mockUseCompanyReturn,
        companies: [mockCompany1, mockCompany2],
        hasCompanies: true,
      });

      render(<CompanySelector />);
      
      const trigger = screen.getByRole('button');
      
      // Open with Enter key
      fireEvent.keyDown(trigger, { key: 'Enter' });
      expect(screen.getByRole('listbox')).toBeInTheDocument();
      
      // Close with Escape key
      fireEvent.keyDown(trigger, { key: 'Escape' });
      expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
    });
  });
});