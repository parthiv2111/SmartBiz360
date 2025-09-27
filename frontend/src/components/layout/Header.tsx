import React, { useState } from 'react';
import { 
  Search, 
  Bell, 
  LogOut, 
  Sun, 
  Moon
} from 'lucide-react';
import { useApp } from '../../contexts/AppContext';

const Header: React.FC = () => {
  const { state, dispatch, logout } = useApp();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const toggleTheme = () => {
    const newTheme = state.theme === 'light' ? 'dark' : 'light';
    dispatch({ type: 'SET_THEME', payload: newTheme });
  };

  const handleLogout = () => {
    logout();
    setShowUserMenu(false);
  };

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4 transition-all duration-300 dark:bg-gradient-to-r dark:from-slate-800/80 dark:via-slate-800/60 dark:to-slate-900/80 dark:border-slate-700/30 backdrop-blur-xl">
      <div className="flex items-center justify-between">
        {/* Left side - Search */}
        <div className="flex-1 max-w-md">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-slate-400" />
            <input
              type="text"
              placeholder="Search..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input-field pl-12 pr-4 py-3"
            />
          </div>
        </div>

        {/* Right side - Actions */}
        <div className="flex items-center space-x-4">
          {/* Theme toggle */}
          <button
            onClick={toggleTheme}
            className="p-3 rounded-xl hover:bg-gray-100 dark:hover:bg-gradient-to-r dark:hover:from-slate-700/50 dark:hover:to-slate-600/50 transition-all duration-300 dark:backdrop-blur-sm premium-hover"
            title={`Switch to ${state.theme === 'light' ? 'dark' : 'light'} mode`}
          >
            {state.theme === 'light' ? (
              <Moon className="w-5 h-5 text-gray-600 dark:text-slate-300" />
            ) : (
              <Sun className="w-5 h-5 text-slate-300" />
            )}
          </button>

          {/* Notifications */}
          <button className="relative p-3 rounded-xl hover:bg-gray-100 dark:hover:bg-gradient-to-r dark:hover:from-slate-700/50 dark:hover:to-slate-600/50 transition-all duration-300 dark:backdrop-blur-sm premium-hover">
            <Bell className="w-5 h-5 text-gray-600 dark:text-slate-300" />
            {state.notifications.length > 0 && (
              <span className="absolute -top-1 -right-1 w-5 h-5 bg-gradient-to-r from-red-500 to-pink-500 text-white text-xs rounded-full flex items-center justify-center shadow-lg">
                {state.notifications.length}
              </span>
            )}
          </button>

          {/* User menu */}
          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center space-x-3 p-3 rounded-xl hover:bg-gray-100 dark:hover:bg-gradient-to-r dark:hover:from-slate-700/50 dark:hover:to-slate-600/50 transition-all duration-300 dark:backdrop-blur-sm premium-hover"
            >
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg">
                <span className="text-white font-medium text-sm">
                {state.user?.name?.charAt(0)?.toUpperCase() || 'U'}
                </span>
              </div>
              {state.user && (
                <span className="hidden md:block text-sm font-medium text-gray-700 dark:text-slate-300">
                  {state.user.name}
                </span>
              )}
            </button>

            {/* User dropdown */}
            {showUserMenu && (
              <div className="absolute right-0 mt-3 w-56 bg-white dark:bg-gradient-to-br dark:from-slate-800/90 dark:via-slate-800/80 dark:to-slate-900/90 rounded-2xl shadow-2xl border border-gray-200 dark:border-slate-700/30 py-3 z-50 backdrop-blur-xl">
                <div className="px-4 py-3 border-b border-gray-100 dark:border-slate-700/30">
                <p className="text-sm font-medium text-gray-900 dark:text-slate-100 truncate">
                  {`${state.user?.first_name || ''} ${state.user?.last_name || ''}`.trim() || 'User'}
                </p>
                <p className="text-xs text-gray-500 dark:text-slate-400 truncate">
                  {state.user?.email || 'user@example.com'}
                </p>
                </div>
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center space-x-3 px-4 py-3 text-sm text-gray-700 dark:text-slate-300 hover:bg-gray-50 dark:hover:bg-gradient-to-r dark:hover:from-slate-700/50 dark:hover:to-slate-600/50 transition-all duration-300"
                >
                  <LogOut className="w-4 h-4" />
                  <span>Sign out</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
