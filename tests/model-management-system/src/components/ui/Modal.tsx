import React from 'react';
import { X } from 'lucide-react';
import { modalStyles } from '../../theme';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  className?: string;
  noScroll?: boolean;
}

const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  footer,
  size = 'lg',
  className = '',
  noScroll = false,
}) => {
  if (!isOpen) return null;

  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    full: 'max-w-[95vw]',
  };

  // Use fixed dimensions for full-size modal with noScroll
  const containerClasses = size === 'full' && noScroll 
    ? `bg-white rounded-lg flex flex-col h-[90vh] ${sizeClasses[size]} w-full ${className}`
    : `${modalStyles.container} ${sizeClasses[size]} w-full ${className}`;

  return (
    <div className={modalStyles.overlay}>
      <div className={containerClasses}>
        <div className={modalStyles.header}>
          <h2 className="text-xl font-semibold text-gray-900">{title}</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div className={noScroll ? 'flex-1 px-6 py-4 flex flex-col overflow-hidden' : modalStyles.body}>
          {children}
        </div>
        
        {footer && (
          <div className={modalStyles.footer}>
            {footer}
          </div>
        )}
      </div>
    </div>
  );
};

export default Modal;