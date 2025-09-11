import React from 'react';
import { StatusIcon, type TaskStatus } from './Icons';

export type { TaskStatus };
export type TaskPriority = 'low' | 'medium' | 'high';

interface StatusBadgeProps {
  status: TaskStatus;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
  className?: string;
}

interface PriorityBadgeProps {
  priority: TaskPriority;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ 
  status, 
  size = 'md',
  showIcon = true,
  className = '' 
}) => {
  const getIconSize = () => {
    switch (size) {
      case 'sm': return 'xs';
      case 'lg': return 'lg';
      default: return 'sm';
    }
  };

  const getStatusStyles = () => {
    const baseStyles = {
      'released': 'bg-gradient-to-r from-emerald-500 to-green-500 text-white font-bold',
      'completed': 'bg-green-100 text-green-800',
      'in-progress': 'bg-blue-100 text-blue-800',
      'failed': 'bg-red-100 text-red-800',
      'pending': 'bg-gray-100 text-gray-800'
    };
    return baseStyles[status];
  };

  const getSizeStyles = () => {
    switch (size) {
      case 'sm':
        return 'px-2 py-0.5 text-xs gap-1';
      case 'lg':
        return 'px-4 py-2 text-sm gap-2';
      default:
        return 'px-3 py-1.5 text-xs gap-1';
    }
  };

  const getStatusText = () => {
    if (status === 'released') {
      return 'RELEASED';
    }
    return status.replace('-', ' ');
  };

  return (
    <span className={`inline-flex items-center font-semibold rounded-full ${getStatusStyles()} ${getSizeStyles()} ${
      status === 'released' ? 'uppercase tracking-wider' : ''
    } ${className}`}>
      {showIcon && <StatusIcon status={status} size={getIconSize()} className="flex-shrink-0 !text-current" />}
      {getStatusText()}
    </span>
  );
};

export const PriorityBadge: React.FC<PriorityBadgeProps> = ({ 
  priority, 
  size = 'md',
  showLabel = true,
  className = '' 
}) => {
  const getPriorityStyles = () => {
    const baseStyles = {
      'high': 'bg-red-100 text-red-800',
      'medium': 'bg-yellow-100 text-yellow-800',
      'low': 'bg-gray-100 text-gray-800'
    };
    return baseStyles[priority];
  };

  const getSizeStyles = () => {
    switch (size) {
      case 'sm':
        return 'px-2 py-0.5 text-xs';
      case 'lg':
        return 'px-4 py-2 text-sm';
      default:
        return 'px-2 py-1 text-xs';
    }
  };

  return (
    <span className={`font-semibold rounded-full ${getPriorityStyles()} ${getSizeStyles()} ${className}`}>
      {priority}{showLabel ? ' priority' : ''}
    </span>
  );
};