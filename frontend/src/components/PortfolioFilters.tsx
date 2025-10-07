import React, { useState, useEffect } from 'react';
import { Filter, X, ChevronDown } from 'lucide-react';
import axios from 'axios';

interface FilterOptions {
  owners: string[];
  brokers: string[];
  account_types: string[];
}

interface PortfolioFiltersProps {
  sessionId: string;
  onFiltersChange: (filters: {
    owner?: string;
    broker?: string;
    account_type?: string;
  }) => void;
}

const PortfolioFilters: React.FC<PortfolioFiltersProps> = ({ sessionId, onFiltersChange }) => {
  const [filterOptions, setFilterOptions] = useState<FilterOptions>({
    owners: [],
    brokers: [],
    account_types: []
  });
  const [activeFilters, setActiveFilters] = useState<{
    owner?: string;
    broker?: string;
    account_type?: string;
  }>({});
  const [isExpanded, setIsExpanded] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // 필터 옵션 로드
  useEffect(() => {
    if (sessionId) {
      loadFilterOptions();
    }
  }, [sessionId]);

  const loadFilterOptions = async () => {
    try {
      setIsLoading(true);
      const response = await axios.get(`http://localhost:8000/portfolio/filters/${sessionId}`);
      setFilterOptions(response.data);
    } catch (error) {
      console.error('필터 옵션 로드 실패:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFilterChange = (type: 'owner' | 'broker' | 'account_type', value: string) => {
    const newFilters = { ...activeFilters };
    
    if (value === '전체') {
      delete newFilters[type];
    } else {
      newFilters[type] = value;
    }
    
    setActiveFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const clearAllFilters = () => {
    setActiveFilters({});
    onFiltersChange({});
  };

  const hasActiveFilters = Object.keys(activeFilters).length > 0;

  const FilterDropdown: React.FC<{
    label: string;
    options: string[];
    value?: string;
    onChange: (value: string) => void;
  }> = ({ label, options, value, onChange }) => {
    const [isOpen, setIsOpen] = useState(false);

    return (
      <div className="relative">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center space-x-2 px-3 py-2 text-sm bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <span className="text-gray-700">{label}:</span>
          <span className="font-medium text-gray-900">
            {value || '전체'}
          </span>
          <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
        </button>

        {isOpen && (
          <div className="absolute top-full left-0 mt-1 w-48 bg-white border border-gray-300 rounded-lg shadow-lg z-10">
            <div className="py-1">
              <button
                onClick={() => {
                  onChange('전체');
                  setIsOpen(false);
                }}
                className={`w-full px-3 py-2 text-left text-sm hover:bg-gray-50 ${
                  !value ? 'bg-blue-50 text-blue-700' : 'text-gray-700'
                }`}
              >
                전체
              </button>
              {options.map((option) => (
                <button
                  key={option}
                  onClick={() => {
                    onChange(option);
                    setIsOpen(false);
                  }}
                  className={`w-full px-3 py-2 text-left text-sm hover:bg-gray-50 ${
                    value === option ? 'bg-blue-50 text-blue-700' : 'text-gray-700'
                  }`}
                >
                  {option}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      {/* 필터 헤더 */}
      <div 
        className="flex items-center justify-between cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center space-x-2">
          <Filter className="w-5 h-5 text-blue-600" />
          <h3 className="font-semibold text-gray-900">포트폴리오 필터</h3>
          {hasActiveFilters && (
            <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
              {Object.keys(activeFilters).length}개 적용
            </span>
          )}
        </div>
        <ChevronDown className={`w-5 h-5 text-gray-500 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
      </div>

      {/* 필터 내용 */}
      {isExpanded && (
        <div className="mt-4 space-y-4">
          {isLoading ? (
            <div className="text-center py-4">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
              <p className="text-sm text-gray-600 mt-2">필터 옵션을 로드하는 중...</p>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <FilterDropdown
                  label="소유자"
                  options={filterOptions.owners}
                  value={activeFilters.owner}
                  onChange={(value) => handleFilterChange('owner', value)}
                />
                <FilterDropdown
                  label="증권사"
                  options={filterOptions.brokers}
                  value={activeFilters.broker}
                  onChange={(value) => handleFilterChange('broker', value)}
                />
                <FilterDropdown
                  label="계좌 타입"
                  options={filterOptions.account_types}
                  value={activeFilters.account_type}
                  onChange={(value) => handleFilterChange('account_type', value)}
                />
              </div>

              {hasActiveFilters && (
                <div className="flex items-center justify-between pt-3 border-t border-gray-200">
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <span>적용된 필터:</span>
                    {activeFilters.owner && (
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
                        소유자: {activeFilters.owner}
                      </span>
                    )}
                    {activeFilters.broker && (
                      <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">
                        증권사: {activeFilters.broker}
                      </span>
                    )}
                    {activeFilters.account_type && (
                      <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-xs">
                        계좌: {activeFilters.account_type}
                      </span>
                    )}
                  </div>
                  <button
                    onClick={clearAllFilters}
                    className="flex items-center space-x-1 px-3 py-1 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <X className="w-4 h-4" />
                    <span>모두 해제</span>
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default PortfolioFilters;
