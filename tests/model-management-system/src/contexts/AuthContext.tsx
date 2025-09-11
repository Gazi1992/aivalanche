import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, LoginCredentials, RegisterData, AuthState } from '../types/user';

interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  register: (data: RegisterData) => Promise<void>;
  updateUser: (updates: Partial<User>) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Mock users for demo
const mockUsers: { [key: string]: User & { password: string } } = {
  'john.doe@company.com': {
    id: 'user-001',
    email: 'john.doe@company.com',
    password: 'password123',
    name: 'John Doe',
    department: 'Device Modeling',
    role: 'admin',
    avatar: 'https://ui-avatars.com/api/?name=John+Doe&background=667eea&color=fff',
    preferences: {
      theme: 'light',
      defaultView: 'dashboard',
      emailNotifications: true,
      dashboardLayout: ['workflow', 'requests', 'statistics'],
      favoriteModels: ['MOD-BSIM4-001', 'MOD-PSP-001'],
      recentProjects: ['REQ-2025-001', 'REQ-2025-002']
    },
    statistics: {
      totalRequests: 45,
      completedRequests: 38,
      pendingRequests: 7,
      modelsCreated: 28,
      averageCalibrationTime: 4.2,
      successRate: 96.5
    },
    createdAt: '2023-01-15T10:00:00Z',
    lastLogin: '2025-01-11T09:00:00Z'
  },
  'jane.smith@company.com': {
    id: 'user-002',
    email: 'jane.smith@company.com',
    password: 'password123',
    name: 'Jane Smith',
    department: 'Analog Design',
    role: 'manager',
    avatar: 'https://ui-avatars.com/api/?name=Jane+Smith&background=764ba2&color=fff',
    preferences: {
      theme: 'dark',
      defaultView: 'libraries',
      emailNotifications: true,
      dashboardLayout: ['statistics', 'workflow', 'team'],
      favoriteModels: ['MOD-DIODE-001'],
      recentProjects: ['REQ-2025-002', 'REQ-2025-003']
    },
    statistics: {
      totalRequests: 120,
      completedRequests: 115,
      pendingRequests: 5,
      modelsCreated: 67,
      averageCalibrationTime: 3.8,
      successRate: 98.2
    },
    createdAt: '2022-06-10T10:00:00Z',
    lastLogin: '2025-01-11T08:30:00Z'
  },
  'admin@company.com': {
    id: 'user-admin',
    email: 'admin@company.com',
    password: 'admin123',
    name: 'Admin User',
    department: 'IT',
    role: 'admin',
    avatar: 'https://ui-avatars.com/api/?name=Admin&background=dc3545&color=fff',
    preferences: {
      theme: 'light',
      defaultView: 'dashboard',
      emailNotifications: true,
      dashboardLayout: ['system', 'users', 'statistics'],
      favoriteModels: [],
      recentProjects: []
    },
    statistics: {
      totalRequests: 0,
      completedRequests: 0,
      pendingRequests: 0,
      modelsCreated: 0,
      averageCalibrationTime: 0,
      successRate: 0
    },
    createdAt: '2022-01-01T10:00:00Z',
    lastLogin: '2025-01-11T07:00:00Z'
  }
};

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    user: null,
    loading: false,
    error: null
  });

  // Check for saved session on mount
  useEffect(() => {
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
      const user = JSON.parse(savedUser);
      setAuthState({
        isAuthenticated: true,
        user,
        loading: false,
        error: null
      });
    }
  }, []);

  const login = async (credentials: LoginCredentials) => {
    setAuthState(prev => ({ ...prev, loading: true, error: null }));
    
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const userWithPassword = mockUsers[credentials.email];
    
    if (userWithPassword && userWithPassword.password === credentials.password) {
      const { password, ...user } = userWithPassword;
      user.lastLogin = new Date().toISOString();
      
      localStorage.setItem('currentUser', JSON.stringify(user));
      
      setAuthState({
        isAuthenticated: true,
        user,
        loading: false,
        error: null
      });
    } else {
      setAuthState({
        isAuthenticated: false,
        user: null,
        loading: false,
        error: 'Invalid email or password'
      });
      throw new Error('Invalid credentials');
    }
  };

  const logout = () => {
    localStorage.removeItem('currentUser');
    setAuthState({
      isAuthenticated: false,
      user: null,
      loading: false,
      error: null
    });
  };

  const register = async (data: RegisterData) => {
    setAuthState(prev => ({ ...prev, loading: true, error: null }));
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    if (mockUsers[data.email]) {
      setAuthState(prev => ({
        ...prev,
        loading: false,
        error: 'Email already exists'
      }));
      throw new Error('Email already exists');
    }
    
    const newUser: User = {
      id: `user-${Date.now()}`,
      email: data.email,
      name: data.name,
      department: data.department,
      role: (data.role as User['role']) || 'viewer',
      avatar: `https://ui-avatars.com/api/?name=${encodeURIComponent(data.name)}&background=667eea&color=fff`,
      preferences: {
        theme: 'light',
        defaultView: 'dashboard',
        emailNotifications: true,
        dashboardLayout: ['workflow', 'requests', 'statistics'],
        favoriteModels: [],
        recentProjects: []
      },
      statistics: {
        totalRequests: 0,
        completedRequests: 0,
        pendingRequests: 0,
        modelsCreated: 0,
        averageCalibrationTime: 0,
        successRate: 0
      },
      createdAt: new Date().toISOString(),
      lastLogin: new Date().toISOString()
    };
    
    // Add to mock users
    mockUsers[data.email] = { ...newUser, password: data.password };
    
    localStorage.setItem('currentUser', JSON.stringify(newUser));
    
    setAuthState({
      isAuthenticated: true,
      user: newUser,
      loading: false,
      error: null
    });
  };

  const updateUser = (updates: Partial<User>) => {
    if (authState.user) {
      const updatedUser = { ...authState.user, ...updates };
      localStorage.setItem('currentUser', JSON.stringify(updatedUser));
      setAuthState(prev => ({
        ...prev,
        user: updatedUser
      }));
    }
  };

  return (
    <AuthContext.Provider
      value={{
        ...authState,
        login,
        logout,
        register,
        updateUser
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};