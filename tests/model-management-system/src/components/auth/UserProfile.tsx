import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { 
  User, Mail, Building, Shield, Calendar, Activity, 
  TrendingUp, CheckCircle, Edit2, Save, X 
} from 'lucide-react';

const UserProfile: React.FC = () => {
  const { user, updateUser } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState({
    name: user?.name || '',
    department: user?.department || '',
    emailNotifications: user?.preferences.emailNotifications || false,
    theme: user?.preferences.theme || 'light'
  });

  if (!user) return null;

  const handleSave = () => {
    updateUser({
      name: editData.name,
      department: editData.department,
      preferences: {
        ...user.preferences,
        emailNotifications: editData.emailNotifications,
        theme: editData.theme as 'light' | 'dark'
      }
    });
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditData({
      name: user.name,
      department: user.department,
      emailNotifications: user.preferences.emailNotifications,
      theme: user.preferences.theme
    });
    setIsEditing(false);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">User Profile</h1>
        <p className="text-gray-600 mt-2">Manage your account settings and preferences</p>
      </div>

      {/* Profile Header */}
      <div className="bg-white rounded-lg shadow">
        <div className="bg-gradient-to-r from-purple-600 to-blue-600 h-32 rounded-t-lg"></div>
        <div className="px-6 pb-6">
          <div className="flex items-end -mt-16 mb-4">
            <div className="bg-white rounded-full p-2">
              {user.avatar ? (
                <img src={user.avatar} alt={user.name} className="w-24 h-24 rounded-full" />
              ) : (
                <div className="w-24 h-24 bg-gray-200 rounded-full flex items-center justify-center">
                  <User className="w-12 h-12 text-gray-500" />
                </div>
              )}
            </div>
            <div className="ml-4 flex-1">
              <h2 className="text-2xl font-bold text-gray-900">{user.name}</h2>
              <div className="flex items-center gap-4 text-sm text-gray-600 mt-1">
                <span className="flex items-center gap-1">
                  <Mail className="w-4 h-4" />
                  {user.email}
                </span>
                <span className="flex items-center gap-1">
                  <Building className="w-4 h-4" />
                  {user.department}
                </span>
                <span className="flex items-center gap-1">
                  <Shield className="w-4 h-4" />
                  <span className="capitalize">{user.role}</span>
                </span>
              </div>
            </div>
            {!isEditing && (
              <button
                onClick={() => setIsEditing(true)}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center gap-2"
              >
                <Edit2 className="w-4 h-4" />
                Edit Profile
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Edit Form */}
      {isEditing && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Edit Profile</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
              <input
                type="text"
                value={editData.name}
                onChange={(e) => setEditData({ ...editData, name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Department</label>
              <input
                type="text"
                value={editData.department}
                onChange={(e) => setEditData({ ...editData, department: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Theme</label>
              <select
                value={editData.theme}
                onChange={(e) => setEditData({ ...editData, theme: e.target.value as 'light' | 'dark' })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              >
                <option value="light">Light</option>
                <option value="dark">Dark</option>
              </select>
            </div>
            <div className="flex items-center">
              <input
                type="checkbox"
                id="emailNotifications"
                checked={editData.emailNotifications}
                onChange={(e) => setEditData({ ...editData, emailNotifications: e.target.checked })}
                className="mr-2"
              />
              <label htmlFor="emailNotifications" className="text-sm font-medium text-gray-700">
                Email Notifications
              </label>
            </div>
          </div>
          <div className="flex gap-3 mt-6">
            <button
              onClick={handleSave}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
            >
              <Save className="w-4 h-4" />
              Save Changes
            </button>
            <button
              onClick={handleCancel}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2"
            >
              <X className="w-4 h-4" />
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">My Requests</h3>
            <Activity className="w-5 h-5 text-purple-600" />
          </div>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Total</span>
              <span className="font-semibold">{user.statistics.totalRequests}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Completed</span>
              <span className="font-semibold text-green-600">{user.statistics.completedRequests}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Pending</span>
              <span className="font-semibold text-yellow-600">{user.statistics.pendingRequests}</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Performance</h3>
            <TrendingUp className="w-5 h-5 text-green-600" />
          </div>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Models Created</span>
              <span className="font-semibold">{user.statistics.modelsCreated}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Success Rate</span>
              <span className="font-semibold text-green-600">{user.statistics.successRate}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Avg Time</span>
              <span className="font-semibold">{user.statistics.averageCalibrationTime}h</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Account Info</h3>
            <Calendar className="w-5 h-5 text-blue-600" />
          </div>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Member Since</span>
              <span className="font-semibold">
                {new Date(user.createdAt).toLocaleDateString()}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Last Login</span>
              <span className="font-semibold">
                {new Date(user.lastLogin).toLocaleTimeString()}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Status</span>
              <span className="font-semibold text-green-600">Active</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {user.preferences.recentProjects.map((projectId, index) => (
              <div key={projectId} className="flex items-center gap-3">
                <div className={`w-2 h-2 rounded-full ${index === 0 ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">
                    Worked on {projectId}
                  </p>
                  <p className="text-xs text-gray-500">
                    {index === 0 ? 'Currently active' : `${index + 1} days ago`}
                  </p>
                </div>
                {index === 0 && <CheckCircle className="w-5 h-5 text-green-500" />}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Favorite Models */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Favorite Models</h3>
        </div>
        <div className="p-6">
          {user.preferences.favoriteModels.length > 0 ? (
            <div className="grid grid-cols-2 gap-4">
              {user.preferences.favoriteModels.map((modelId) => (
                <div key={modelId} className="border border-gray-200 rounded-lg p-3">
                  <p className="font-medium text-gray-900">{modelId}</p>
                  <p className="text-sm text-gray-500">Last used 2 days ago</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">No favorite models yet</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default UserProfile;