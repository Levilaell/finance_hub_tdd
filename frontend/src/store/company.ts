/**
 * @file Company store
 * Zustand store for company management
 */
import { create } from 'zustand';
import { companyService } from '@/services/company';
import type { Company, CompanyCreateData, CompanyUpdateData } from '@/types/company';

interface CompanyState {
  // State
  companies: Company[];
  selectedCompany: Company | null;
  currentCompany: Company | null;
  loading: boolean;
  error: string | null;

  // Actions
  setCompanies: (companies: Company[]) => void;
  setSelectedCompany: (company: Company | null) => void;
  setCurrentCompany: (company: Company | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;

  // Async actions
  fetchCompanies: (params?: Record<string, any>) => Promise<void>;
  createCompany: (data: CompanyCreateData) => Promise<Company>;
  updateCompany: (id: string, data: CompanyUpdateData) => Promise<Company>;
  deleteCompany: (id: string) => Promise<void>;
}

const initialState = {
  companies: [],
  selectedCompany: null,
  currentCompany: null,
  loading: false,
  error: null,
};

export const useCompanyStore = create<CompanyState>((set, get) => ({
  ...initialState,

  // Setters
  setCompanies: (companies) => set({ companies }),
  setSelectedCompany: (selectedCompany) => set({ selectedCompany }),
  setCurrentCompany: (currentCompany) => set({ currentCompany }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  reset: () => set(initialState),

  // Async actions
  fetchCompanies: async (params) => {
    try {
      set({ loading: true, error: null });
      const response = await companyService.getCompanies(params);
      set({ companies: response.results, loading: false });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      set({ loading: false, error: errorMessage });
    }
  },

  createCompany: async (data) => {
    try {
      set({ error: null });
      const company = await companyService.createCompany(data);
      const { companies } = get();
      set({ companies: [...companies, company] });
      return company;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      set({ error: errorMessage });
      throw error;
    }
  },

  updateCompany: async (id, data) => {
    try {
      set({ error: null });
      const updatedCompany = await companyService.updateCompany(id, data);
      const { companies } = get();
      const updatedCompanies = companies.map((company) =>
        company.id === id ? updatedCompany : company
      );
      set({ companies: updatedCompanies });
      return updatedCompany;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      set({ error: errorMessage });
      throw error;
    }
  },

  deleteCompany: async (id) => {
    try {
      set({ error: null });
      await companyService.deleteCompany(id);
      const { companies } = get();
      const updatedCompanies = companies.filter((company) => company.id !== id);
      set({ companies: updatedCompanies });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      set({ error: errorMessage });
      throw error;
    }
  },
}));