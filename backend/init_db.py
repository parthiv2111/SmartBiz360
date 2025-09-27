from app import create_app
from models import db, Product, Customer, Order, OrderItem, User, UserSettings
from datetime import datetime, date
from decimal import Decimal
import uuid

def init_database():
    """Initialize database with sample data"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if data already exists
        if Product.query.first() is not None:
            print("Database already contains data. Skipping initialization.")
            return
        
        print("Initializing database with sample data...")
        
        # Create sample products
        products = [
            {
                'name': 'Premium Widget',
                'sku': 'PW-001',
                'category': 'Widgets',
                'price': Decimal('299.99'),
                'stock': 45,
                'status': 'In Stock',
                'image': 'https://via.placeholder.com/40x40',
                'description': 'High-quality premium widget with advanced features'
            },
            {
                'name': 'Basic Widget',
                'sku': 'BW-001',
                'category': 'Widgets',
                'price': Decimal('99.99'),
                'stock': 120,
                'status': 'In Stock',
                'image': 'https://via.placeholder.com/40x40',
                'description': 'Standard widget for basic needs'
            },
            {
                'name': 'Deluxe Widget',
                'sku': 'DW-001',
                'category': 'Widgets',
                'price': Decimal('199.99'),
                'stock': 23,
                'status': 'Low Stock',
                'image': 'https://via.placeholder.com/40x40',
                'description': 'Deluxe widget with premium features'
            },
            {
                'name': 'Standard Widget',
                'sku': 'SW-001',
                'category': 'Widgets',
                'price': Decimal('149.99'),
                'stock': 0,
                'status': 'Out of Stock',
                'image': 'https://via.placeholder.com/40x40',
                'description': 'Standard widget for everyday use'
            },
            {
                'name': 'Pro Widget',
                'sku': 'PROW-001',
                'category': 'Premium',
                'price': Decimal('499.99'),
                'stock': 12,
                'status': 'In Stock',
                'image': 'https://via.placeholder.com/40x40',
                'description': 'Professional-grade widget for experts'
            }
        ]
        
        created_products = []
        for product_data in products:
            product = Product(**product_data)
            db.session.add(product)
            created_products.append(product)
        
        # Create sample customers
        customers = [
            {
                'name': 'John Doe',
                'email': 'john.doe@example.com',
                'company': 'Acme Corp',
                'phone': '+1 (555) 123-4567',
                'status': 'Active',
                'join_date': date(2024, 1, 15),
                'address': '123 Main St, Anytown, USA'
            },
            {
                'name': 'Jane Smith',
                'email': 'jane.smith@example.com',
                'company': 'Tech Solutions',
                'phone': '+1 (555) 987-6543',
                'status': 'Active',
                'join_date': date(2024, 2, 20),
                'address': '456 Oak Ave, Somewhere, USA'
            },
            {
                'name': 'Bob Johnson',
                'email': 'bob.johnson@example.com',
                'company': 'Global Industries',
                'phone': '+1 (555) 456-7890',
                'status': 'Inactive',
                'join_date': date(2023, 11, 10),
                'address': '789 Pine Rd, Elsewhere, USA'
            },
            {
                'name': 'Alice Brown',
                'email': 'alice.brown@example.com',
                'company': 'Innovation Labs',
                'phone': '+1 (555) 789-0123',
                'status': 'Active',
                'join_date': date(2024, 3, 5),
                'address': '321 Elm St, Nowhere, USA'
            },
            {
                'name': 'Charlie Wilson',
                'email': 'charlie.wilson@example.com',
                'company': 'Startup Inc',
                'phone': '+1 (555) 321-6540',
                'status': 'Active',
                'join_date': date(2024, 1, 28),
                'address': '654 Maple Dr, Anywhere, USA'
            }
        ]
        
        created_customers = []
        for customer_data in customers:
            customer = Customer(**customer_data)
            db.session.add(customer)
            created_customers.append(customer)
        
        # Commit to get IDs
        db.session.commit()
        
        # Create sample orders
        orders = [
            {
                'order_number': '#1234',
                'customer_id': created_customers[0].id,  # John Doe
                'total': Decimal('399.98'),
                'status': 'Completed',
                'order_date': date(2024, 3, 15),
                'payment_method': 'Credit Card',
                'shipping_address': '123 Main St, Anytown, USA',
                'notes': 'Priority shipping requested'
            },
            {
                'order_number': '#1235',
                'customer_id': created_customers[1].id,  # Jane Smith
                'total': Decimal('199.99'),
                'status': 'Processing',
                'order_date': date(2024, 3, 14),
                'payment_method': 'PayPal',
                'shipping_address': '456 Oak Ave, Somewhere, USA',
                'notes': None
            },
            {
                'order_number': '#1236',
                'customer_id': created_customers[2].id,  # Bob Johnson
                'total': Decimal('649.98'),
                'status': 'Shipped',
                'order_date': date(2024, 3, 13),
                'payment_method': 'Credit Card',
                'shipping_address': '789 Pine Rd, Elsewhere, USA',
                'notes': 'Gift wrapping requested'
            },
            {
                'order_number': '#1237',
                'customer_id': created_customers[3].id,  # Alice Brown
                'total': Decimal('299.99'),
                'status': 'Pending',
                'order_date': date(2024, 3, 12),
                'payment_method': 'Bank Transfer',
                'shipping_address': '321 Elm St, Nowhere, USA',
                'notes': None
            },
            {
                'order_number': '#1238',
                'customer_id': created_customers[4].id,  # Charlie Wilson
                'total': Decimal('99.99'),
                'status': 'Cancelled',
                'order_date': date(2024, 3, 11),
                'payment_method': 'Credit Card',
                'shipping_address': '654 Maple Dr, Anywhere, USA',
                'notes': 'Customer requested cancellation'
            }
        ]
        
        created_orders = []
        for order_data in orders:
            order = Order(**order_data)
            db.session.add(order)
            created_orders.append(order)
        
        # Commit to get order IDs
        db.session.commit()
        
        # Create sample order items
        order_items = [
            # Order #1234 - John Doe (Premium Widget + Basic Widget)
            {
                'order_id': created_orders[0].id,
                'product_id': created_products[0].id,  # Premium Widget
                'quantity': 1,
                'unit_price': Decimal('299.99'),
                'subtotal': Decimal('299.99')
            },
            {
                'order_id': created_orders[0].id,
                'product_id': created_products[1].id,  # Basic Widget
                'quantity': 1,
                'unit_price': Decimal('99.99'),
                'subtotal': Decimal('99.99')
            },
            # Order #1235 - Jane Smith (Deluxe Widget)
            {
                'order_id': created_orders[1].id,
                'product_id': created_products[2].id,  # Deluxe Widget
                'quantity': 1,
                'unit_price': Decimal('199.99'),
                'subtotal': Decimal('199.99')
            },
            # Order #1236 - Bob Johnson (Standard Widget + Pro Widget)
            {
                'order_id': created_orders[2].id,
                'product_id': created_products[3].id,  # Standard Widget
                'quantity': 1,
                'unit_price': Decimal('149.99'),
                'subtotal': Decimal('149.99')
            },
            {
                'order_id': created_orders[2].id,
                'product_id': created_products[4].id,  # Pro Widget
                'quantity': 1,
                'unit_price': Decimal('499.99'),
                'subtotal': Decimal('499.99')
            },
            # Order #1237 - Alice Brown (Premium Widget)
            {
                'order_id': created_orders[3].id,
                'product_id': created_products[0].id,  # Premium Widget
                'quantity': 1,
                'unit_price': Decimal('299.99'),
                'subtotal': Decimal('299.99')
            },
            # Order #1238 - Charlie Wilson (Basic Widget) - Cancelled
            {
                'order_id': created_orders[4].id,
                'product_id': created_products[1].id,  # Basic Widget
                'quantity': 1,
                'unit_price': Decimal('99.99'),
                'subtotal': Decimal('99.99')
            }
        ]
        
        for item_data in order_items:
            order_item = OrderItem(**item_data)
            db.session.add(order_item)
        
        # Create sample users
        users_data = [
            {
                'first_name': 'Admin',
                'last_name': 'User',
                'email': 'admin@smartbiz360.com',
                'password': 'admin123',
                'company': 'SmartBiz360',
                'phone': '+1 (555) 123-4567',
                'role': 'admin'
            },
            {
                'first_name': 'John',
                'last_name': 'Manager',
                'email': 'manager@smartbiz360.com',
                'password': 'manager123',
                'company': 'SmartBiz360',
                'phone': '+1 (555) 123-4568',
                'role': 'manager'
            },
            {
                'first_name': 'Jane',
                'last_name': 'User',
                'email': 'user@smartbiz360.com',
                'password': 'user123',
                'company': 'SmartBiz360',
                'phone': '+1 (555) 123-4569',
                'role': 'user'
            }
        ]
        
        created_users = []
        for user_data in users_data:
            user = User(
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                email=user_data['email'],
                company=user_data['company'],
                phone=user_data['phone'],
                role=user_data['role']
            )
            user.set_password(user_data['password'])
            db.session.add(user)
            created_users.append(user)
        
        db.session.flush()  # Get user IDs
        
        # Create default settings for each user
        for user in created_users:
            settings = UserSettings(
                user_id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                company=user.company,
                phone=user.phone
            )
            db.session.add(settings)
        
        # Final commit
        db.session.commit()
        
        print("Database initialization completed successfully!")
        print(f"Created {len(created_products)} products")
        print(f"Created {len(created_customers)} customers")
        print(f"Created {len(created_orders)} orders")
        print(f"Created {len(order_items)} order items")
        print(f"Created {len(created_users)} users")
        print("\nSample login credentials:")
        print("Admin: admin@smartbiz360.com / admin123")
        print("Manager: manager@smartbiz360.com / manager123")
        print("User: user@smartbiz360.com / user123")

if __name__ == '__main__':
    init_database()
