// Frontend Configuration
export const config = {
  // API Configuration
  API_BASE_URL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000/api/v1',
  BACKEND_URL: process.env.REACT_APP_BACKEND_URL || 'http://localhost:5000',
  
  // Environment
  ENVIRONMENT: process.env.REACT_APP_ENVIRONMENT || 'development',
  DEBUG: process.env.REACT_APP_DEBUG === 'true' || false,
  
  // Pagination
  DEFAULT_PAGE_SIZE: 10,
  MAX_PAGE_SIZE: 100,
  
  // Search debounce delay (ms)
  SEARCH_DEBOUNCE_DELAY: 500,
  
  // Date formats
  DATE_FORMAT: 'YYYY-MM-DD',
  DATETIME_FORMAT: 'YYYY-MM-DD HH:mm:ss',
  
  // Currency
  CURRENCY: 'USD',
  CURRENCY_SYMBOL: '$',
  
  // Status colors
  STATUS_COLORS: {
    'Active': 'bg-success-100 text-success-800',
    'Inactive': 'bg-gray-100 text-gray-800',
    'In Stock': 'bg-success-100 text-success-800',
    'Low Stock': 'bg-warning-100 text-warning-800',
    'Out of Stock': 'bg-error-100 text-error-800',
    'Completed': 'bg-success-100 text-success-800',
    'Processing': 'bg-warning-100 text-warning-800',
    'Shipped': 'bg-primary-100 text-primary-800',
    'Pending': 'bg-gray-100 text-gray-800',
    'Cancelled': 'bg-error-100 text-error-800',
  }
};

export default config;
