import React from 'react';
import Card from '../ui/Card';
import { theme } from '../../theme';

interface StatCardProps {
  label: string;
  value: string | number;
  icon?: React.ReactNode;
  trend?: {
    value: string;
    isPositive: boolean;
  };
  className?: string;
}

const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  icon,
  trend,
  className = '',
}) => {
  return (
    <Card className={className}>
      <div className="flex items-center justify-between">
        <div>
          <p className={theme.typography.metricLabel}>{label}</p>
          <p className={theme.typography.metric}>{value}</p>
          {trend && (
            <p className={`text-sm mt-1 ${trend.isPositive ? 'text-green-600' : 'text-red-600'}`}>
              {trend.isPositive ? '↑' : '↓'} {trend.value}
            </p>
          )}
        </div>
        {icon && (
          <div className="text-purple-500">
            {icon}
          </div>
        )}
      </div>
    </Card>
  );
};

export default StatCard;