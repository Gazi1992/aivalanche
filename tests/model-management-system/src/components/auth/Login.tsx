import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Mail, Lock, User, Building, LogIn, UserPlus } from 'lucide-react';
import { Icon } from '../ui/Icons';
import Logo from '../Logo';
import UserGuide from '../UserGuide';

const Login: React.FC = () => {
  const { login, register, error } = useAuth();
  const [isRegister, setIsRegister] = useState(false);
  const [loading, setLoading] = useState(false);
  const [showUserGuide, setShowUserGuide] = useState(false);
  const [formData, setFormData] = useState({
    email: 'john.doe@company.com',
    password: 'password123',
    name: '',
    department: '',
    role: 'engineer'
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      if (isRegister) {
        await register({
          email: formData.email,
          password: formData.password,
          name: formData.name,
          department: formData.department,
          role: formData.role
        });
      } else {
        await login({
          email: formData.email,
          password: formData.password
        });
      }
    } catch (err) {
      console.error('Auth error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center p-4 relative">
      {/* User Guide Button - Fixed Position */}
      <button
        onClick={() => setShowUserGuide(true)}
        className="absolute top-6 right-6 bg-white/10 backdrop-blur-sm text-white px-4 py-2 rounded-lg hover:bg-white/20 transition-colors flex items-center gap-2 border border-white/20"
      >
        <Icon name="userGuide" size="md" />
        <span className="font-medium">User Guide</span>
      </button>

      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg p-8">
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <Logo size="large" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Model Management & Calibration</h1>
          <p className="text-gray-600 mt-2">
            {isRegister ? 'Create your account' : 'Sign in to your account'}
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4" autoComplete={isRegister ? "off" : "on"}>
          {isRegister && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Full Name
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="John Doe"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Department
                </label>
                <div className="relative">
                  <Building className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <input
                    type="text"
                    name="department"
                    value={formData.department}
                    onChange={handleInputChange}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="Device Modeling"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Role
                </label>
                <select
                  name="role"
                  value={formData.role}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="engineer">Engineer</option>
                  <option value="manager">Manager</option>
                  <option value="viewer">Viewer</option>
                </select>
              </div>
            </>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email Address
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="john.doe@company.com"
                autoComplete="username email"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="••••••••"
                autoComplete={isRegister ? "new-password" : "current-password"}
                required
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white py-3 rounded-lg font-medium hover:from-purple-700 hover:to-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <span>Processing...</span>
            ) : (
              <>
                {isRegister ? <UserPlus className="w-5 h-5" /> : <LogIn className="w-5 h-5" />}
                {isRegister ? 'Create Account' : 'Sign In'}
              </>
            )}
          </button>
        </form>

        <div className="mt-6 text-center">
          <button
            onClick={() => {
              setIsRegister(!isRegister);
              if (!isRegister) {
                // Clear pre-filled credentials when switching to register
                setFormData({
                  email: '',
                  password: '',
                  name: '',
                  department: '',
                  role: 'engineer'
                });
              } else {
                // Restore engineer credentials when switching back to login
                setFormData({
                  email: 'john.doe@company.com',
                  password: 'password123',
                  name: '',
                  department: '',
                  role: 'engineer'
                });
              }
            }}
            className="text-purple-600 hover:text-purple-700 font-medium"
          >
            {isRegister
              ? 'Already have an account? Sign in'
              : "Don't have an account? Sign up"}
          </button>
          
          <div className="mt-4">
            <button
              onClick={() => setShowUserGuide(true)}
              className="text-gray-500 hover:text-gray-700 text-sm font-medium flex items-center gap-1 mx-auto justify-center"
            >
              <Icon name="userGuide" size="sm" />
              Need help? View User Guide
            </button>
          </div>
        </div>

        {!isRegister && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <p className="text-sm text-gray-600 text-center mb-3">Demo Accounts:</p>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between bg-gray-50 p-2 rounded">
                <span>Engineer:</span>
                <span className="font-mono">john.doe@company.com / password123</span>
              </div>
              <div className="flex justify-between bg-gray-50 p-2 rounded">
                <span>Manager:</span>
                <span className="font-mono">jane.smith@company.com / password123</span>
              </div>
              <div className="flex justify-between bg-gray-50 p-2 rounded">
                <span>Admin:</span>
                <span className="font-mono">admin@company.com / admin123</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* User Guide Modal */}
      <UserGuide isOpen={showUserGuide} onClose={() => setShowUserGuide(false)} />
    </div>
  );
};

export default Login;