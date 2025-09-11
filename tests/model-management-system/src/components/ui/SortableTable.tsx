import React, { useState, useMemo } from 'react';
import { ChevronUp, ChevronDown, ChevronsUpDown } from 'lucide-react';

export interface Column<T> {
  key: string;
  header: string | React.ReactNode;
  sortable?: boolean;
  render?: (value: any, item: T, index: number) => React.ReactNode;
  className?: string;
  headerClassName?: string;
}

interface SortableTableProps<T> {
  data: T[];
  columns: Column<T>[];
  className?: string;
  headerClassName?: string;
  rowClassName?: string | ((item: T, index: number) => string);
  onRowClick?: (item: T, index: number) => void;
  stickyHeader?: boolean;
  striped?: boolean;
  hoverable?: boolean;
  compact?: boolean;
}

type SortDirection = 'asc' | 'desc' | null;

const SortableTable = <T extends Record<string, any>>({
  data,
  columns,
  className = '',
  headerClassName = '',
  rowClassName = '',
  onRowClick,
  stickyHeader = true,
  striped = false,
  hoverable = true,
  compact = false
}: SortableTableProps<T>) => {
  const [sortColumn, setSortColumn] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<SortDirection>(null);

  const handleSort = (columnKey: string) => {
    if (sortColumn === columnKey) {
      // Toggle through: asc -> desc -> null
      if (sortDirection === 'asc') {
        setSortDirection('desc');
      } else if (sortDirection === 'desc') {
        setSortDirection(null);
        setSortColumn(null);
      }
    } else {
      setSortColumn(columnKey);
      setSortDirection('asc');
    }
  };

  const sortedData = useMemo(() => {
    if (!sortColumn || !sortDirection) return data;

    return [...data].sort((a, b) => {
      const aValue = a[sortColumn];
      const bValue = b[sortColumn];

      // Handle null/undefined values
      if (aValue == null) return sortDirection === 'asc' ? 1 : -1;
      if (bValue == null) return sortDirection === 'asc' ? -1 : 1;

      // Numeric comparison
      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return sortDirection === 'asc' ? aValue - bValue : bValue - aValue;
      }

      // String comparison (case-insensitive)
      const aStr = String(aValue).toLowerCase();
      const bStr = String(bValue).toLowerCase();
      
      if (aStr < bStr) return sortDirection === 'asc' ? -1 : 1;
      if (aStr > bStr) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
  }, [data, sortColumn, sortDirection]);

  const getSortIcon = (columnKey: string) => {
    if (sortColumn !== columnKey) {
      return <ChevronsUpDown className="w-3 h-3 text-gray-400" />;
    }
    if (sortDirection === 'asc') {
      return <ChevronUp className="w-3 h-3 text-purple-600" />;
    }
    if (sortDirection === 'desc') {
      return <ChevronDown className="w-3 h-3 text-purple-600" />;
    }
    return <ChevronsUpDown className="w-3 h-3 text-gray-400" />;
  };

  const getRowClassName = (item: T, index: number): string => {
    const baseClasses = [];
    
    if (hoverable) baseClasses.push('hover:bg-gray-50');
    if (striped && index % 2 === 1) baseClasses.push('bg-gray-50/50');
    if (onRowClick) baseClasses.push('cursor-pointer');
    
    if (typeof rowClassName === 'function') {
      baseClasses.push(rowClassName(item, index));
    } else if (rowClassName) {
      baseClasses.push(rowClassName);
    }
    
    return baseClasses.join(' ');
  };

  const paddingClass = compact ? 'px-2 py-1' : 'px-4 py-2';

  return (
    <table className={`w-full ${className}`}>
      <thead className={`bg-gray-50 border-b border-gray-200 ${stickyHeader ? 'sticky top-0 z-10' : ''} ${headerClassName}`}>
        <tr>
          {columns.map((column) => (
            <th
              key={column.key}
              className={`${paddingClass} text-left text-xs font-medium text-gray-700 ${
                column.sortable ? 'cursor-pointer select-none hover:bg-gray-100' : ''
              } ${column.headerClassName || ''}`}
              onClick={column.sortable ? () => handleSort(column.key) : undefined}
            >
              {column.sortable ? (
                <div className="flex items-center justify-between">
                  <span>{column.header}</span>
                  <span className="ml-1">
                    {getSortIcon(column.key)}
                  </span>
                </div>
              ) : (
                typeof column.header === 'string' ? (
                  <span>{column.header}</span>
                ) : (
                  column.header
                )
              )}
            </th>
          ))}
        </tr>
      </thead>
      <tbody className="bg-white divide-y divide-gray-200">
        {sortedData.map((item, rowIndex) => (
          <tr
            key={rowIndex}
            className={getRowClassName(item, rowIndex)}
            onClick={onRowClick ? () => onRowClick(item, rowIndex) : undefined}
          >
            {columns.map((column) => {
              const value = item[column.key];
              const cellContent = column.render 
                ? column.render(value, item, rowIndex)
                : value;

              return (
                <td
                  key={column.key}
                  className={`${paddingClass} text-sm text-gray-900 ${column.className || ''}`}
                >
                  {cellContent}
                </td>
              );
            })}
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default SortableTable;