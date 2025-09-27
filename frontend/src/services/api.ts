import config from '../config/config';

const API_BASE_URL = config.API_BASE_URL;

// Get auth token from localStorage
const getAuthToken = (): string | null => {
  return localStorage.getItem('access_token');
};

// Generic API request function
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const token = getAuthToken();
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, defaultOptions);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error(`API request failed for ${endpoint}:`, error);
    throw error;
  }
}

// Generic API request function for file uploads
async function apiFileUpload<T>(
  endpoint: string,
  file: File,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const token = getAuthToken();
  const formData = new FormData();
  formData.append('file', file);
  
  const defaultOptions: RequestInit = {
    method: 'POST',
    headers: {
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers,
    },
    body: formData,
    ...options,
  };

  try {
    const response = await fetch(url, defaultOptions);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error(`File upload failed for ${endpoint}:`, error);
    throw error;
  }
}

// Products API
export const productsAPI = {
  getAll: (params?: { page?: number; per_page?: number; search?: string; category?: string; status?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.append('page', params.page.toString());
    if (params?.per_page) searchParams.append('per_page', params.per_page.toString());
    if (params?.search) searchParams.append('search', params.search);
    if (params?.category) searchParams.append('category', params.category);
    if (params?.status) searchParams.append('status', params.status);
    
    const queryString = searchParams.toString();
    const endpoint = `/products${queryString ? `?${queryString}` : ''}`;
    
    return apiRequest<{
      success: boolean;
      data: any[];
      pagination: {
        page: number;
        per_page: number;
        total: number;
        pages: number;
        has_next: boolean;
        has_prev: boolean;
      };
    }>(endpoint);
  },

  getById: (id: string) => 
    apiRequest<{ success: boolean; data: any }>(`/products/${id}`),

  create: (productData: any) => 
    apiRequest<{ success: boolean; message: string; data: any }>('/products', {
      method: 'POST',
      body: JSON.stringify(productData),
    }),

  update: (id: string, productData: any) => 
    apiRequest<{ success: boolean; message: string; data: any }>(`/products/${id}`, {
      method: 'PUT',
      body: JSON.stringify(productData),
    }),

  delete: (id: string) => 
    apiRequest<{ success: boolean; message: string }>(`/products/${id}`, {
      method: 'DELETE',
    }),

  getStats: () => 
    apiRequest<{ success: boolean; data: any }>('/products/stats'),
};

// Customers API
export const customersAPI = {
  getAll: (params?: { page?: number; per_page?: number; search?: string; status?: string; company?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.append('page', params.page.toString());
    if (params?.per_page) searchParams.append('per_page', params.per_page.toString());
    if (params?.search) searchParams.append('search', params.search);
    if (params?.status) searchParams.append('status', params.status);
    if (params?.company) searchParams.append('company', params.company);
    
    const queryString = searchParams.toString();
    const endpoint = `/customers${queryString ? `?${queryString}` : ''}`;
    
    return apiRequest<{
      success: boolean;
      data: any[];
      pagination: {
        page: number;
        per_page: number;
        total: number;
        pages: number;
        has_next: boolean;
        has_prev: boolean;
      };
    }>(endpoint);
  },

  getById: (id: string) => 
    apiRequest<{ success: boolean; data: any }>(`/customers/${id}`),

  create: (customerData: any) => 
    apiRequest<{ success: boolean; message: string; data: any }>('/customers', {
      method: 'POST',
      body: JSON.stringify(customerData),
    }),

  update: (id: string, customerData: any) => 
    apiRequest<{ success: boolean; message: string; data: any }>(`/customers/${id}`, {
      method: 'PUT',
      body: JSON.stringify(customerData),
    }),

  delete: (id: string) => 
    apiRequest<{ success: boolean; message: string }>(`/customers/${id}`, {
      method: 'DELETE',
    }),

  getStats: () => 
    apiRequest<{ success: boolean; data: any }>('/customers/stats'),
};

// Orders API
export const ordersAPI = {
  getAll: (params?: { page?: number; per_page?: number; search?: string; status?: string; customer_id?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.append('page', params.page.toString());
    if (params?.per_page) searchParams.append('per_page', params.per_page.toString());
    if (params?.search) searchParams.append('search', params.search);
    if (params?.status) searchParams.append('status', params.status);
    if (params?.customer_id) searchParams.append('customer_id', params.customer_id);
    
    const queryString = searchParams.toString();
    const endpoint = `/orders${queryString ? `?${queryString}` : ''}`;
    
    return apiRequest<{
      success: boolean;
      data: any[];
      pagination: {
        page: number;
        per_page: number;
        total: number;
        pages: number;
        has_next: boolean;
        has_prev: boolean;
      };
    }>(endpoint);
  },

  getById: (id: string) => 
    apiRequest<{ success: boolean; data: any }>(`/orders/${id}`),

  create: (orderData: any) => 
    apiRequest<{ success: boolean; message: string; data: any }>('/orders', {
      method: 'POST',
      body: JSON.stringify(orderData),
    }),

  update: (id: string, orderData: any) => 
    apiRequest<{ success: boolean; message: string; data: any }>(`/orders/${id}`, {
      method: 'PUT',
      body: JSON.stringify(orderData),
    }),

  delete: (id: string) => 
    apiRequest<{ success: boolean; message: string }>(`/orders/${id}`, {
      method: 'DELETE',
    }),

  getStats: () => 
    apiRequest<{ success: boolean; data: any }>('/orders/stats'),
};

// Dashboard API
export const dashboardAPI = {
  getStats: () => 
    apiRequest<{ success: boolean; data: any }>('/dashboard/stats'),

  getRevenueTrends: () => 
    apiRequest<{ success: boolean; data: any[] }>('/dashboard/revenue-trends'),

  getCustomerGrowth: () => 
    apiRequest<{ success: boolean; data: any[] }>('/dashboard/customer-growth'),

  getPerformanceMetrics: () => 
    apiRequest<{ success: boolean; data: any }>('/dashboard/performance-metrics'),
};

// Analytics API
export const analyticsAPI = {
  getOverview: () => 
    apiRequest<{ success: boolean; data: any }>('/analytics/overview'),

  getRevenueTrends: (period?: string) => {
    const endpoint = period ? `/analytics/revenue-trends?period=${period}` : '/analytics/revenue-trends';
    return apiRequest<{ success: boolean; data: any[] }>(endpoint);
  },

  getCustomerInsights: () => 
    apiRequest<{ success: boolean; data: any }>('/analytics/customer-insights'),

  getProductPerformance: () => 
    apiRequest<{ success: boolean; data: any }>('/analytics/product-performance'),

  getSalesPerformance: () => 
    apiRequest<{ success: boolean; data: any }>('/analytics/sales-performance'),
};

// Authentication API
export const authAPI = {
  register: (userData: {
    first_name: string;
    last_name: string;
    email: string;
    password: string;
    company?: string;
    phone?: string;
  }) => 
    apiRequest<{ success: boolean; message: string; data: { user: any; access_token: string; refresh_token: string } }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    }),

  login: (credentials: { email: string; password: string }) => 
    apiRequest<{ success: boolean; message: string; data: { user: any; access_token: string; refresh_token: string } }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    }),

  refresh: () => 
    apiRequest<{ success: boolean; data: { access_token: string } }>('/auth/refresh', {
      method: 'POST',
    }),

  logout: () => 
    apiRequest<{ success: boolean; message: string }>('/auth/logout', {
      method: 'POST',
    }),

  getProfile: () => 
    apiRequest<{ success: boolean; data: any }>('/auth/profile'),

  updateProfile: (profileData: any) => 
    apiRequest<{ success: boolean; message: string; data: any }>('/auth/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    }),

  forgotPassword: (email: string) => 
    apiRequest<{ success: boolean; message: string }>('/auth/forgot-password', {
      method: 'POST',
      body: JSON.stringify({ email }),
    }),

  resetPassword: (token: string, password: string) => 
    apiRequest<{ success: boolean; message: string }>('/auth/reset-password', {
      method: 'POST',
      body: JSON.stringify({ token, password }),
    }),
};

