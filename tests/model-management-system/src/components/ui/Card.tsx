import React from 'react';
import { cardStyles } from '../../theme';

interface CardProps {
  variant?: keyof typeof cardStyles;
  className?: string;
  children: React.ReactNode;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  onClick?: () => void;
}

const Card: React.FC<CardProps> = ({
  variant = 'base',
  className = '',
  children,
  padding = 'lg',
  onClick,
}) => {
  const paddingClasses = {
    none: '',
    sm: 'p-4',
    md: 'p-5',
    lg: 'p-6',
  };

  const classes = [
    cardStyles[variant],
    paddingClasses[padding],
    onClick ? 'cursor-pointer hover:shadow-lg transition-shadow' : '',
    className,
  ].filter(Boolean).join(' ');

  return (
    <div className={classes} onClick={onClick}>
      {children}
    </div>
  );
};

export default Card;