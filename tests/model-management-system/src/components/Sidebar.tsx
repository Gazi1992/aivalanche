import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import Logo from './Logo';
import { ICONS, getIconSizeClass } from './ui/Icons';

interface SidebarProps {
  activeSection: string;
  onSectionChange: (section: string) => void;
  onNewRequest: () => void;
  onUploadData: () => void;
  onShowUserGuide?: () => void;
  onShowSupport?: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ activeSection, onSectionChange, onNewRequest, onUploadData, onShowUserGuide, onShowSupport }) => {
  const { user, logout } = useAuth();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const menuItems = [
    { id: 'dashboard', name: 'Dashboard', icon: ICONS.dashboard },
    { id: 'my-models', name: 'My Models', icon: ICONS.myModels },
    { id: 'libraries', name: 'Libraries', icon: ICONS.libraries },
    { id: 'requests', name: 'Requests', icon: ICONS.requests },
    { id: 'reports', name: 'Reports', icon: ICONS.reports },
    // { id: 'profile', name: 'Profile', icon: ICONS.profile }, // Hidden for now
    { id: 'settings', name: 'Settings', icon: ICONS.settings },
  ];

  return (
    <div 
      className={`bg-gray-900 text-white ${isCollapsed ? 'w-28' : 'w-64'} h-screen sticky top-0 p-4 flex flex-col transition-all duration-300 relative`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Toggle arrow that appears on hover */}
      {isHovered && (
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="absolute top-4 right-2 p-1.5 text-gray-400 hover:text-white transition-all duration-200 z-10"
        >
          {isCollapsed ? <ICONS.chevronRight className="w-3 h-3" /> : <ICONS.chevronLeft className="w-3 h-3" />}
        </button>
      )}
      
      {/* Logo Section */}
      <div className="mb-10 mt-8">
        <div className="flex flex-col">
          <div className={`flex items-center ${isCollapsed ? 'justify-center' : 'gap-3'}`}>
            <Logo size="medium" />
            {!isCollapsed && (
              <div className="flex-1">
                <h1 className="text-base font-bold text-white leading-tight">Model Management & Calibration</h1>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Subtle divider line */}
      <div className="mb-10 px-4">
        <div className="h-px bg-gradient-to-r from-transparent via-gray-700 to-transparent"></div>
      </div>

      {/* User Info Section - Moved to top */}
      {user && (
        <div className={`bg-gray-800 rounded-lg ${isCollapsed ? 'p-2' : 'p-4'} mb-6`}>
          {isCollapsed ? (
            <div className="flex flex-col items-center">
              {user.avatar ? (
                <img src={user.avatar} alt={user.name} className="w-10 h-10 rounded-full" />
              ) : (
                <div className="w-10 h-10 bg-gray-600 rounded-full flex items-center justify-center">
                  <ICONS.user className="w-5 h-5 text-gray-300" />
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center gap-3">
              {user.avatar ? (
                <img src={user.avatar} alt={user.name} className="w-10 h-10 rounded-full" />
              ) : (
                <div className="w-10 h-10 bg-gray-600 rounded-full flex items-center justify-center">
                  <ICONS.user className="w-5 h-5 text-gray-300" />
                </div>
              )}
              <div className="flex-1">
                <p className="text-sm font-medium">{user.name}</p>
                <p className="text-xs text-gray-400 capitalize">{user.role}</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Navigation Menu */}
      <nav className="space-y-1 flex-1">
        {menuItems.map((item) => {
          const Icon = item.icon;
          return (
            <button
              key={item.id}
              onClick={() => onSectionChange(item.id)}
              className={`w-full ${isCollapsed ? 'px-3' : 'px-4'} py-3 rounded-lg flex items-center ${isCollapsed ? 'justify-center' : 'gap-3'} transition-colors ${
                activeSection === item.id
                  ? 'bg-purple-600 text-white'
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
              }`}
              title={isCollapsed ? item.name : undefined}
            >
              <Icon className="w-5 h-5" />
              {!isCollapsed && <span className="font-medium">{item.name}</span>}
            </button>
          );
        })}
      </nav>

      {/* Bottom Section - Support, User Guide and Logout */}
      <div className="space-y-2 mt-auto">
        {/* Contact Support Button */}
        {onShowSupport && (
          <button
            onClick={onShowSupport}
            className={`w-full ${isCollapsed ? 'px-3' : 'px-4'} py-3 rounded-lg flex items-center ${isCollapsed ? 'justify-center' : 'gap-3'} transition-colors text-gray-300 hover:bg-gray-800 hover:text-white`}
            title={isCollapsed ? "Contact Support" : undefined}
          >
            <ICONS.contactSupport className="w-5 h-5" />
            {!isCollapsed && <span className="font-medium">Contact Support</span>}
          </button>
        )}
        
        {/* User Guide Button */}
        {onShowUserGuide && (
          <button
            onClick={onShowUserGuide}
            className={`w-full ${isCollapsed ? 'px-3' : 'px-4'} py-3 rounded-lg flex items-center ${isCollapsed ? 'justify-center' : 'gap-3'} transition-colors text-gray-300 hover:bg-gray-800 hover:text-white`}
            title={isCollapsed ? "User Guide" : undefined}
          >
            <ICONS.userGuide className="w-5 h-5" />
            {!isCollapsed && <span className="font-medium">User Guide</span>}
          </button>
        )}
        
        {/* Logout Button */}
        {user && (
          <button
            onClick={logout}
            className={`w-full ${isCollapsed ? 'px-3' : 'px-4'} py-3 bg-red-600 hover:bg-red-700 rounded-lg flex items-center ${isCollapsed ? 'justify-center' : 'gap-3'} transition-colors`}
            title={isCollapsed ? "Logout" : undefined}
          >
            <ICONS.logout className="w-5 h-5" />
            {!isCollapsed && <span className="font-medium">Logout</span>}
          </button>
        )}
      </div>
    </div>
  );
};

export default Sidebar;