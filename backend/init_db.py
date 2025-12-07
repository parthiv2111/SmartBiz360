#!/usr/bin/env python3
"""
Database initialization script for SmartBiz360 Backend
This script creates all tables and adds sample data
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Set Flask app before importing models
os.environ['FLASK_APP'] = 'app.py'

from app import app, db
from models import (
    User, Product, Customer, Order, OrderItem, 
    DashboardStats, Analytics, PasswordResetOTP
)
from werkzeug.security import generate_password_hash

def init_database():
    """Initialize the database with tables and sample data"""
    
    print("Initializing SmartBiz360 database...")
    
    with app.app_context():
        try:
            # Create all tables
            print("Creating database tables...")
            db.create_all()
            print("✓ Database tables created successfully!")
            
            # Check if data already exists
            if User.query.first():
                print("✓ Database already contains data. Skipping sample data creation.")
                return True
            
            # Create sample users
            print("Creating sample users...")
            users_data = [
                {
                    'email': 'admin@smartbiz360.com',
                    'password': 'admin123',
                    'first_name': 'Admin',
                    'last_name': 'User',
                    'role': 'admin',
                    'is_active': True
                },
                {
                    'email': 'manager@smartbiz360.com',
                    'password': 'manager123',
                    'first_name': 'Manager',
                    'last_name': 'User',
                    'role': 'manager',
                    'is_active': True
                },
                {
                    'email': 'employee@smartbiz360.com',
                    'password': 'employee123',
                    'first_name': 'Employee',
                    'last_name': 'User',
                    'role': 'employee',
                    'is_active': True
                }
            ]
            
            for user_data in users_data:
                user = User(
                    email=user_data['email'],
                    password_hash=generate_password_hash(user_data['password']),
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    role=user_data['role'],
                    is_active=user_data['is_active']
                )
                db.session.add(user)
            
            db.session.commit()
            print("✓ Sample users created successfully!")
            
            # Create sample products
            print("Creating sample products...")
            products_data = [
                {
                    'name': 'Laptop Pro 15"',
                    'sku': 'LAPTOP-PRO-15',
                    'category': 'Electronics',
                    'price': 1299.99,
                    'stock': 50,
                    'status': 'In Stock',
                    'description': 'High-performance laptop for professionals'
                },
                {
                    'name': 'Wireless Mouse',
                    'sku': 'MOUSE-WIRELESS-001',
                    'category': 'Accessories',
                    'price': 29.99,
                    'stock': 200,
                    'status': 'In Stock',
                    'description': 'Ergonomic wireless mouse with long battery life'
                },
                {
                    'name': 'Mechanical Keyboard',
                    'sku': 'KEYBOARD-MECH-001',
                    'category': 'Accessories',
                    'price': 89.99,
                    'stock': 75,
                    'status': 'In Stock',
                    'description': 'RGB mechanical keyboard with blue switches'
                },
                {
                    'name': 'Monitor 27" 4K',
                    'sku': 'MONITOR-27-4K',
                    'category': 'Electronics',
                    'price': 399.99,
                    'stock': 30,
                    'status': 'In Stock',
                    'description': 'Ultra HD 27-inch monitor for content creators'
                },
                {
                    'name': 'USB-C Hub',
                    'sku': 'HUB-USBC-001',
                    'category': 'Accessories',
                    'price': 49.99,
                    'stock': 100,
                    'status': 'In Stock',
                    'description': 'Multi-port USB-C hub with HDMI and Ethernet'
                }
            ]
            
            for product_data in products_data:
                product = Product(**product_data)
                db.session.add(product)
            
            db.session.commit()
            print("✓ Sample products created successfully!")
            
            # Create sample customers
            print("Creating sample customers...")
            customers_data = [
                {
                    'name': 'John Smith',
                    'email': 'john.smith@email.com',
                    'company': 'Tech Solutions Inc.',
                    'phone': '+1-555-0123',
                    'address': '123 Business St, City, State 12345',
                    'status': 'Active'
                },
                {
                    'name': 'Sarah Johnson',
                    'email': 'sarah.johnson@email.com',
                    'company': 'Digital Marketing Co.',
                    'phone': '+1-555-0456',
                    'address': '456 Marketing Ave, City, State 12345',
                    'status': 'Active'
                },
                {
                    'name': 'Mike Wilson',
                    'email': 'mike.wilson@email.com',
                    'company': 'Startup Ventures',
                    'phone': '+1-555-0789',
                    'address': '789 Innovation Blvd, City, State 12345',
                    'status': 'Active'
                }
            ]
            
            for customer_data in customers_data:
                customer = Customer(**customer_data)
                db.session.add(customer)
            
            db.session.commit()
            print("✓ Sample customers created successfully!")
            
            # Create sample orders
            print("Creating sample orders...")
            customers = Customer.query.all()
            products = Product.query.all()
            
            if customers and products:
                orders_data = [
                    {
                        'customer_id': customers[0].id,
                        'total': 1329.98,
                        'status': 'Completed',
                        'order_date': datetime.utcnow() - timedelta(days=5)
                    },
                    {
                        'customer_id': customers[1].id,
                        'total': 119.98,
                        'status': 'Processing',
                        'order_date': datetime.utcnow() - timedelta(days=2)
                    },
                    {
                        'customer_id': customers[2].id,
                        'total': 489.98,
                        'status': 'Shipped',
                        'order_date': datetime.utcnow() - timedelta(days=1)
                    }
                ]
                
                for order_data in orders_data:
                    order = Order(**order_data)
                    db.session.add(order)
                
                db.session.commit()
                
                # Create order items
                orders = Order.query.all()
                if orders and products:
                    order_items_data = [
                        {
                            'order_id': orders[0].id,
                            'product_id': products[0].id,
                            'quantity': 1,
                            'price': products[0].price
                        },
                        {
                            'order_id': orders[1].id,
                            'product_id': products[1].id,
                            'quantity': 2,
                            'price': products[1].price
                        },
                        {
                            'order_id': orders[1].id,
                            'product_id': products[2].id,
                            'quantity': 1,
                            'price': products[2].price
                        },
                        {
                            'order_id': orders[2].id,
                            'product_id': products[3].id,
                            'quantity': 1,
                            'price': products[3].price
                        },
                        {
                            'order_id': orders[2].id,
                            'product_id': products[4].id,
                            'quantity': 1,
                            'price': products[4].price
                        }
                    ]
                    
                    for item_data in order_items_data:
                        order_item = OrderItem(**item_data)
                        db.session.add(order_item)
                    
                    db.session.commit()
                    print("✓ Sample orders and order items created successfully!")
            
            print("\n🎉 Database initialization completed successfully!")
            print("\nSample data created:")
            print(f"  - {User.query.count()} users")
            print(f"  - {Product.query.count()} products")
            print(f"  - {Customer.query.count()} customers")
            print(f"  - {Order.query.count()} orders")
            print(f"  - {OrderItem.query.count()} order items")
            
            print("\nDefault login credentials:")
            print("  Admin: admin@smartbiz360.com / admin123")
            print("  Manager: manager@smartbiz360.com / manager123")
            print("  Employee: employee@smartbiz360.com / employee123")
            
            return True
            
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    success = init_database()
    if success:
        print("\n✅ Database is ready to use!")
        print("You can now start the API server with: python app.py")
    else:
        print("\n❌ Database initialization failed!")
        sys.exit(1)