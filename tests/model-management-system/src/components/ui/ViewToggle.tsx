import React from 'react';
import { List, Grid3X3 } from 'lucide-react';

interface ViewToggleProps {
  viewMode: 'table' | 'cards';
  onViewChange: (mode: 'table' | 'cards') => void;
  className?: string;
}

const ViewToggle: React.FC<ViewToggleProps> = ({
  viewMode,
  onViewChange,
  className = '',
}) => {
  return (
    <div className={`flex items-center border border-gray-300 rounded-lg ${className}`}>
      <button
        onClick={() => onViewChange('table')}
        className={`px-4 py-2 rounded-l-lg transition-colors ${
          viewMode === 'table'
            ? 'bg-purple-600 text-white'
            : 'bg-white text-gray-700 hover:bg-gray-50'
        }`}
        title="Table View"
      >
        <List className="w-4 h-4" />
      </button>
      <button
        onClick={() => onViewChange('cards')}
        className={`px-4 py-2 rounded-r-lg transition-colors ${
          viewMode === 'cards'
            ? 'bg-purple-600 text-white'
            : 'bg-white text-gray-700 hover:bg-gray-50'
        }`}
        title="Card View"
      >
        <Grid3X3 className="w-4 h-4" />
      </button>
    </div>
  );
};

export default ViewToggle;