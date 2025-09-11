import React from 'react';
import { Search } from 'lucide-react';
import { inputStyles } from '../../theme';

interface SearchInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  onSearch?: (value: string) => void;
  className?: string;
}

const SearchInput: React.FC<SearchInputProps> = ({
  onSearch,
  className = '',
  placeholder = 'Search...',
  ...props
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (onSearch) {
      onSearch(e.target.value);
    }
    if (props.onChange) {
      props.onChange(e);
    }
  };

  return (
    <div className={`relative flex-1 ${className}`}>
      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
      <input
        type="text"
        className={`${inputStyles.base} pl-10`}
        placeholder={placeholder}
        {...props}
        onChange={handleChange}
      />
    </div>
  );
};

export default SearchInput;