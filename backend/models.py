from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

db = SQLAlchemy()

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default='In Stock')  # In Stock, Low Stock, Out of Stock
    image = db.Column(db.String(500))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'sku': self.sku,
            'category': self.category,
            'price': float(self.price),
            'stock': self.stock,
            'status': self.status,
            'image': self.image,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    company = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    status = db.Column(db.String(50), default='Active')  # Active, Inactive
    join_date = db.Column(db.Date, default=datetime.utcnow().date)
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', backref='customer', lazy=True)
    
    def __repr__(self):
        return f'<Customer {self.name}>'
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'email': self.email,
            'company': self.company,
            'phone': self.phone,
            'status': self.status,
            'join_date': self.join_date.isoformat() if self.join_date else None,
            'address': self.address,
            'total_orders': len(self.orders),
            'total_spent': sum(float(order.total) for order in self.orders if order.status != 'Cancelled'),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('customers.id'), nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), default='Pending')  # Pending, Processing, Shipped, Completed, Cancelled
    order_date = db.Column(db.Date, default=datetime.utcnow().date)
    payment_method = db.Column(db.String(100))
    shipping_address = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.order_number}>'
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'order_number': self.order_number,
            'customer': self.customer.name if self.customer else None,
            'customer_id': str(self.customer_id),
            'products': ', '.join([item.product.name for item in self.order_items]),
            'total': float(self.total),
            'status': self.status,
            'date': self.order_date.isoformat() if self.order_date else None,
            'payment': self.payment_method,
            'shipping_address': self.shipping_address,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = db.Column(UUID(as_uuid=True), db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(UUID(as_uuid=True), db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    
    def __repr__(self):
        return f'<OrderItem {self.id}>'
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'order_id': str(self.order_id),
            'product_id': str(self.product_id),
            'product_name': self.product.name if self.product else None,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'subtotal': float(self.subtotal)
        }

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    role = db.Column(db.String(50), default='user')  # admin, user, manager
    avatar = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    department = db.Column(db.String(100))
    position = db.Column(db.String(100))
    join_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'first_name': self.first_name,
            'last_name': self.last_name,
            'name': f"{self.first_name} {self.last_name}",
            'email': self.email,
            'company': self.company,
            'phone': self.phone,
            'role': self.role,
            'avatar': self.avatar,
            'is_active': self.is_active,
            'email_verified': self.email_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class UserSettings(db.Model):
    __tablename__ = 'user_settings'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    
    # Profile settings
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(255))
    company = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    
    # Notification settings
    email_notifications = db.Column(db.Boolean, default=True)
    push_notifications = db.Column(db.Boolean, default=True)
    order_updates = db.Column(db.Boolean, default=True)
    marketing_emails = db.Column(db.Boolean, default=False)
    weekly_reports = db.Column(db.Boolean, default=True)
    
    # Security settings
    two_factor_auth = db.Column(db.Boolean, default=False)
    session_timeout = db.Column(db.String(10), default='24h')  # 1h, 8h, 24h, 7d
    password_expiry = db.Column(db.String(10), default='90d')  # 30d, 60d, 90d, 180d
    
    # General settings
    language = db.Column(db.String(10), default='en')
    timezone = db.Column(db.String(50), default='UTC')
    theme = db.Column(db.String(10), default='light')  # light, dark
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='settings')
    
    def __repr__(self):
        return f'<UserSettings {self.user_id}>'
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'profile': {
                'first_name': self.first_name,
                'last_name': self.last_name,
                'email': self.email,
                'company': self.company,
                'phone': self.phone
            },
            'notifications': {
                'email_notifications': self.email_notifications,
                'push_notifications': self.push_notifications,
                'order_updates': self.order_updates,
                'marketing_emails': self.marketing_emails,
                'weekly_reports': self.weekly_reports
            },
            'security': {
                'two_factor_auth': self.two_factor_auth,
                'session_timeout': self.session_timeout,
                'password_expiry': self.password_expiry
            },
            'general': {
                'language': self.language,
                'timezone': self.timezone,
                'theme': self.theme
            },
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    check_in = db.Column(db.DateTime)
    check_out = db.Column(db.DateTime)
    status = db.Column(db.String(50), nullable=False) # Present, On Leave, Absent
    
    user = db.relationship('User', backref='attendance_records')

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='Planning') # Planning, In Progress, Review, Completed
    budget = db.Column(db.Numeric(12, 2))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    progress = db.Column(db.Integer, default=0)
    manager_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    deleted_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    manager = db.relationship('User', backref='managed_projects')
    tasks = db.relationship('Task', backref='project', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'budget': float(self.budget) if self.budget is not None else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'progress': int(self.progress) if self.progress is not None else 0,
            'manager_id': str(self.manager_id) if self.manager_id else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255), nullable=False)
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'), nullable=False)
    assignee_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    status = db.Column(db.String(50), default='To Do') # To Do, In Progress, Done
    due_date = db.Column(db.Date)
    
    assignee = db.relationship('User', backref='tasks')


class ProjectActivity(db.Model):
    __tablename__ = 'project_activity'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'), nullable=False)
    actor_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    diff = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    project = db.relationship('Project', backref='activities')
    actor = db.relationship('User', backref='project_activities')

    def to_dict(self):
        return {
            'id': str(self.id),
            'project_id': str(self.project_id),
            'actor_id': str(self.actor_id) if self.actor_id else None,
            'action': self.action,
            'diff': self.diff,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

class Lead(db.Model):
    __tablename__ = 'leads'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    company = db.Column(db.String(255))
    status = db.Column(db.String(50), default='New') # New, Contacted, Qualified, Lost
    source = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Deal(db.Model):
    __tablename__ = 'deals'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255), nullable=False)
    customer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('customers.id'), nullable=False)
    stage = db.Column(db.String(50), default='Qualified') # Qualified, Proposal, Negotiation, Closed Won, Closed Lost
    value = db.Column(db.Numeric(12, 2))
    probability = db.Column(db.Integer)
    close_date = db.Column(db.Date)
    
    customer = db.relationship('Customer', backref='deals')

class Expense(db.Model):
    __tablename__ = 'expenses'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    date = db.Column(db.Date, nullable=False)
    vendor = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255), nullable=False, unique=True)
    contact_info = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_orders'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    po_number = db.Column(db.String(50), unique=True, nullable=False)
    supplier_id = db.Column(UUID(as_uuid=True), db.ForeignKey('suppliers.id'), nullable=False)
    status = db.Column(db.String(50), default='Pending') # Pending, Shipped, Delivered
    total_amount = db.Column(db.Numeric(12, 2))
    order_date = db.Column(db.Date, default=datetime.utcnow().date)
    
    supplier = db.relationship('Supplier', backref='purchase_orders')

class PasswordResetOTP(db.Model):
    __tablename__ = 'password_reset_otps'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    otp_code = db.Column(db.String(6), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='password_reset_otps')
    
    def __repr__(self):
        return f'<PasswordResetOTP {self.email}>'
    
    def is_expired(self):
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self):
        return not self.is_used and not self.is_expired()
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'email': self.email,
            'expires_at': self.expires_at.isoformat(),
            'is_used': self.is_used,
            'created_at': self.created_at.isoformat()
        }