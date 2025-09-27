import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { 
  Home, 
  BarChart3, 
  Users, 
  Package, 
  ShoppingCart, 
  Settings, 
  ChevronLeft,
  Building2,
  LogOut
} from 'lucide-react';
import { useApp } from '../../contexts/AppContext';

const Sidebar: React.FC = () => {
  const { state, dispatch, logout } = useApp();
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/', icon: Home },
    { name: 'Analytics', href: '/analytics', icon: BarChart3 },
    { name: 'Customers', href: '/customers', icon: Users },
    { name: 'Products', href: '/products', icon: Package },
    { name: 'Orders', href: '/orders', icon: ShoppingCart },
    { name: 'Settings', href: '/settings', icon: Settings },
  ];

  const toggleSidebar = () => {
    dispatch({ type: 'TOGGLE_SIDEBAR' });
  };

  return (
    <div className={`fixed left-0 top-0 h-full bg-white border-r border-gray-200 transition-all duration-300 z-30 dark:bg-gradient-to-b dark:from-slate-800/90 dark:via-slate-800/80 dark:to-slate-900/90 dark:border-slate-700/30 backdrop-blur-xl ${
      state.sidebarCollapsed ? 'w-16' : 'w-64'
    } ${state.sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
      {/* Logo */}
      <div className="flex items-center justify-between h-16 px-4 border-b border-gray-200 dark:border-slate-700/30">
        {!state.sidebarCollapsed && (
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
              <Building2 className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900 dark:text-slate-100">SmartBiz360</span>
          </div>
        )}
        <button
          onClick={toggleSidebar}
          className="p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gradient-to-r dark:hover:from-slate-700/50 dark:hover:to-slate-600/50 transition-all duration-300 dark:backdrop-blur-sm premium-hover"
        >
          <ChevronLeft className={`w-5 h-5 text-gray-500 dark:text-slate-400 transition-transform ${
            state.sidebarCollapsed ? 'rotate-180' : ''
          }`} />
        </button>
      </div>

      {/* Navigation */}
      <nav className="mt-6 px-3">
        <ul className="space-y-2">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href;
            return (
              <li key={item.name}>
                <NavLink
                  to={item.href}
                  className={`sidebar-item ${isActive ? 'active' : ''}`}
                  title={state.sidebarCollapsed ? item.name : undefined}
                >
                  <item.icon className="w-5 h-5 sidebar-icon" />
                  {!state.sidebarCollapsed && (
                    <span className="font-medium">{item.name}</span>
                  )}
                </NavLink>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* User info and logout */}
      {state.user && (
        <div className="absolute bottom-6 left-3 right-3">
          <div className="card p-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg">
                <span className="text-white font-medium text-sm">
                  {state.user?.first_name?.charAt(0)?.toUpperCase() || 'U'}
                </span>
              </div>
              {!state.sidebarCollapsed && (
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 dark:text-slate-100 truncate">
                    {`${state.user?.first_name || ''} ${state.user?.last_name || ''}`.trim() || 'User'}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-slate-400 truncate">
                    {state.user?.email || 'user@example.com'}
                  </p>
                </div>
              )}
              <button
                onClick={logout}
                className="p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gradient-to-r dark:hover:from-slate-700/50 dark:hover:to-slate-600/50 transition-all duration-300 dark:backdrop-blur-sm premium-hover"
                title={state.sidebarCollapsed ? "Sign out" : undefined}
              >
                <LogOut className="w-4 h-4 text-gray-500 dark:text-slate-400" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Sidebar;
