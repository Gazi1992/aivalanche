import { statusColors } from '../theme';

export const getStatusBadgeColor = (status: string): string => {
  const normalizedStatus = status.toLowerCase().replace(/\s+/g, '-');
  return statusColors[normalizedStatus as keyof typeof statusColors] || 'bg-gray-100 text-gray-800';
};

export const getStatusIcon = (status: string) => {
  const statusIcons: Record<string, string> = {
    'production': '✓',
    'validated': '✓',
    'completed': '✓',
    'development': '⚡',
    'in-progress': '⟳',
    'calibrating': '⟳',
    'testing': '🧪',
    'failed': '✗',
    'pending': '⏳',
  };
  
  const normalizedStatus = status.toLowerCase().replace(/\s+/g, '-');
  return statusIcons[normalizedStatus] || '•';
};

export const formatStatus = (status: string): string => {
  return status
    .split(/[-_]/)
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
};