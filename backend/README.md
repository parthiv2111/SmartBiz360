# SmartBiz360 Backend API

A comprehensive Flask-based backend API for the SmartBiz360 business management system with PostgreSQL database.

## Features

- **Products Management**: Full CRUD operations for product catalog
- **Customer Management**: Customer relationship management with order history
- **Order Management**: Order processing with inventory tracking
- **Dashboard Analytics**: Real-time business metrics and insights
- **Advanced Analytics**: Business intelligence and reporting
- **RESTful API**: Clean, consistent API design
- **Data Validation**: Comprehensive input validation using Marshmallow
- **Database Migrations**: Easy database schema management

## Tech Stack

- **Backend**: Flask 2.3.3
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migrations**: Flask-Migrate
- **Validation**: Marshmallow schemas
- **CORS**: Flask-CORS for frontend integration

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip (Python package manager)

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd SmartBiz360/backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

#### Create PostgreSQL Database

```sql
CREATE DATABASE smartbiz360;
CREATE USER smartbiz360_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE smartbiz360 TO smartbiz360_user;
```

#### Configure Environment Variables

Create a `.env` file in the backend directory:

```env
DATABASE_URL=postgresql://smartbiz360_user:your_password@localhost:5432/smartbiz360
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### 5. Initialize Database

```bash
python init_db.py
```

This will create all tables and populate them with sample data.

### 6. Run the Application

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Base URL
```
http://localhost:5000/api/v1
```

### Products API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/products` | Get all products with pagination |
| GET | `/products/<id>` | Get specific product |
| POST | `/products` | Create new product |
| PUT | `/products/<id>` | Update product |
| DELETE | `/products/<id>` | Delete product |
| GET | `/products/stats` | Get product statistics |

### Customers API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/customers` | Get all customers with pagination |
| GET | `/customers/<id>` | Get specific customer |
| POST | `/customers` | Create new customer |
| PUT | `/customers/<id>` | Update customer |
| DELETE | `/customers/<id>` | Delete customer |
| GET | `/customers/stats` | Get customer statistics |

### Orders API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/orders` | Get all orders with pagination |
| GET | `/orders/<id>` | Get specific order |
| POST | `/orders` | Create new order |
| PUT | `/orders/<id>` | Update order |
| DELETE | `/orders/<id>` | Delete order |
| GET | `/orders/stats` | Get order statistics |

### Dashboard API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard/stats` | Get dashboard statistics |
| GET | `/dashboard/revenue-trends` | Get revenue trends |
| GET | `/dashboard/customer-growth` | Get customer growth data |
| GET | `/dashboard/performance-metrics` | Get performance metrics |

### Analytics API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/analytics/overview` | Get analytics overview |
| GET | `/analytics/revenue-trends` | Get detailed revenue trends |
| GET | `/analytics/customer-insights` | Get customer insights |
| GET | `/analytics/product-performance` | Get product performance |
| GET | `/analytics/sales-performance` | Get sales performance |

## Data Models

### Product
- `id`: UUID (Primary Key)
- `name`: String (Required)
- `sku`: String (Required, Unique)
- `category`: String (Required)
- `price`: Decimal (Required)
- `stock`: Integer
- `status`: String (In Stock, Low Stock, Out of Stock)
- `image`: String (URL)
- `description`: Text
- `created_at`: DateTime
- `updated_at`: DateTime

### Customer
- `id`: UUID (Primary Key)
- `name`: String (Required)
- `email`: String (Required, Unique)
- `company`: String
- `phone`: String
- `status`: String (Active, Inactive)
- `join_date`: Date
- `address`: Text
- `created_at`: DateTime
- `updated_at`: DateTime

### Order
- `id`: UUID (Primary Key)
- `order_number`: String (Required, Unique)
- `customer_id`: UUID (Foreign Key)
- `total`: Decimal (Required)
- `status`: String (Pending, Processing, Shipped, Completed, Cancelled)
- `order_date`: Date
- `payment_method`: String
- `shipping_address`: Text
- `notes`: Text
- `created_at`: DateTime
- `updated_at`: DateTime

### OrderItem
- `id`: UUID (Primary Key)
- `order_id`: UUID (Foreign Key)
- `product_id`: UUID (Foreign Key)
- `quantity`: Integer (Required)
- `unit_price`: Decimal (Required)
- `subtotal`: Decimal (Required)

## Sample API Requests

### Create a Product

```bash
curl -X POST http://localhost:5000/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Widget",
    "sku": "NW-001",
    "category": "Widgets",
    "price": 199.99,
    "stock": 50,
    "description": "A brand new widget"
  }'
```

### Create a Customer

```bash
curl -X POST http://localhost:5000/api/v1/customers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Smith",
    "email": "john.smith@example.com",
    "company": "Tech Corp",
    "phone": "+1 (555) 123-4567",
    "status": "Active"
  }'
```

### Create an Order

```bash
curl -X POST http://localhost:5000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{
    "order_number": "#1239",
    "customer_id": "customer-uuid-here",
    "order_items": [
      {
        "product_id": "product-uuid-here",
        "quantity": 2,
        "unit_price": 99.99
      }
    ],
    "payment_method": "Credit Card",
    "shipping_address": "123 Main St, Anytown, USA"
  }'
```

## Query Parameters

### Pagination
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 10, max: 100)

### Search & Filtering
- `search`: Search term for text fields
- `category`: Filter by product category
- `status`: Filter by status
- `company`: Filter by customer company

### Analytics
- `period`: Time period for trends (daily, weekly, monthly, yearly)

## Error Handling

All API endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "Error message description"
}
```

Common HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request (Validation Error)
- `404`: Not Found
- `500`: Internal Server Error

## Development

### Running Tests

```bash
# Set testing environment
export FLASK_ENV=testing

# Run tests (when implemented)
python -m pytest
```

### Database Migrations

```bash
# Initialize migrations (first time)
flask db init

# Create migration
flask db migrate -m "Description of changes"

# Apply migration
flask db upgrade
```

### Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to all functions
- Handle exceptions gracefully

## Deployment

### Production Considerations

1. **Environment Variables**: Set proper production values
2. **Database**: Use production PostgreSQL instance
3. **Security**: Change default secret keys
4. **CORS**: Restrict origins to production domains
5. **Logging**: Implement proper logging
6. **Monitoring**: Add health checks and monitoring

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app.py"]
```

## Support

For issues and questions:
1. Check the API documentation
2. Review error logs
3. Verify database connectivity
4. Check environment variables

## License

This project is licensed under the MIT License.
