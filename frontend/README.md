# SmartBiz360 Frontend

A React-based frontend application for the SmartBiz360 business management system, now integrated with the Flask backend API.

## Features

- **Dynamic Data**: All data is now fetched from the backend API instead of static mock data
- **Real-time Updates**: Dashboard and analytics show live business metrics
- **Responsive Design**: Modern UI with Tailwind CSS
- **TypeScript**: Full type safety and better development experience
- **API Integration**: Complete CRUD operations for products, customers, and orders

## API Integration

The frontend is now fully integrated with the backend API endpoints:

### Dashboard
- Fetches real-time statistics from `/api/v1/dashboard/stats`
- Shows actual revenue, customer counts, and order data
- Displays recent orders and top products from the database

### Products
- Lists products from `/api/v1/products` with pagination
- Search and filtering handled by the backend
- Statistics from `/api/v1/products/stats`

### Customers
- Customer data from `/api/v1/customers` with pagination
- Search functionality with backend filtering
- Customer statistics from `/api/v1/customers/stats`

### Orders
- Order management via `/api/v1/orders`
- Real-time order status and customer information
- Order statistics from `/api/v1/orders/stats`

### Analytics
- Business insights from `/api/v1/analytics/overview`
- Revenue trends and customer growth data
- Performance metrics and KPIs

## Setup Instructions

### 1. Start the Backend
Make sure your Flask backend is running:

   ```bash
cd backend
python start.py
```

The API will be available at `http://localhost:5000`

### 2. Start the Frontend
In a new terminal:

   ```bash
cd frontend
   npm start
   ```

The frontend will run at `http://localhost:3000`

### 3. Database Setup
Ensure your PostgreSQL database is running and populated:

```bash
cd backend
python setup_db.py
python init_db.py
```

## Configuration

The frontend configuration is in `src/config/config.ts`:

- **API_BASE_URL**: Backend API endpoint (default: `http://localhost:5000/api/v1`)
- **BACKEND_URL**: Backend server URL (default: `http://localhost:5000`)
- **Environment variables**: Can be set via `.env` file

## API Service

The main API service is located at `src/services/api.ts` and provides:

- **Generic API requests** with error handling
- **Endpoint-specific methods** for each resource
- **Type-safe responses** with TypeScript interfaces
- **Automatic pagination** and search parameter handling

## Data Flow

1. **Component Mount**: Components fetch data from API on mount
2. **State Management**: Data is stored in React state
3. **User Interactions**: Search, pagination, and filtering trigger new API calls
4. **Real-time Updates**: Dashboard refreshes data automatically

## Error Handling

- **Loading States**: Shows loading indicators while fetching data
- **Error Boundaries**: Graceful error handling with user-friendly messages
- **Fallback Data**: Components show appropriate messages when data is unavailable
- **Network Issues**: Handles API connection problems gracefully

## Development

### Adding New API Endpoints

1. Add the endpoint method to `src/services/api.ts`
2. Create TypeScript interfaces for the data
3. Update the component to use the new API method
4. Add loading and error states

### Customizing API Calls

```typescript
// Example: Custom API call with parameters
const response = await productsAPI.getAll({
  page: 1,
  per_page: 20,
  search: 'widget',
  category: 'electronics'
});
```

### Environment Variables

Create a `.env` file in the frontend directory:

```env
REACT_APP_API_BASE_URL=http://localhost:5000/api/v1
REACT_APP_BACKEND_URL=http://localhost:5000
REACT_APP_ENVIRONMENT=development
```

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure backend CORS is configured for `http://localhost:3000`
2. **API Connection**: Verify backend is running on port 5000
3. **Database**: Check PostgreSQL connection and sample data
4. **Environment**: Verify `.env` file configuration

### Debug Mode

Enable debug mode in the config to see detailed API requests and responses.

## Performance

- **Debounced Search**: Search input has 500ms debounce to reduce API calls
- **Pagination**: Large datasets are paginated for better performance
- **Caching**: Consider implementing React Query for advanced caching
- **Lazy Loading**: Components load data only when needed

## Next Steps

- [ ] Implement real-time updates with WebSockets
- [ ] Add data caching with React Query
- [ ] Implement offline support
- [ ] Add data export functionality
- [ ] Implement user authentication
- [ ] Add role-based access control

## Support

For issues and questions:
1. Check the backend API documentation
2. Verify database connectivity
3. Check browser console for errors
4. Ensure both frontend and backend are running
