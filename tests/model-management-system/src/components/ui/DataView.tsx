import React from 'react';
import ViewToggle from './ViewToggle';
import SortableTable, { Column } from './SortableTable';
import Card from './Card';

export type ViewMode = 'table' | 'cards';

interface DataViewProps<T> {
  data: T[];
  viewMode: ViewMode;
  onViewModeChange: (mode: ViewMode) => void;
  
  // Table configuration
  columns?: Column<T>[];
  onRowClick?: (item: T, index: number) => void;
  stickyHeader?: boolean;
  
  // Card configuration
  renderCard: (item: T, index: number) => React.ReactNode;
  cardClassName?: string | ((item: T, index: number) => string);
  gridClassName?: string;
  
  // Common props
  className?: string;
  emptyMessage?: string | React.ReactNode;
  showViewToggle?: boolean;
  viewTogglePosition?: 'top' | 'inline';
}

const DataView = <T extends Record<string, any>>({
  data,
  viewMode,
  onViewModeChange,
  columns = [],
  onRowClick,
  stickyHeader = true,
  renderCard,
  cardClassName = '',
  gridClassName = 'p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4',
  className = '',
  emptyMessage = 'No data available',
  showViewToggle = true,
  viewTogglePosition = 'inline'
}: DataViewProps<T>) => {
  
  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        {emptyMessage}
      </div>
    );
  }

  const content = viewMode === 'table' ? (
    <SortableTable
      data={data}
      columns={columns}
      onRowClick={onRowClick}
      stickyHeader={stickyHeader}
      hoverable={true}
      className="w-full"
    />
  ) : (
    <div className={gridClassName}>
      {data.map((item, index) => (
        <div 
          key={index} 
          className={typeof cardClassName === 'function' ? cardClassName(item, index) : cardClassName}
          onClick={() => onRowClick?.(item, index)}
        >
          {renderCard(item, index)}
        </div>
      ))}
    </div>
  );

  if (!showViewToggle || viewTogglePosition === 'inline') {
    return (
      <Card padding="none" className={`flex-1 overflow-auto ${className}`}>
        {content}
      </Card>
    );
  }

  return (
    <div className={`flex flex-col ${className}`}>
      <div className="flex justify-end mb-4">
        <ViewToggle viewMode={viewMode} onViewChange={onViewModeChange} />
      </div>
      <Card padding="none" className="flex-1 overflow-auto">
        {content}
      </Card>
    </div>
  );
};

export default DataView;