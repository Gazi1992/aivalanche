import React from 'react';
import { X } from 'lucide-react';
import { theme } from '../../theme';

interface SidePanelProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  width?: 'sm' | 'md' | 'lg';
  className?: string;
}

const SidePanel: React.FC<SidePanelProps> = ({
  isOpen,
  onClose,
  title,
  children,
  width = 'md',
  className = '',
}) => {
  if (!isOpen) return null;

  const widthClasses = {
    sm: 'w-96',
    md: 'w-[500px]',
    lg: 'w-[600px]',
  };

  return (
    <div className={`fixed right-0 top-0 bottom-0 ${widthClasses[width]} bg-white border-l border-gray-200 flex flex-col z-40 shadow-xl ${className}`}>
      <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between flex-shrink-0">
        <h2 className={theme.typography.h4}>{title}</h2>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>
      <div className="flex-1 overflow-y-auto px-6 py-4">
        {children}
      </div>
    </div>
  );
};

export default SidePanel;