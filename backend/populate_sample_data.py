#!/usr/bin/env python3
"""
Populate database with comprehensive sample data
Adds approximately 30 items to each table
"""

import os
import sys
from datetime import datetime, timedelta
from random import choice, randint, uniform
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Set Flask app before importing models
os.environ['FLASK_APP'] = 'app.py'

from app import app, db
from models import (
    User, UserSettings, Product, Customer, Order, OrderItem,
    Attendance, Project, Task, Lead, Deal, Expense, Supplier,
    PurchaseOrder, PasswordResetOTP
)
from werkzeug.security import generate_password_hash

# Sample data generators
FIRST_NAMES = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Jessica', 
               'William', 'Ashley', 'James', 'Amanda', 'Christopher', 'Melissa', 'Daniel',
               'Michelle', 'Matthew', 'Kimberly', 'Anthony', 'Amy', 'Mark', 'Angela',
               'Donald', 'Stephanie', 'Steven', 'Nicole', 'Paul', 'Elizabeth', 'Andrew', 'Helen']

LAST_NAMES = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
              'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Wilson', 'Anderson', 'Thomas',
              'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Thompson', 'White', 'Harris',
              'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker', 'Young']

COMPANIES = ['Tech Solutions Inc.', 'Digital Marketing Co.', 'Startup Ventures', 'Global Industries',
             'Innovation Labs', 'Business Partners', 'Enterprise Systems', 'Creative Agency',
             'Smart Solutions', 'Future Tech', 'Data Analytics Corp', 'Cloud Services Ltd',
             'Software Innovations', 'Network Solutions', 'Cyber Security Pro', 'AI Technologies',
             'Mobile Apps Co.', 'Web Development Inc.', 'E-commerce Solutions', 'IT Consulting Group']

PRODUCT_CATEGORIES = ['Electronics', 'Accessories', 'Software', 'Hardware', 'Office Supplies',
                      'Networking', 'Security', 'Storage', 'Peripherals', 'Components']

PRODUCT_NAMES = ['Laptop', 'Desktop', 'Monitor', 'Keyboard', 'Mouse', 'Headphones', 'Webcam',
                 'Printer', 'Scanner', 'Tablet', 'Smartphone', 'Router', 'Switch', 'Server',
                 'Hard Drive', 'SSD', 'Memory', 'Processor', 'Graphics Card', 'Motherboard']

def generate_email(first_name, last_name, company=None):
    """Generate a unique email"""
    base = f"{first_name.lower()}.{last_name.lower()}"
    if company:
        domain = company.lower().replace(' ', '').replace('.', '').replace(',', '')[:15]
    else:
        domain = 'example'
    return f"{base}@{domain}.com"

def populate_users():
    """Create 30 users"""
    print("Creating 30 users...")
    users = []
    roles = ['admin', 'manager', 'user', 'employee']
    departments = ['Sales', 'Marketing', 'IT', 'HR', 'Finance', 'Operations', 'Support']
    positions = ['Manager', 'Developer', 'Analyst', 'Specialist', 'Coordinator', 'Director', 'Executive']
    
    for i in range(30):
        first_name = choice(FIRST_NAMES)
        last_name = choice(LAST_NAMES)
        email = generate_email(first_name, last_name)
        
        # Ensure unique email
        while User.query.filter_by(email=email).first():
            email = f"{first_name.lower()}.{last_name.lower()}{i}@example.com"
        
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=generate_password_hash('password123'),
            company=choice(COMPANIES) if i % 3 == 0 else None,
            phone=f"+1-555-{randint(1000, 9999)}",
            role=choice(roles),
            is_active=True,
            email_verified=i % 2 == 0,
            department=choice(departments) if i % 2 == 0 else None,
            position=choice(positions) if i % 2 == 0 else None,
            join_date=(datetime.utcnow() - timedelta(days=randint(0, 365))).date()
        )
        db.session.add(user)
        users.append(user)
    
    db.session.commit()
    print(f"✓ Created {len(users)} users")
    return users

def populate_products():
    """Create 30 products"""
    print("Creating 30 products...")
    products = []
    statuses = ['In Stock', 'Low Stock', 'Out of Stock']
    
    for i in range(30):
        category = choice(PRODUCT_CATEGORIES)
        product_name = choice(PRODUCT_NAMES)
        name = f"{product_name} {randint(1, 9)}.{randint(0, 9)}"
        sku = f"{category[:3].upper()}-{product_name[:3].upper()}-{str(i+1).zfill(3)}"
        
        # Ensure unique SKU
        while Product.query.filter_by(sku=sku).first():
            sku = f"{category[:3].upper()}-{product_name[:3].upper()}-{str(i+100).zfill(3)}"
        
        stock = randint(0, 200)
        if stock > 50:
            status = 'In Stock'
        elif stock > 10:
            status = 'Low Stock'
        else:
            status = 'Out of Stock'
        
        product = Product(
            name=name,
            sku=sku,
            category=category,
            price=round(uniform(10.00, 2000.00), 2),
            stock=stock,
            status=status,
            description=f"High-quality {name.lower()} for professional use"
        )
        db.session.add(product)
        products.append(product)
    
    db.session.commit()
    print(f"✓ Created {len(products)} products")
    return products

