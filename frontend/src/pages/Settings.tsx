import React, { useState, useEffect } from 'react';
import { User, Bell, Shield, Globe, Save, Upload } from 'lucide-react';
import { useApp } from '../contexts/AppContext';
import { settingsAPI, uploadAPI } from '../services/api';

const Settings: React.FC = () => {
  const { state, dispatch, addNotification } = useApp();
  const [activeTab, setActiveTab] = useState('profile');
  const [isSaving, setIsSaving] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const [profileData, setProfileData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    company: '',
    phone: ''
  });

  const [notificationSettings, setNotificationSettings] = useState({
    emailNotifications: true,
    pushNotifications: true,
    orderUpdates: true,
    marketingEmails: false,
    weeklyReports: true
  });

  const [securitySettings, setSecuritySettings] = useState({
    twoFactorAuth: false,
    sessionTimeout: '24h',
    passwordExpiry: '90d'
  });

  const [generalSettings, setGeneralSettings] = useState({
    language: 'en',
    timezone: 'UTC',
    theme: 'light'
  });

  // Load settings on component mount
  useEffect(() => {
    const loadSettings = async () => {
      try {
        setIsLoading(true);
        const [profileResponse, notificationsResponse, securityResponse, generalResponse] = await Promise.all([
          settingsAPI.getProfile(),
          settingsAPI.getNotifications(),
          settingsAPI.getSecurity(),
          settingsAPI.getGeneral()
        ]);

        if (profileResponse.success) {
          const profile = profileResponse.data.profile;
          setProfileData({
            firstName: profile.first_name || '',
            lastName: profile.last_name || '',
            email: profile.email || '',
            company: profile.company || '',
            phone: profile.phone || ''
          });
        }

        if (notificationsResponse.success) {
          setNotificationSettings(notificationsResponse.data.notifications);
        }

        if (securityResponse.success) {
          setSecuritySettings(securityResponse.data.security);
        }

        if (generalResponse.success) {
          setGeneralSettings(generalResponse.data.general);
        }
      } catch (error) {
        console.error('Failed to load settings:', error);
        addNotification('error', 'Failed to load settings');
      } finally {
        setIsLoading(false);
      }
    };

    loadSettings();
  }, [addNotification]);

  const tabs = [
    { id: 'profile', name: 'Profile', icon: User },
    { id: 'notifications', name: 'Notifications', icon: Bell },
    { id: 'security', name: 'Security', icon: Shield },
    { id: 'general', name: 'General', icon: Globe }
  ];

  const handleSave = async () => {
    setIsSaving(true);
    try {
      let success = true;
      
      if (activeTab === 'profile') {
        const response = await settingsAPI.updateProfile({
          first_name: profileData.firstName,
          last_name: profileData.lastName,
          email: profileData.email,
          company: profileData.company,
          phone: profileData.phone
        });
        success = response.success;
      } else if (activeTab === 'notifications') {
        const response = await settingsAPI.updateNotifications(notificationSettings);
        success = response.success;
      } else if (activeTab === 'security') {
        const response = await settingsAPI.updateSecurity(securitySettings);
        success = response.success;
      } else if (activeTab === 'general') {
        const response = await settingsAPI.updateGeneral(generalSettings);
        success = response.success;
      }
      
      if (success) {
        addNotification('success', 'Settings saved successfully');
      } else {
        addNotification('error', 'Failed to save settings');
      }
    } catch (error) {
      console.error('Save failed:', error);
      addNotification('error', 'Failed to save settings');
    } finally {
      setIsSaving(false);
    }
  };

  const handleAvatarUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      addNotification('error', 'Please select an image file');
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      addNotification('error', 'File size must be less than 5MB');
      return;
    }

    try {
      setIsSaving(true);
      const response = await uploadAPI.uploadAvatar(file);
      if (response.success && state.user) {
        addNotification('success', 'Avatar uploaded successfully');
        // Update user context with new avatar URL instantly
        dispatch({ 
          type: 'SET_USER', 
          payload: { ...state.user, avatar: response.data.avatar_url } 
        });
      } else {
        addNotification('error', 'Failed to upload avatar');
      }
    } catch (error) {
      console.error('Avatar upload failed:', error);
      addNotification('error', 'Failed to upload avatar');
    } finally {
      setIsSaving(false);
    }
  };

  const renderProfileTab = () => (
    <div className="space-y-6">
      <div className="card p-8">
        <div className="flex items-center space-x-3 mb-6">
          <div className="relative">
            <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
              {state.user?.avatar ? (
                <img 
                  src={uploadAPI.getFileUrl(state.user.avatar.split('/').pop()!)} 
                  alt="Avatar" 
                  className="w-12 h-12 rounded-xl object-cover"
                />
              ) : (
                <User className="w-6 h-6 text-white" />
              )}
            </div>
            <label className="absolute -bottom-1 -right-1 bg-blue-500 text-white rounded-full p-1 cursor-pointer hover:bg-blue-600 transition-colors">
              <Upload className="w-3 h-3" />
              <input
                type="file"
                accept="image/*"
                onChange={handleAvatarUpload}
                className="hidden"
              />
            </label>
          </div>
          <div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-slate-100">Personal Information</h3>
            <p className="text-sm text-gray-500 dark:text-slate-400">Manage your personal details and contact information</p>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-2">
              First Name
            </label>
            <input
              type="text"
              value={profileData.firstName}
              onChange={(e) => setProfileData(prev => ({ ...prev, firstName: e.target.value }))}
              className="input-field"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-2">
              Last Name
            </label>
            <input
              type="text"
              value={profileData.lastName}
              onChange={(e) => setProfileData(prev => ({ ...prev, lastName: e.target.value }))}
              className="input-field"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-2">
              Email
            </label>
            <input
              type="email"
              value={profileData.email}
              onChange={(e) => setProfileData(prev => ({ ...prev, email: e.target.value }))}
              className="input-field"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-2">
              Company
            </label>
            <input
              type="text"
              value={profileData.company}
              onChange={(e) => setProfileData(prev => ({ ...prev, company: e.target.value }))}
              className="input-field"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-2">
              Phone
            </label>
            <input
              type="tel"
              value={profileData.phone}
              onChange={(e) => setProfileData(prev => ({ ...prev, phone: e.target.value }))}
              className="input-field"
            />
          </div>
        </div>
      </div>
    </div>
  );

  const renderNotificationsTab = () => (
    <div className="space-y-6">
      <div className="card p-8">
        <div className="flex items-center space-x-3 mb-6">
          <div className="w-12 h-12 bg-gradient-to-r from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center shadow-lg">
            <Bell className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-slate-100">Notification Preferences</h3>
            <p className="text-sm text-gray-500 dark:text-slate-400">Customize how you receive notifications</p>
          </div>
        </div>
        <div className="space-y-6">
          {Object.entries(notificationSettings).map(([key, value]) => (
            <div key={key} className="flex items-center justify-between p-4 rounded-xl bg-gray-50 dark:bg-slate-800/30">
              <div>
                <label className="text-sm font-medium text-gray-900 dark:text-slate-100 capitalize">
                  {key.replace(/([A-Z])/g, ' $1').trim()}
                </label>
                <p className="text-sm text-gray-500 dark:text-slate-400 mt-1">
                  Receive notifications about {key.replace(/([A-Z])/g, ' $1').toLowerCase()}
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={value}
                  onChange={(e) => setNotificationSettings(prev => ({ ...prev, [key]: e.target.checked }))}
                  className="sr-only peer"
                />
                <div className="w-12 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-emerald-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-gradient-to-r peer-checked:from-emerald-500 peer-checked:to-teal-600 dark:bg-slate-600"></div>
              </label>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderSecurityTab = () => (
    <div className="space-y-6">
      <div className="card p-8">
        <div className="flex items-center space-x-3 mb-6">
          <div className="w-12 h-12 bg-gradient-to-r from-amber-500 to-orange-600 rounded-xl flex items-center justify-center shadow-lg">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-slate-100">Security Settings</h3>
            <p className="text-sm text-gray-500 dark:text-slate-400">Enhance your account security</p>
          </div>
        </div>
        <div className="space-y-6">
          <div className="flex items-center justify-between p-4 rounded-xl bg-gray-50 dark:bg-slate-800/30">
            <div>
              <label className="text-sm font-medium text-gray-900 dark:text-slate-100">Two-Factor Authentication</label>
              <p className="text-sm text-gray-500 dark:text-slate-400 mt-1">Add an extra layer of security to your account</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={securitySettings.twoFactorAuth}
                onChange={(e) => setSecuritySettings(prev => ({ ...prev, twoFactorAuth: e.target.checked }))}
                className="sr-only peer"
              />
              <div className="w-12 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-amber-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-gradient-to-r peer-checked:from-amber-500 peer-checked:to-orange-600 dark:bg-slate-600"></div>
            </label>
          </div>
          
          <div className="p-4 rounded-xl bg-gray-50 dark:bg-slate-800/30">
            <label className="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-2">
              Session Timeout
            </label>
            <select
              value={securitySettings.sessionTimeout}
              onChange={(e) => setSecuritySettings(prev => ({ ...prev, sessionTimeout: e.target.value }))}
              className="input-field"
            >
              <option value="1h">1 hour</option>
              <option value="8h">8 hours</option>
              <option value="24h">24 hours</option>
              <option value="7d">7 days</option>
            </select>
          </div>
          
          <div className="p-4 rounded-xl bg-gray-50 dark:bg-slate-800/30">
            <label className="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-2">
              Password Expiry
            </label>
            <select
              value={securitySettings.passwordExpiry}
              onChange={(e) => setSecuritySettings(prev => ({ ...prev, passwordExpiry: e.target.value }))}
              className="input-field"
            >
              <option value="30d">30 days</option>
              <option value="60d">60 days</option>
              <option value="90d">90 days</option>
              <option value="180d">180 days</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );

  const renderGeneralTab = () => (
    <div className="space-y-6">
      <div className="card p-8">
        <div className="flex items-center space-x-3 mb-6">
          <div className="w-12 h-12 bg-gradient-to-r from-slate-500 to-gray-600 rounded-xl flex items-center justify-center shadow-lg">
            <Globe className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-slate-100">General Settings</h3>
            <p className="text-sm text-gray-500 dark:text-slate-400">Configure your general preferences</p>
          </div>
        </div>
        <div className="space-y-6">
          <div className="p-4 rounded-xl bg-gray-50 dark:bg-slate-800/30">
            <label className="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-2">
              Language
            </label>
            <select 
              className="input-field"
              value={generalSettings.language}
              onChange={(e) => setGeneralSettings(prev => ({ ...prev, language: e.target.value }))}
            >
              <option value="en">English</option>
              <option value="es">Spanish</option>
              <option value="fr">French</option>
              <option value="de">German</option>
            </select>
          </div>
          
          <div className="p-4 rounded-xl bg-gray-50 dark:bg-slate-800/30">
            <label className="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-2">
              Timezone
            </label>
            <select 
              className="input-field"
              value={generalSettings.timezone}
              onChange={(e) => setGeneralSettings(prev => ({ ...prev, timezone: e.target.value }))}
            >
              <option value="UTC">UTC</option>
              <option value="EST">Eastern Time</option>
              <option value="PST">Pacific Time</option>
              <option value="GMT">GMT</option>
            </select>
          </div>

          <div className="p-4 rounded-xl bg-gray-50 dark:bg-slate-800/30">
            <label className="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-2">
              Theme
            </label>
            <select 
              className="input-field"
              value={generalSettings.theme}
              onChange={(e) => {
                const newTheme = e.target.value as 'light' | 'dark';
                setGeneralSettings(prev => ({ ...prev, theme: newTheme }));
                dispatch({ type: 'SET_THEME', payload: newTheme });
              }}
            >
              <option value="light">Light</option>
              <option value="dark">Dark</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'profile':
        return renderProfileTab();
      case 'notifications':
        return renderNotificationsTab();
      case 'security':
        return renderSecurityTab();
      case 'general':
        return renderGeneralTab();
      default:
        return renderProfileTab();
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-slate-100 mb-3">Settings</h1>
          <p className="text-lg text-gray-600 dark:text-slate-400 max-w-2xl mx-auto">Manage your account preferences and settings to customize your SmartBiz360 experience</p>
        </div>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Page header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-slate-100 mb-3">Settings</h1>
        <p className="text-lg text-gray-600 dark:text-slate-400 max-w-2xl mx-auto">Manage your account preferences and settings to customize your SmartBiz360 experience</p>
      </div>

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Sidebar */}
        <div className="lg:w-72">
          <div className="card sticky top-6">
            <nav className="p-6">
              <ul className="space-y-2">
                {tabs.map((tab) => {
                  const Icon = tab.icon;
                  return (
                    <li key={tab.id}>
                      <button
                        onClick={() => setActiveTab(tab.id)}
                        className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-xl transition-all duration-300 ${
                          activeTab === tab.id
                            ? 'bg-gradient-to-r from-blue-500/20 via-blue-500/20 to-purple-500/20 text-blue-600 dark:text-blue-400 shadow-lg'
                            : 'text-gray-700 hover:bg-gray-50 dark:text-slate-300 dark:hover:bg-gradient-to-r dark:hover:from-slate-700/50 dark:hover:to-slate-600/50'
                        }`}
                      >
                        <Icon className="w-5 h-5 mr-3" />
                        {tab.name}
                      </button>
                    </li>
                  );
                })}
              </ul>
            </nav>
          </div>
        </div>

        {/* Main content */}
        <div className="flex-1">
          {renderTabContent()}
          
          {/* Save button */}
          <div className="mt-8 flex justify-center">
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="btn-primary flex items-center px-8 py-4 text-lg"
            >
              {isSaving ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
              ) : (
                <Save className="w-5 h-5 mr-3" />
              )}
              Save Changes
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;