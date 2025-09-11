export interface User {
  id: string;
  email: string;
  name: string;
  department: string;
  role: 'admin' | 'engineer' | 'manager' | 'viewer';
  avatar?: string;
  preferences: UserPreferences;
  statistics: UserStatistics;
  createdAt: string;
  lastLogin: string;
}

export interface UserPreferences {
  theme: 'light' | 'dark';
  defaultView: string;
  emailNotifications: boolean;
  dashboardLayout: string[];
  favoriteModels: string[];
  recentProjects: string[];
}

export interface UserStatistics {
  totalRequests: number;
  completedRequests: number;
  pendingRequests: number;
  modelsCreated: number;
  averageCalibrationTime: number;
  successRate: number;
}

export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  loading: boolean;
  error: string | null;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData extends LoginCredentials {
  name: string;
  department: string;
  role?: string;
}