# SmartBiz360 API Documentation

## Overview
This document describes the newly implemented APIs for authentication, settings, file uploads, and export/import functionality.

## Authentication APIs

### Register User
- **POST** `/api/v1/auth/register`
- **Body**: `{ "first_name": "John", "last_name": "Doe", "email": "john@example.com", "password": "password123", "company": "Company Name" }`
- **Response**: User data with access and refresh tokens

### Login User
- **POST** `/api/v1/auth/login`
- **Body**: `{ "email": "john@example.com", "password": "password123" }`
- **Response**: User data with access and refresh tokens

### Refresh Token
- **POST** `/api/v1/auth/refresh`
- **Headers**: `Authorization: Bearer <refresh_token>`
- **Response**: New access token

### Logout
- **POST** `/api/v1/auth/logout`
- **Headers**: `Authorization: Bearer <access_token>`

### Get Profile
- **GET** `/api/v1/auth/profile`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response**: Current user profile

### Update Profile
- **PUT** `/api/v1/auth/profile`
- **Headers**: `Authorization: Bearer <access_token>`
- **Body**: `{ "first_name": "John", "last_name": "Smith", "email": "john@example.com" }`

### Forgot Password
- **POST** `/api/v1/auth/forgot-password`
- **Body**: `{ "email": "john@example.com" }`

### Reset Password
- **POST** `/api/v1/auth/reset-password`
- **Body**: `{ "token": "reset_token", "password": "new_password" }`

## Settings APIs

### Get Profile Settings
- **GET** `/api/v1/settings/profile`
- **Headers**: `Authorization: Bearer <access_token>`

### Update Profile Settings
- **PUT** `/api/v1/settings/profile`
- **Headers**: `Authorization: Bearer <access_token>`
- **Body**: `{ "first_name": "John", "last_name": "Doe", "email": "john@example.com", "company": "Company", "phone": "+1234567890" }`

### Get Notification Settings
- **GET** `/api/v1/settings/notifications`
- **Headers**: `Authorization: Bearer <access_token>`

### Update Notification Settings
- **PUT** `/api/v1/settings/notifications`
- **Headers**: `Authorization: Bearer <access_token>`
- **Body**: `{ "email_notifications": true, "push_notifications": false, "order_updates": true, "marketing_emails": false, "weekly_reports": true }`

### Get Security Settings
- **GET** `/api/v1/settings/security`
- **Headers**: `Authorization: Bearer <access_token>`

### Update Security Settings
- **PUT** `/api/v1/settings/security`
- **Headers**: `Authorization: Bearer <access_token>`
- **Body**: `{ "two_factor_auth": false, "session_timeout": "24h", "password_expiry": "90d" }`

### Get General Settings
- **GET** `/api/v1/settings/general`
- **Headers**: `Authorization: Bearer <access_token>`

### Update General Settings
- **PUT** `/api/v1/settings/general`
- **Headers**: `Authorization: Bearer <access_token>`
- **Body**: `{ "language": "en", "timezone": "UTC", "theme": "light" }`

## File Upload APIs

### Upload Avatar
- **POST** `/api/v1/upload/avatar`
- **Headers**: `Authorization: Bearer <access_token>`
- **Body**: Form data with `file` field
- **Response**: `{ "avatar_url": "/api/v1/files/avatars/filename.jpg" }`

### Upload Product Image
- **POST** `/api/v1/upload/product-image`
- **Headers**: `Authorization: Bearer <access_token>`
- **Body**: Form data with `file` field
- **Response**: `{ "image_url": "/api/v1/files/products/filename.jpg" }`

### Serve Files
- **GET** `/api/v1/files/avatars/{filename}`
- **GET** `/api/v1/files/products/{filename}`

## Export/Import APIs

### Export Customers
- **GET** `/api/v1/export/customers?format=csv`
- **GET** `/api/v1/export/customers?format=excel`
- **Headers**: `Authorization: Bearer <access_token>`
- **Permissions**: Admin or Manager only

### Export Products
- **GET** `/api/v1/export/products?format=csv`
- **GET** `/api/v1/export/products?format=excel`
- **Headers**: `Authorization: Bearer <access_token>`
- **Permissions**: Admin or Manager only

### Export Orders
- **GET** `/api/v1/export/orders?format=csv`
- **GET** `/api/v1/export/orders?format=excel`
- **Headers**: `Authorization: Bearer <access_token>`
- **Permissions**: Admin or Manager only

### Import Customers
- **POST** `/api/v1/import/customers`
- **Headers**: `Authorization: Bearer <access_token>`
- **Body**: Form data with CSV/Excel file
- **Permissions**: Admin or Manager only

### Import Products
- **POST** `/api/v1/import/products`
- **Headers**: `Authorization: Bearer <access_token>`
- **Body**: Form data with CSV/Excel file
- **Permissions**: Admin or Manager only

## Sample Login Credentials

After running the database initialization, you can use these credentials:

- **Admin**: `admin@smartbiz360.com` / `admin123`
- **Manager**: `manager@smartbiz360.com` / `manager123`
- **User**: `user@smartbiz360.com` / `user123`

## Installation and Setup

1. Install new dependencies:
```bash
pip install -r requirements.txt
```

2. Run database migrations:
```bash
flask db upgrade
```

3. Initialize database with sample data:
```bash
python init_db.py
```

4. Start the server:
```bash
python app.py
```

## File Upload Configuration

- Upload directory: `uploads/` (created automatically)
- Avatar directory: `uploads/avatars/`
- Product images directory: `uploads/products/`
- Maximum file size: 16MB
- Allowed formats: PNG, JPG, JPEG, GIF, WEBP
- Images are automatically resized to 800x800px maximum

## Security Notes

- All authentication endpoints use JWT tokens
- Passwords are hashed using Werkzeug's security functions
- File uploads are validated for type and size
- Export/Import operations require admin or manager permissions
- CORS is configured for frontend integration
