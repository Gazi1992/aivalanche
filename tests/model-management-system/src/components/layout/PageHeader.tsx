import React from 'react';
import { theme } from '../../theme';

interface PageHeaderProps {
  title: string;
  description?: string;
  actions?: React.ReactNode;
  className?: string;
}

const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  description,
  actions,
  className = '',
}) => {
  return (
    <div className={`flex justify-between items-start mb-6 ${className}`}>
      <div>
        <h1 className={theme.typography.h1}>{title}</h1>
        {description && (
          <p className="text-gray-600 mt-1">{description}</p>
        )}
      </div>
      {actions && (
        <div className="flex gap-3">
          {actions}
        </div>
      )}
    </div>
  );
};

export default PageHeader;