// Settings API
export const settingsAPI = {
  getProfile: () => 
    apiRequest<{ success: boolean; data: any }>('/settings/profile'),

  updateProfile: (profileData: any) => 
    apiRequest<{ success: boolean; message: string; data: any }>('/settings/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    }),

  getNotifications: () => 
    apiRequest<{ success: boolean; data: { notifications: any } }>('/settings/notifications'),

  updateNotifications: (notificationData: any) => 
    apiRequest<{ success: boolean; message: string; data: { notifications: any } }>('/settings/notifications', {
      method: 'PUT',
      body: JSON.stringify(notificationData),
    }),

  getSecurity: () => 
    apiRequest<{ success: boolean; data: { security: any } }>('/settings/security'),

  updateSecurity: (securityData: any) => 
    apiRequest<{ success: boolean; message: string; data: { security: any } }>('/settings/security', {
      method: 'PUT',
      body: JSON.stringify(securityData),
    }),

  getGeneral: () => 
    apiRequest<{ success: boolean; data: { general: any } }>('/settings/general'),

  updateGeneral: (generalData: any) => 
    apiRequest<{ success: boolean; message: string; data: { general: any } }>('/settings/general', {
      method: 'PUT',
      body: JSON.stringify(generalData),
    }),
};

// File Upload API
export const uploadAPI = {
  uploadAvatar: (file: File) => 
    apiFileUpload<{ success: boolean; message: string; data: { avatar_url: string; filename: string } }>('/upload/avatar', file),

  uploadProductImage: (file: File) => 
    apiFileUpload<{ success: boolean; message: string; data: { image_url: string; filename: string } }>('/upload/product-image', file),

  getFileUrl: (path: string) => `${API_BASE_URL}/files/${path}`,
};

// Export/Import API
export const exportImportAPI = {
  exportCustomers: (format: 'csv' | 'excel' = 'csv') => {
    const url = `${API_BASE_URL}/export/customers?format=${format}`;
    const token = getAuthToken();
    
    return fetch(url, {
      headers: {
        ...(token && { 'Authorization': `Bearer ${token}` }),
      },
    }).then(response => {
      if (!response.ok) {
        throw new Error('Export failed');
      }
      return response.blob();
    });
  },

  exportProducts: (format: 'csv' | 'excel' = 'csv') => {
    const url = `${API_BASE_URL}/export/products?format=${format}`;
    const token = getAuthToken();
    
    return fetch(url, {
      headers: {
        ...(token && { 'Authorization': `Bearer ${token}` }),
      },
    }).then(response => {
      if (!response.ok) {
        throw new Error('Export failed');
      }
      return response.blob();
    });
  },

  exportOrders: (format: 'csv' | 'excel' = 'csv') => {
    const url = `${API_BASE_URL}/export/orders?format=${format}`;
    const token = getAuthToken();
    
    return fetch(url, {
      headers: {
        ...(token && { 'Authorization': `Bearer ${token}` }),
      },
    }).then(response => {
      if (!response.ok) {
        throw new Error('Export failed');
      }
      return response.blob();
    });
  },

  importCustomers: (file: File) => 
    apiFileUpload<{ success: boolean; message: string; data: { imported_count: number; errors: string[] } }>('/import/customers', file),

  importProducts: (file: File) => 
    apiFileUpload<{ success: boolean; message: string; data: { imported_count: number; errors: string[] } }>('/import/products', file),
};

export default {
  products: productsAPI,
  customers: customersAPI,
  orders: ordersAPI,
  dashboard: dashboardAPI,
  analytics: analyticsAPI,
  auth: authAPI,
  settings: settingsAPI,
  upload: uploadAPI,
  exportImport: exportImportAPI,
};
