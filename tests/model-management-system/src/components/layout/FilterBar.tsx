import React from 'react';
import SearchInput from '../ui/SearchInput';
import Card from '../ui/Card';

interface FilterBarProps {
  searchValue: string;
  onSearchChange: (value: string) => void;
  filters?: React.ReactNode;
  actions?: React.ReactNode;
  className?: string;
}

const FilterBar: React.FC<FilterBarProps> = ({
  searchValue,
  onSearchChange,
  filters,
  actions,
  className = '',
}) => {
  return (
    <Card padding="sm" className={`mb-4 flex-shrink-0 ${className}`}>
      <div className="flex gap-4 items-center">
        <SearchInput
          value={searchValue}
          onSearch={onSearchChange}
          placeholder="Search..."
        />
        
        {filters}
        
        {actions && (
          <div className="flex gap-2">
            {actions}
          </div>
        )}
      </div>
    </Card>
  );
};

export default FilterBar;