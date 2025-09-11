/**
 * Centralized icon definitions and components for consistent UI across the application
 */

import React from 'react';
import { 
  Home, 
  Database, 
  Cpu, 
  FileText, 
  BarChart3, 
  Settings, 
  User, 
  LogOut, 
  ChevronLeft, 
  ChevronRight, 
  HelpCircle, 
  Headphones,
  Presentation,
  Play,
  Pause,
  Zap,
  Shield,
  Users,
  GitBranch,
  Package,
  Layers,
  Info,
  AlertCircle,
  Search,
  X,
  Book,
  BookOpen,
  GraduationCap,
  Mail,
  Lock,
  Building,
  LogIn,
  UserPlus,
  Rocket,
  CheckCircle,
  RefreshCw,
  Clock,
  Wrench,
  Plus,
  TrendingUp,
  Download,
  List,
  Grid3X3,
  Filter,
  Share2,
  FileBarChart,
  Calendar,
  Sliders,
  Trash2,
  ChevronDown,
  Shuffle,
  CheckCircle2,
  Brain,
  Briefcase,
  Network,
  Microscope,
  Send,
  Phone,
  MessageSquare,
  FolderOpen,
  Copy,
  Check,
  Code,
  Table,
  TestTube,
  Eye,
  Server,
  ArrowRight,
  ArrowLeft,
  ChevronUp,
  ChevronsUpDown,
  MoreVertical,
  Maximize2,
  Activity,
  ExternalLink,
  Edit,
  Save,
  Image,
  AlertTriangle,
  RotateCw,
  FileDown,
  type LucideIcon
} from 'lucide-react';

// Navigation Icons
export const ICONS = {
  // Main Navigation
  dashboard: Home,
  libraries: Database,
  myModels: Cpu,
  requests: FileText,
  reports: BarChart3,
  settings: Settings,
  profile: User,
  
  // Support & Help
  userGuide: BookOpen,
  contactSupport: Headphones,
  presentation: Presentation,
  technicalPresentation: Presentation, // Alias for clarity
  systemArchitecture: Layers, // Alias for clarity
  
  // Authentication
  login: LogIn,
  logout: LogOut,
  register: UserPlus,
  
  // Form Icons
  email: Mail,
  password: Lock,
  department: Building,
  user: User,
  
  // UI Controls
  chevronLeft: ChevronLeft,
  chevronRight: ChevronRight,
  chevronDown: ChevronDown,
  close: X,
  search: Search,
  play: Play,
  pause: Pause,
  filter: Filter,
  list: List,
  grid: Grid3X3,
  
  // Features
  optimization: Zap,
  security: Shield,
  collaboration: Users,
  workflow: GitBranch,
  packages: Package,
  architecture: Layers,
  
  // Status & Alerts
  info: Info,
  alert: AlertCircle,
  help: HelpCircle,
  
  // Task Status Icons
  released: Rocket,
  completed: CheckCircle,
  inProgress: RefreshCw,
  failed: AlertCircle,
  pending: Clock,
  
  // Actions
  wrench: Wrench,
  plus: Plus,
  trending: TrendingUp,
  download: Download,
  share: Share2,
  calendar: Calendar,
  sliders: Sliders,
  trash: Trash2,
  
  // Calibration Tabs
  model: FileText,
  referenceData: Database,
  simulations: Play,
  calibration: Brain,
  monteCarlo: Shuffle,
  validation: CheckCircle2,
  encryption: Shield,
  documentation: FileText,
  report: FileBarChart,
  
  // Persona Icons
  requestor: Briefcase,
  manager: Network,
  dataProvider: Microscope,
  modelEngineer: Brain,
  
  // Communication
  send: Send,
  phone: Phone,
  messageSquare: MessageSquare,
  
  // File Operations
  folderOpen: FolderOpen,
  copy: Copy,
  check: Check,
  code: Code,
  table: Table,
  eye: Eye,
  image: Image,
  edit: Edit,
  save: Save,
  fileDown: FileDown,
  
  // Lab/Testing
  testTube: TestTube,
  activity: Activity,
  
  // System
  server: Server,
  externalLink: ExternalLink,
  
  // Navigation Arrows
  arrowRight: ArrowRight,
  arrowLeft: ArrowLeft,
  chevronUp: ChevronUp,
  chevronsUpDown: ChevronsUpDown,
  moreVertical: MoreVertical,
  
  // UI Controls
  maximize: Maximize2,
  rotateCw: RotateCw,
  
  // Alerts
  alertTriangle: AlertTriangle,
} as const;

// Type for icon keys
export type IconName = keyof typeof ICONS;

// Helper function to get icon component
export const getIcon = (name: IconName): LucideIcon => {
  return ICONS[name];
};

