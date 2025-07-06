/**
 * @file CompanySelector component
 * Dropdown component for selecting companies
 */
'use client';

import { useState, useEffect, useRef } from 'react';
import { useCompany } from '@/hooks/useCompany';
import type { Company } from '@/types/company';

interface CompanySelectorProps {
  className?: string;
  placeholder?: string;
  onSelect?: (company: Company) => void;
  disabled?: boolean;
}

export const CompanySelector = ({
  className = '',
  placeholder = 'Selecionar Empresa',
  onSelect,
  disabled = false,
}: CompanySelectorProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  
  const {
    companies,
    selectedCompany,
    hasCompanies,
    isLoading,
    hasError,
    error,
    fetchCompanies,
    setSelectedCompany,
  } = useCompany();

  // Fetch companies on mount
  useEffect(() => {
    fetchCompanies();
  }, [fetchCompanies]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const handleToggle = () => {
    if (!disabled) {
      setIsOpen(!isOpen);
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (disabled) return;

    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      setIsOpen(!isOpen);
    } else if (event.key === 'Escape') {
      setIsOpen(false);
    }
  };

  const handleSelect = (company: Company) => {
    setSelectedCompany(company);
    setIsOpen(false);
    onSelect?.(company);
  };

  const renderTrigger = () => {
    if (isLoading) {
      return <span>Carregando...</span>;
    }

    if (hasError) {
      return <span>Erro: {error}</span>;
    }

    if (selectedCompany) {
      return <span>{selectedCompany.name}</span>;
    }

    return <span>{placeholder}</span>;
  };

  const renderDropdown = () => {
    if (!isOpen) return null;

    if (isLoading) {
      return (
        <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-300 rounded-md shadow-lg z-10">
          <div className="p-2 text-gray-500">Carregando...</div>
        </div>
      );
    }

    if (!hasCompanies) {
      return (
        <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-300 rounded-md shadow-lg z-10">
          <div className="p-2 text-gray-500">Nenhuma empresa encontrada</div>
        </div>
      );
    }

    return (
      <div
        role="listbox"
        className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-300 rounded-md shadow-lg z-10 max-h-60 overflow-y-auto"
      >
        {companies.map((company) => (
          <button
            key={company.id}
            className="w-full text-left p-3 hover:bg-gray-50 focus:bg-gray-50 focus:outline-none border-b border-gray-100 last:border-b-0"
            onClick={() => handleSelect(company)}
            role="option"
            aria-selected={selectedCompany?.id === company.id}
          >
            <div className="font-medium text-gray-900">{company.name}</div>
            <div className="text-sm text-gray-500">{company.cnpj}</div>
            <div className="text-xs text-gray-400">{company.business_sector}</div>
          </button>
        ))}
      </div>
    );
  };

  return (
    <div ref={dropdownRef} className={`relative ${className}`}>
      <button
        type="button"
        className={`
          w-full px-3 py-2 text-left bg-white border border-gray-300 rounded-md shadow-sm
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
          ${disabled ? 'bg-gray-100 cursor-not-allowed' : 'hover:border-gray-400 cursor-pointer'}
          ${isOpen ? 'ring-2 ring-blue-500 border-blue-500' : ''}
        `}
        onClick={handleToggle}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
      >
        <div className="flex items-center justify-between">
          {renderTrigger()}
          <svg
            className={`w-5 h-5 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
              clipRule="evenodd"
            />
          </svg>
        </div>
      </button>

      {renderDropdown()}
    </div>
  );
};