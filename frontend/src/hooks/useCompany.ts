/**
 * @file useCompany hook
 * Custom hook for company management with computed values and helpers
 */
import { useCompanyStore } from '@/store/company';
import type { Company, CompanyCreateData, CompanyUpdateData } from '@/types/company';

export const useCompany = () => {
  const {
    companies,
    selectedCompany,
    currentCompany,
    loading,
    error,
    fetchCompanies,
    createCompany,
    updateCompany,
    deleteCompany,
    setSelectedCompany,
    setCurrentCompany,
  } = useCompanyStore();

  // Computed values
  const hasCompanies = companies.length > 0;
  const hasSelectedCompany = selectedCompany !== null;
  const isLoading = loading;
  const hasError = error !== null;

  // Helper methods
  const findCompanyById = (id: string): Company | undefined => {
    return companies.find((company) => company.id === id);
  };

  const isCompanySelected = (id: string): boolean => {
    return selectedCompany?.id === id;
  };

  const clearSelection = () => {
    setSelectedCompany(null);
  };

  return {
    // State
    companies,
    selectedCompany,
    currentCompany,
    loading,
    error,
    
    // Computed values
    hasCompanies,
    hasSelectedCompany,
    isLoading,
    hasError,
    
    // Actions
    fetchCompanies,
    createCompany,
    updateCompany,
    deleteCompany,
    setSelectedCompany,
    setCurrentCompany,
    
    // Helper methods
    findCompanyById,
    isCompanySelected,
    clearSelection,
  };
};