def populate_customers():
    """Create 30 customers"""
    print("Creating 30 customers...")
    customers = []
    statuses = ['Active', 'Inactive']
    
    for i in range(30):
        first_name = choice(FIRST_NAMES)
        last_name = choice(LAST_NAMES)
        name = f"{first_name} {last_name}"
        company = choice(COMPANIES) if i % 2 == 0 else None
        email = generate_email(first_name, last_name, company)
        
        # Ensure unique email
        while Customer.query.filter_by(email=email).first():
            email = f"{first_name.lower()}.{last_name.lower()}{i}@customer.com"
        
        customer = Customer(
            name=name,
            email=email,
            company=company,
            phone=f"+1-555-{randint(1000, 9999)}",
            status=choice(statuses),
            address=f"{randint(100, 9999)} {choice(['Main', 'Oak', 'Park', 'Elm', 'Maple'])} St, City, State {randint(10000, 99999)}",
            join_date=(datetime.utcnow() - timedelta(days=randint(0, 730))).date()
        )
        db.session.add(customer)
        customers.append(customer)
    
    db.session.commit()
    print(f"✓ Created {len(customers)} customers")
    return customers

def populate_orders(customers, products):
    """Create 30 orders"""
    print("Creating 30 orders...")
    orders = []
    statuses = ['Pending', 'Processing', 'Shipped', 'Completed', 'Cancelled']
    payment_methods = ['Credit Card', 'Debit Card', 'PayPal', 'Bank Transfer', 'Cash']
    
    for i in range(30):
        customer = choice(customers)
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{str(i+1).zfill(4)}"
        
        # Ensure unique order number
        while Order.query.filter_by(order_number=order_number).first():
            order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{str(i+1000).zfill(4)}"
        
        # Calculate total first before creating order
        num_items = randint(1, 5)
        selected_products = [choice(products) for _ in range(num_items)]
        total = 0
        order_items_data = []
        
        # Calculate total and prepare order items data
        for product in selected_products:
            quantity = randint(1, 10)
            unit_price = float(product.price)
            subtotal = round(unit_price * quantity, 2)
            total += subtotal
            order_items_data.append({
                'product_id': product.id,
                'quantity': quantity,
                'unit_price': unit_price,
                'subtotal': subtotal
            })
        
        # Create order with total already calculated
        order = Order(
            order_number=order_number,
            customer_id=customer.id,
            total=round(total, 2),  # Set total before adding to session
            status=choice(statuses),
            order_date=(datetime.utcnow() - timedelta(days=randint(0, 90))).date(),
            payment_method=choice(payment_methods),
            shipping_address=customer.address,
            notes=f"Order #{i+1}" if i % 3 == 0 else None
        )
        db.session.add(order)
        db.session.flush()  # Flush to get order.id
        
        # Create order items now that we have order.id
        for item_data in order_items_data:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data['product_id'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                subtotal=item_data['subtotal']
            )
            db.session.add(order_item)
        
        orders.append(order)
    
    db.session.commit()
    print(f"✓ Created {len(orders)} orders")
    return orders

def populate_leads():
    """Create 30 leads"""
    print("Creating 30 leads...")
    leads = []
    statuses = ['New', 'Contacted', 'Qualified', 'Lost']
    sources = ['Website', 'Referral', 'Social Media', 'Email Campaign', 'Trade Show', 'Cold Call']
    
    for i in range(30):
        first_name = choice(FIRST_NAMES)
        last_name = choice(LAST_NAMES)
        name = f"{first_name} {last_name}"
        company = choice(COMPANIES) if i % 2 == 0 else None
        email = generate_email(first_name, last_name, company)
        
        # Ensure unique email
        while Lead.query.filter_by(email=email).first():
            email = f"{first_name.lower()}.{last_name.lower()}{i}@lead.com"
        
        lead = Lead(
            name=name,
            email=email,
            company=company,
            status=choice(statuses),
            source=choice(sources),
            created_at=datetime.utcnow() - timedelta(days=randint(0, 180))
        )
        db.session.add(lead)
        leads.append(lead)
    
    db.session.commit()
    print(f"✓ Created {len(leads)} leads")
    return leads

