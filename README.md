# SmartBiz360 - Complete Business Management System

A modern, full-stack business management application built with React, Flask, and PostgreSQL. SmartBiz360 provides comprehensive tools for managing products, customers, orders, analytics, and more.

## 🌟 Features

### 🔐 Authentication & User Management
- **JWT-based Authentication**: Secure token-based authentication system
- **Role-based Access Control**: Admin, Manager, and User roles with different permissions
- **User Registration & Login**: Complete user onboarding flow
- **Profile Management**: User profile with avatar upload
- **Password Reset**: Secure password recovery system

### 📊 Dashboard & Analytics
- **Real-time Dashboard**: Key metrics and KPIs at a glance
- **Advanced Analytics**: Revenue trends, customer insights, product performance
- **Interactive Charts**: Visual data representation with charts and graphs
- **Performance Metrics**: Business performance tracking

### 🛍️ Product Management
- **Product Catalog**: Complete product management with CRUD operations
- **Inventory Tracking**: Stock management with low stock alerts
- **Product Images**: Image upload and management
- **Categories & SKUs**: Organized product categorization
- **Import/Export**: Bulk product import/export (CSV/Excel)

### 👥 Customer Management
- **Customer Database**: Comprehensive customer information management
- **Customer Analytics**: Customer insights and behavior tracking
- **Order History**: Complete customer order tracking
- **Communication**: Customer communication tools

### 📦 Order Management
- **Order Processing**: Complete order lifecycle management
- **Order Tracking**: Real-time order status updates
- **Payment Integration**: Multiple payment method support
- **Shipping Management**: Order fulfillment and tracking

### ⚙️ Settings & Configuration
- **User Preferences**: Personalized settings for each user
- **Notification Settings**: Customizable notification preferences
- **Security Settings**: Two-factor authentication, session management
- **Theme Support**: Light/dark theme switching
- **Multi-language**: Support for multiple languages

### 📁 File Management
- **Image Upload**: Secure image upload with automatic resizing
- **File Validation**: File type and size validation
- **Organized Storage**: Structured file organization

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL 12+
- Docker (optional)

### Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Setup environment variables:**
```bash
cp env.example .env
# Edit .env with your database credentials
```

5. **Initialize database:**
```bash
flask db upgrade
python init_db.py
```

6. **Start the server:**
```bash
python app.py
```

Backend will be available at `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Setup environment variables:**
```bash
cp env.example .env
# Edit .env with your API URL
```

4. **Start the development server:**
```bash
npm start
```

Frontend will be available at `http://localhost:3000`

## 🐳 Docker Deployment

### Quick Start with Docker Compose

```bash
# From the root directory
docker-compose up -d
```

This will start:
- PostgreSQL database
- Backend API server
- Frontend web application

### Individual Services

**Backend:**
```bash
cd backend
docker build -t smartbiz360-backend .
docker run -p 5000:5000 smartbiz360-backend
```