// Common icon props for consistency
export const ICON_SIZES = {
  xs: 'w-3 h-3',
  sm: 'w-4 h-4',
  md: 'w-5 h-5',
  lg: 'w-6 h-6',
  xl: 'w-8 h-8',
  '2xl': 'w-10 h-10',
} as const;

export type IconSize = keyof typeof ICON_SIZES;

// Get size class
export const getIconSizeClass = (size: IconSize = 'md'): string => {
  return ICON_SIZES[size];
};

// Task Status specific helpers
export type TaskStatus = 'pending' | 'in-progress' | 'completed' | 'failed' | 'released';

export const STATUS_ICON_COLORS = {
  released: 'text-emerald-600',
  completed: 'text-green-500',
  'in-progress': 'text-blue-500',
  failed: 'text-red-500',
  pending: 'text-gray-400',
} as const;

export const getStatusIconName = (status: TaskStatus): IconName => {
  switch (status) {
    case 'released':
      return 'released';
    case 'completed':
      return 'completed';
    case 'in-progress':
      return 'inProgress';
    case 'failed':
      return 'failed';
    default:
      return 'pending';
  }
};

// Status Icon Component
interface StatusIconProps {
  status: TaskStatus;
  size?: IconSize;
  className?: string;
}

export const StatusIcon: React.FC<StatusIconProps> = ({ 
  status, 
  size = 'md',
  className = ''
}) => {
  const Icon = getIcon(getStatusIconName(status));
  const sizeClass = getIconSizeClass(size);
  const colorClass = STATUS_ICON_COLORS[status];
  const animateClass = status === 'in-progress' ? 'animate-spin' : '';
  
  return <Icon className={`${sizeClass} ${colorClass} ${animateClass} ${className}`} />;
};

// Generic Icon Component
interface IconProps {
  name: IconName;
  size?: IconSize;
  className?: string;
}

export const Icon: React.FC<IconProps> = ({ 
  name, 
  size = 'md',
  className = ''
}) => {
  const IconComponent = getIcon(name);
  const sizeClass = getIconSizeClass(size);
  
  return <IconComponent className={`${sizeClass} ${className}`} />;
};

// ============= PERSONA ICONS =============

// Color configurations for each persona
export const personaColors = {
  requestor: {
    primary: '#fb923c', // orange-400
    gradient: 'from-orange-400 to-orange-600',
    border: 'border-orange-500',
    text: 'text-orange-700',
    bg: 'bg-orange-100'
  },
  manager: {
    primary: '#3b82f6', // blue-500
    gradient: 'from-blue-400 to-blue-600',
    border: 'border-blue-500',
    text: 'text-blue-700',
    bg: 'bg-blue-100'
  },
  dataProvider: {
    primary: '#10b981', // green-500
    gradient: 'from-green-400 to-green-600',
    border: 'border-green-500',
    text: 'text-green-700',
    bg: 'bg-green-100'
  },
  engineer: {
    primary: '#a855f7', // purple-500
    gradient: 'from-purple-400 to-purple-600',
    border: 'border-purple-500',
    text: 'text-purple-700',
    bg: 'bg-purple-100'
  }
};

interface PersonaIconProps {
  size?: 'small' | 'medium' | 'large';
  showShoulders?: boolean;
  className?: string;
}

// Requestor Icon Component
export const RequestorIcon: React.FC<PersonaIconProps> = ({ 
  size = 'medium', 
  showShoulders = true,
  className = '' 
}) => {
  const sizes = {
    small: { circle: 'w-10 h-10', icon: 'w-5 h-5', svg: 'w-14 h-6' },
    medium: { circle: 'w-16 h-16', icon: 'w-8 h-8', svg: 'w-20 h-8' },
    large: { circle: 'w-24 h-24', icon: 'w-12 h-12', svg: 'w-32 h-12' }
  };

  const sizeConfig = sizes[size];
  const IconComponent = ICONS.requestor; // Using Briefcase from ICONS

  return (
    <div className={`relative ${className}`}>
      <div className={`${sizeConfig.circle} bg-gradient-to-br ${personaColors.requestor.gradient} rounded-full flex items-center justify-center relative z-10`}>
        <IconComponent className={`${sizeConfig.icon} text-white`} />
      </div>
      {showShoulders && (
        <svg className={`absolute -bottom-3 left-1/2 transform -translate-x-1/2 ${sizeConfig.svg}`} viewBox="0 0 128 48">
          <path 
            d="M 20 48 Q 20 20 64 20 Q 108 20 108 48" 
            fill={personaColors.requestor.primary}
            opacity="0.9"
          />
        </svg>
      )}
    </div>
  );
};