def populate_deals(customers):
    """Create 30 deals"""
    print("Creating 30 deals...")
    deals = []
    stages = ['New Leads', 'Qualified', 'Proposal', 'Negotiation', 'Closed Won', 'Closed Lost']
    
    for i in range(30):
        customer = choice(customers)
        deal = Deal(
            name=f"Deal with {customer.name}",
            customer_id=customer.id,
            stage=choice(stages),
            value=round(uniform(1000.00, 100000.00), 2),
            probability=randint(10, 90),
            close_date=(datetime.utcnow() + timedelta(days=randint(-30, 90))).date() if i % 2 == 0 else None
        )
        db.session.add(deal)
        deals.append(deal)
    
    db.session.commit()
    print(f"✓ Created {len(deals)} deals")
    return deals

def populate_suppliers():
    """Create 30 suppliers"""
    print("Creating 30 suppliers...")
    suppliers = []
    
    for i in range(30):
        name = f"{choice(['Global', 'Premium', 'Elite', 'Pro', 'Advanced'])} {choice(['Supplies', 'Distributors', 'Vendors', 'Partners', 'Solutions'])} {i+1}"
        
        # Ensure unique name
        while Supplier.query.filter_by(name=name).first():
            name = f"{choice(['Global', 'Premium', 'Elite'])} Supplies {i+100}"
        
        supplier = Supplier(
            name=name,
            contact_info=f"Phone: +1-555-{randint(1000, 9999)}\nEmail: contact@{name.lower().replace(' ', '')}.com\nAddress: {randint(100, 9999)} Business Ave"
        )
        db.session.add(supplier)
        suppliers.append(supplier)
    
    db.session.commit()
    print(f"✓ Created {len(suppliers)} suppliers")
    return suppliers

def populate_purchase_orders(suppliers):
    """Create 30 purchase orders"""
    print("Creating 30 purchase orders...")
    purchase_orders = []
    statuses = ['Pending', 'Shipped', 'Delivered']
    
    for i in range(30):
        supplier = choice(suppliers)
        po_number = f"PO-{datetime.now().strftime('%Y%m%d')}-{str(i+1).zfill(4)}"
        
        # Ensure unique PO number
        while PurchaseOrder.query.filter_by(po_number=po_number).first():
            po_number = f"PO-{datetime.now().strftime('%Y%m%d')}-{str(i+1000).zfill(4)}"
        
        po = PurchaseOrder(
            po_number=po_number,
            supplier_id=supplier.id,
            status=choice(statuses),
            total_amount=round(uniform(500.00, 50000.00), 2),
            order_date=(datetime.utcnow() - timedelta(days=randint(0, 60))).date()
        )
        db.session.add(po)
        purchase_orders.append(po)
    
    db.session.commit()
    print(f"✓ Created {len(purchase_orders)} purchase orders")
    return purchase_orders

def populate_expenses():
    """Create 30 expenses"""
    print("Creating 30 expenses...")
    expenses = []
    categories = ['Office Supplies', 'Travel', 'Marketing', 'Utilities', 'Rent', 'Equipment', 'Software', 'Training']
    vendors = ['Office Depot', 'Amazon Business', 'Staples', 'Dell', 'Microsoft', 'Adobe', 'Google', 'Salesforce']
    
    for i in range(30):
        expense = Expense(
            description=f"{choice(categories)} expense #{i+1}",
            category=choice(categories),
            amount=round(uniform(50.00, 5000.00), 2),
            date=(datetime.utcnow() - timedelta(days=randint(0, 90))).date(),
            vendor=choice(vendors)
        )
        db.session.add(expense)
        expenses.append(expense)
    
    db.session.commit()
    print(f"✓ Created {len(expenses)} expenses")
    return expenses

def populate_projects(users):
    """Create 30 projects"""
    print("Creating 30 projects...")
    projects = []
    statuses = ['Planning', 'In Progress', 'Review', 'Completed']
    project_names = ['Website Redesign', 'Mobile App Development', 'System Migration', 
                     'Cloud Infrastructure', 'Security Audit', 'Database Optimization',
                     'API Integration', 'UI/UX Enhancement', 'Performance Tuning', 'Feature Development']
    
    for i in range(30):
        manager = choice(users) if users else None
        project = Project(
            name=f"{choice(project_names)} {i+1}",
            description=f"Project description for {choice(project_names).lower()} project",
            status=choice(statuses),
            budget=round(uniform(10000.00, 500000.00), 2),
            start_date=(datetime.utcnow() - timedelta(days=randint(0, 180))).date(),
            end_date=(datetime.utcnow() + timedelta(days=randint(30, 365))).date() if i % 2 == 0 else None,
            manager_id=manager.id if manager else None
        )
        db.session.add(project)
        projects.append(project)
    
    db.session.commit()
    print(f"✓ Created {len(projects)} projects")
    return projects

