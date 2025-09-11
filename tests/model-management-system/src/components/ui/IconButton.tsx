import React from 'react';

interface IconButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  icon: React.ReactNode;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'ghost' | 'solid';
  className?: string;
}

const IconButton: React.FC<IconButtonProps> = ({
  icon,
  size = 'md',
  variant = 'default',
  className = '',
  ...props
}) => {
  const sizeClasses = {
    sm: 'p-1',
    md: 'p-1.5',
    lg: 'p-2',
  };

  const variantClasses = {
    default: 'bg-white/90 hover:bg-gray-100 border border-gray-200 shadow-sm',
    ghost: 'hover:bg-gray-100',
    solid: 'bg-gray-100 hover:bg-gray-200',
  };

  const classes = [
    'rounded transition-colors',
    sizeClasses[size],
    variantClasses[variant],
    className,
  ].filter(Boolean).join(' ');

  return (
    <button className={classes} {...props}>
      {icon}
    </button>
  );
};

export default IconButton;