// Manager Icon Component
export const ManagerIcon: React.FC<PersonaIconProps> = ({ 
  size = 'medium', 
  showShoulders = true,
  className = '' 
}) => {
  const sizes = {
    small: { circle: 'w-10 h-10', icon: 'w-5 h-5', svg: 'w-14 h-6' },
    medium: { circle: 'w-16 h-16', icon: 'w-8 h-8', svg: 'w-20 h-8' },
    large: { circle: 'w-24 h-24', icon: 'w-12 h-12', svg: 'w-32 h-12' }
  };

  const sizeConfig = sizes[size];
  const IconComponent = ICONS.manager; // Using Network from ICONS

  return (
    <div className={`relative ${className}`}>
      <div className={`${sizeConfig.circle} bg-gradient-to-br ${personaColors.manager.gradient} rounded-full flex items-center justify-center relative z-10`}>
        <IconComponent className={`${sizeConfig.icon} text-white`} />
      </div>
      {showShoulders && (
        <svg className={`absolute -bottom-3 left-1/2 transform -translate-x-1/2 ${sizeConfig.svg}`} viewBox="0 0 128 48">
          <path 
            d="M 20 48 Q 20 20 64 20 Q 108 20 108 48" 
            fill={personaColors.manager.primary}
            opacity="0.9"
          />
        </svg>
      )}
    </div>
  );
};

// Data Provider Icon Component
export const DataProviderIcon: React.FC<PersonaIconProps> = ({ 
  size = 'medium', 
  showShoulders = true,
  className = '' 
}) => {
  const sizes = {
    small: { circle: 'w-10 h-10', icon: 'w-5 h-5', svg: 'w-14 h-6' },
    medium: { circle: 'w-16 h-16', icon: 'w-8 h-8', svg: 'w-20 h-8' },
    large: { circle: 'w-24 h-24', icon: 'w-12 h-12', svg: 'w-32 h-12' }
  };

  const sizeConfig = sizes[size];
  const IconComponent = ICONS.dataProvider; // Using Microscope from ICONS

  return (
    <div className={`relative ${className}`}>
      <div className={`${sizeConfig.circle} bg-gradient-to-br ${personaColors.dataProvider.gradient} rounded-full flex items-center justify-center relative z-10`}>
        <IconComponent className={`${sizeConfig.icon} text-white`} />
      </div>
      {showShoulders && (
        <svg className={`absolute -bottom-3 left-1/2 transform -translate-x-1/2 ${sizeConfig.svg}`} viewBox="0 0 128 48">
          <path 
            d="M 20 48 Q 20 20 64 20 Q 108 20 108 48" 
            fill={personaColors.dataProvider.primary}
            opacity="0.9"
          />
        </svg>
      )}
    </div>
  );
};

// Model Engineer Icon Component
export const EngineerIcon: React.FC<PersonaIconProps> = ({ 
  size = 'medium', 
  showShoulders = true,
  className = '' 
}) => {
  const sizes = {
    small: { circle: 'w-10 h-10', icon: 'w-5 h-5', svg: 'w-14 h-6' },
    medium: { circle: 'w-16 h-16', icon: 'w-8 h-8', svg: 'w-20 h-8' },
    large: { circle: 'w-24 h-24', icon: 'w-12 h-12', svg: 'w-32 h-12' }
  };

  const sizeConfig = sizes[size];
  const IconComponent = ICONS.modelEngineer; // Using Brain from ICONS

  return (
    <div className={`relative ${className}`}>
      <div className={`${sizeConfig.circle} bg-gradient-to-br ${personaColors.engineer.gradient} rounded-full flex items-center justify-center relative z-10`}>
        <IconComponent className={`${sizeConfig.icon} text-white`} />
      </div>
      {showShoulders && (
        <svg className={`absolute -bottom-3 left-1/2 transform -translate-x-1/2 ${sizeConfig.svg}`} viewBox="0 0 128 48">
          <path 
            d="M 20 48 Q 20 20 64 20 Q 108 20 108 48" 
            fill={personaColors.engineer.primary}
            opacity="0.9"
          />
        </svg>
      )}
    </div>
  );
};

// Generic persona icon component that takes a type
export type PersonaType = 'requestor' | 'manager' | 'dataProvider' | 'engineer';

export const PersonaIcon: React.FC<PersonaIconProps & { type: PersonaType }> = ({ 
  type, 
  ...props 
}) => {
  switch (type) {
    case 'requestor':
      return <RequestorIcon {...props} />;
    case 'manager':
      return <ManagerIcon {...props} />;
    case 'dataProvider':
      return <DataProviderIcon {...props} />;
    case 'engineer':
      return <EngineerIcon {...props} />;
    default:
      return null;
  }
};