def populate_tasks(projects, users):
    """Create 30 tasks"""
    print("Creating 30 tasks...")
    tasks = []
    statuses = ['To Do', 'In Progress', 'Done']
    task_names = ['Design Review', 'Code Implementation', 'Testing', 'Documentation',
                  'Bug Fix', 'Feature Development', 'Code Review', 'Deployment', 'Research', 'Planning']
    
    for i in range(30):
        project = choice(projects) if projects else None
        assignee = choice(users) if users and i % 2 == 0 else None
        
        task = Task(
            name=f"{choice(task_names)} {i+1}",
            project_id=project.id if project else None,
            assignee_id=assignee.id if assignee else None,
            status=choice(statuses),
            due_date=(datetime.utcnow() + timedelta(days=randint(1, 90))).date() if i % 2 == 0 else None
        )
        db.session.add(task)
        tasks.append(task)
    
    db.session.commit()
    print(f"✓ Created {len(tasks)} tasks")
    return tasks

def populate_attendance(users):
    """Create attendance records for users"""
    print("Creating attendance records...")
    attendance_records = []
    statuses = ['Present', 'On Leave', 'Absent']
    
    # Create attendance for last 30 days for each user
    for user in users[:20]:  # Limit to first 20 users
        for day_offset in range(30):
            date = (datetime.utcnow() - timedelta(days=day_offset)).date()
            
            # Skip weekends (optional)
            if date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                continue
            
            status = choice(statuses)
            check_in = None
            check_out = None
            
            if status == 'Present':
                check_in = datetime.combine(date, datetime.min.time().replace(hour=9, minute=randint(0, 30)))
                check_out = datetime.combine(date, datetime.min.time().replace(hour=17, minute=randint(0, 30)))
            
            attendance = Attendance(
                user_id=user.id,
                date=date,
                check_in=check_in,
                check_out=check_out,
                status=status
            )
            db.session.add(attendance)
            attendance_records.append(attendance)
    
    db.session.commit()
    print(f"✓ Created {len(attendance_records)} attendance records")
    return attendance_records

def populate_user_settings(users):
    """Create user settings for users"""
    print("Creating user settings...")
    settings = []
    
    for idx, user in enumerate(users):
        if not UserSettings.query.filter_by(user_id=user.id).first():
            setting = UserSettings(
                user_id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                company=user.company,
                phone=user.phone,
                email_notifications=True,
                push_notifications=True,
                order_updates=True,
                marketing_emails=idx % 2 == 0,
                weekly_reports=True,
                two_factor_auth=idx % 3 == 0,
                session_timeout='24h',
                password_expiry='90d',
                language='en',
                timezone='UTC',
                theme='light'
            )
            db.session.add(setting)
            settings.append(setting)
    
    db.session.commit()
    print(f"✓ Created {len(settings)} user settings")
    return settings

def main():
    """Main function to populate all tables"""
    print("=" * 60)
    print("Populating SmartBiz360 Database with Sample Data")
    print("=" * 60)
    
    with app.app_context():
        try:
            # Check if data already exists
            if User.query.count() > 10:
                response = input("\n⚠️  Database already contains data. Continue anyway? (y/n): ")
                if response.lower() != 'y':
                    print("Cancelled.")
                    return
            
            # Populate in order (respecting foreign key constraints)
            users = populate_users()
            products = populate_products()
            customers = populate_customers()
            orders = populate_orders(customers, products)
            leads = populate_leads()
            deals = populate_deals(customers)
            suppliers = populate_suppliers()
            purchase_orders = populate_purchase_orders(suppliers)
            expenses = populate_expenses()
            projects = populate_projects(users)
            tasks = populate_tasks(projects, users)
            attendance = populate_attendance(users)
            settings = populate_user_settings(users)
            
            print("\n" + "=" * 60)
            print("✅ Sample data population completed successfully!")
            print("=" * 60)
            print(f"\nSummary:")
            print(f"  - Users: {len(users)}")
            print(f"  - Products: {len(products)}")
            print(f"  - Customers: {len(customers)}")
            print(f"  - Orders: {len(orders)}")
            print(f"  - Leads: {len(leads)}")
            print(f"  - Deals: {len(deals)}")
            print(f"  - Suppliers: {len(suppliers)}")
            print(f"  - Purchase Orders: {len(purchase_orders)}")
            print(f"  - Expenses: {len(expenses)}")
            print(f"  - Projects: {len(projects)}")
            print(f"  - Tasks: {len(tasks)}")
            print(f"  - Attendance Records: {len(attendance)}")
            print(f"  - User Settings: {len(settings)}")
            print("\n🎉 Database is now populated with sample data!")
            
        except Exception as e:
            print(f"\n❌ Error populating database: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