**Frontend:**
```bash
cd frontend
docker build -t smartbiz360-frontend .
docker run -p 80:80 smartbiz360-frontend
```

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/auth/profile` - Get user profile
- `PUT /api/v1/auth/profile` - Update user profile

### Product Endpoints
- `GET /api/v1/products` - List products (with pagination, search, filters)
- `POST /api/v1/products` - Create product
- `GET /api/v1/products/{id}` - Get product details
- `PUT /api/v1/products/{id}` - Update product
- `DELETE /api/v1/products/{id}` - Delete product
- `GET /api/v1/products/stats` - Get product statistics

### Customer Endpoints
- `GET /api/v1/customers` - List customers
- `POST /api/v1/customers` - Create customer
- `GET /api/v1/customers/{id}` - Get customer details
- `PUT /api/v1/customers/{id}` - Update customer
- `DELETE /api/v1/customers/{id}` - Delete customer
- `GET /api/v1/customers/stats` - Get customer statistics

### Order Endpoints
- `GET /api/v1/orders` - List orders
- `POST /api/v1/orders` - Create order
- `GET /api/v1/orders/{id}` - Get order details
- `PUT /api/v1/orders/{id}` - Update order
- `DELETE /api/v1/orders/{id}` - Delete order
- `GET /api/v1/orders/stats` - Get order statistics

### Settings Endpoints
- `GET /api/v1/settings/profile` - Get profile settings
- `PUT /api/v1/settings/profile` - Update profile settings
- `GET /api/v1/settings/notifications` - Get notification settings
- `PUT /api/v1/settings/notifications` - Update notification settings
- `GET /api/v1/settings/security` - Get security settings
- `PUT /api/v1/settings/security` - Update security settings
- `GET /api/v1/settings/general` - Get general settings
- `PUT /api/v1/settings/general` - Update general settings

### File Upload Endpoints
- `POST /api/v1/upload/avatar` - Upload user avatar
- `POST /api/v1/upload/product-image` - Upload product image
- `GET /api/v1/files/{path}` - Serve uploaded files

### Export/Import Endpoints
- `GET /api/v1/export/customers` - Export customers (CSV/Excel)
- `GET /api/v1/export/products` - Export products (CSV/Excel)
- `GET /api/v1/export/orders` - Export orders (CSV/Excel)
- `POST /api/v1/import/customers` - Import customers
- `POST /api/v1/import/products` - Import products

## 🔑 Sample Login Credentials

After running the database initialization, you can use these credentials:

- **Admin**: `admin@smartbiz360.com` / `admin123`
- **Manager**: `manager@smartbiz360.com` / `manager123`
- **User**: `user@smartbiz360.com` / `user123`

## 🛠️ Technology Stack

### Frontend
- **React 18** - Modern React with hooks
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **React Router DOM** - Client-side routing
- **Lucide React** - Beautiful icons
- **Context API** - State management

### Backend
- **Flask** - Lightweight Python web framework
- **SQLAlchemy** - Python SQL toolkit and ORM
- **PostgreSQL** - Robust relational database
- **Flask-JWT-Extended** - JWT authentication
- **Marshmallow** - Object serialization/deserialization
- **Flask-CORS** - Cross-origin resource sharing
- **Pillow** - Image processing
- **Pandas** - Data manipulation and analysis

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Web server and reverse proxy
- **Gunicorn** - Python WSGI HTTP server

## 📁 Project Structure

```
SmartBiz360/
├── backend/
│   ├── app.py                 # Flask application
│   ├── models.py             # Database models
│   ├── schemas.py            # Data validation schemas
│   ├── config.py             # Configuration
│   ├── requirements.txt      # Python dependencies
│   ├── routes/               # API routes
│   │   ├── auth.py          # Authentication routes
│   │   ├── products.py      # Product routes
│   │   ├── customers.py     # Customer routes
│   │   ├── orders.py        # Order routes
│   │   ├── dashboard.py     # Dashboard routes
│   │   ├── analytics.py     # Analytics routes
│   │   ├── settings.py      # Settings routes
│   │   ├── uploads.py       # File upload routes
│   │   └── export_import.py # Export/import routes
│   ├── Dockerfile           # Backend Docker configuration
│   └── docker-compose.yml   # Docker Compose configuration
├── frontend/
│   ├── src/
│   │   ├── components/      # Reusable components
│   │   ├── pages/          # Page components
│   │   ├── contexts/       # React contexts
│   │   ├── services/       # API services
│   │   └── config/         # Configuration
│   ├── public/             # Static files
│   ├── package.json        # Node.js dependencies
│   ├── Dockerfile          # Frontend Docker configuration
│   └── nginx.conf          # Nginx configuration
├── DEPLOYMENT_GUIDE.md     # Deployment instructions
└── README.md              # This file
```

## 🔧 Configuration

### Backend Configuration

Key environment variables in `backend/.env`:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/smartbiz360
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
CORS_ORIGINS=http://localhost:3000
UPLOAD_FOLDER=uploads
FLASK_ENV=development
```

### Frontend Configuration

Key environment variables in `frontend/.env`:

```env
REACT_APP_API_BASE_URL=http://localhost:5000/api/v1
NODE_ENV=development
```

## 🚀 Production Deployment

For production deployment, see the [Deployment Guide](DEPLOYMENT_GUIDE.md) for detailed instructions including:

- Docker deployment
- Environment configuration
- Security considerations
- Performance optimization
- Monitoring and logging
- Backup strategies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the [Deployment Guide](DEPLOYMENT_GUIDE.md)
- Review the API documentation
- Check the troubleshooting section
- Open an issue on GitHub

## 🎯 Roadmap

- [ ] Real-time notifications
- [ ] Advanced reporting
- [ ] Mobile app
- [ ] Third-party integrations
- [ ] Advanced analytics
- [ ] Multi-tenant support
- [ ] API rate limiting
- [ ] Advanced security features

---

**SmartBiz360** - Your complete business management solution! 🚀
