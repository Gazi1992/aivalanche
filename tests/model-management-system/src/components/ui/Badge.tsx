import React from 'react';
import { statusColors } from '../../theme';

interface BadgeProps {
  status?: keyof typeof statusColors;
  children: React.ReactNode;
  className?: string;
  size?: 'sm' | 'md';
}

const Badge: React.FC<BadgeProps> = ({
  status,
  children,
  className = '',
  size = 'md',
}) => {
  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
  };

  const colorClass = status ? statusColors[status] : 'bg-gray-100 text-gray-800';
  
  const classes = [
    'inline-flex items-center rounded-full font-medium',
    sizeClasses[size],
    colorClass,
    className,
  ].filter(Boolean).join(' ');

  return <span className={classes}>{children}</span>;
};

export default Badge;