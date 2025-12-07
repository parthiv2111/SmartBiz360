from marshmallow import Schema, fields, validate, ValidationError
from datetime import datetime

class ProductSchema(Schema):
    id = fields.UUID(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    sku = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    category = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    price = fields.Decimal(required=True, places=2, validate=validate.Range(min=0))
    stock = fields.Int(validate=validate.Range(min=0))
    status = fields.Str(validate=validate.OneOf(['In Stock', 'Low Stock', 'Out of Stock']))
    image = fields.Str(validate=validate.Length(max=500))
    description = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class CustomerSchema(Schema):
    id = fields.UUID(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    email = fields.Email(required=True)
    company = fields.Str(validate=validate.Length(max=255))
    phone = fields.Str(validate=validate.Length(max=50))
    status = fields.Str(validate=validate.OneOf(['Active', 'Inactive']))
    join_date = fields.Date()
    address = fields.Str()
    total_orders = fields.Int(dump_only=True)
    total_spent = fields.Decimal(dump_only=True, places=2)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class OrderItemSchema(Schema):
    id = fields.UUID(dump_only=True)
    product_id = fields.UUID(required=True)
    quantity = fields.Int(required=True, validate=validate.Range(min=1))
    unit_price = fields.Decimal(required=True, places=2, validate=validate.Range(min=0))
    subtotal = fields.Decimal(dump_only=True, places=2)

class OrderSchema(Schema):
    id = fields.UUID(dump_only=True)
    order_number = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    customer_id = fields.UUID(required=True)
    total = fields.Decimal(required=True, places=2, validate=validate.Range(min=0))
    status = fields.Str(validate=validate.OneOf(['Pending', 'Processing', 'Shipped', 'Completed', 'Cancelled']))
    order_date = fields.Date()
    payment_method = fields.Str(validate=validate.Length(max=100))
    shipping_address = fields.Str()
    notes = fields.Str()
    order_items = fields.Nested(OrderItemSchema, many=True, required=True)
    customer = fields.Str(dump_only=True)
    products = fields.Str(dump_only=True)
    date = fields.Date(dump_only=True)
    payment = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class DashboardStatsSchema(Schema):
    total_revenue = fields.Decimal(places=2)
    active_customers = fields.Int()
    products_sold = fields.Int()
    pending_orders = fields.Int()

class AnalyticsSchema(Schema):
    total_revenue = fields.Decimal(places=2)
    new_customers = fields.Int()
    conversion_rate = fields.Decimal(places=2)
    avg_order_value = fields.Decimal(places=2)
    customer_satisfaction = fields.Decimal(places=2)
    profit_margin = fields.Decimal(places=2)
    avg_delivery_time = fields.Decimal(places=2)

class UserSchema(Schema):
    id = fields.UUID(dump_only=True)
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8), load_only=True)
    company = fields.Str(validate=validate.Length(max=255))
    phone = fields.Str(validate=validate.Length(max=50))
    role = fields.Str(validate=validate.OneOf(['admin', 'user', 'manager']))
    avatar = fields.Str(validate=validate.Length(max=500))
    is_active = fields.Bool()
    email_verified = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    last_login = fields.DateTime(dump_only=True)

class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=1))

class UserSettingsSchema(Schema):
    id = fields.UUID(dump_only=True)
    user_id = fields.UUID(dump_only=True)
    
    # Profile settings
    first_name = fields.Str(validate=validate.Length(max=100))
    last_name = fields.Str(validate=validate.Length(max=100))
    email = fields.Email()
    company = fields.Str(validate=validate.Length(max=255))
    phone = fields.Str(validate=validate.Length(max=50))
    
    # Notification settings
    email_notifications = fields.Bool()
    push_notifications = fields.Bool()
    order_updates = fields.Bool()
    marketing_emails = fields.Bool()
    weekly_reports = fields.Bool()
    
    # Security settings
    two_factor_auth = fields.Bool()
    session_timeout = fields.Str(validate=validate.OneOf(['1h', '8h', '24h', '7d']))
    password_expiry = fields.Str(validate=validate.OneOf(['30d', '60d', '90d', '180d']))
    
    # General settings
    language = fields.Str(validate=validate.OneOf(['en', 'es', 'fr', 'de']))
    timezone = fields.Str(validate=validate.Length(max=50))
    theme = fields.Str(validate=validate.OneOf(['light', 'dark']))
    
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class AttendanceSchema(Schema):
    id = fields.UUID(dump_only=True)
    user_id = fields.UUID(required=True)
    date = fields.Date(required=True)
    check_in = fields.DateTime()
    check_out = fields.DateTime()
    status = fields.Str(required=True)

class TaskSchema(Schema):
    id = fields.UUID(dump_only=True)
    name = fields.Str(required=True)
    project_id = fields.UUID(required=True)
    assignee_id = fields.UUID()
    status = fields.Str()
    due_date = fields.Date()

class ProjectSchema(Schema):
    id = fields.UUID(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    status = fields.Str()
    budget = fields.Decimal(places=2)
    start_date = fields.Date()
    end_date = fields.Date()
    progress = fields.Int()
    manager_id = fields.UUID()
    tasks = fields.Nested(TaskSchema, many=True, dump_only=True)
    created_at = fields.DateTime(dump_only=True)

class LeadSchema(Schema):
    id = fields.UUID(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    company = fields.Str()
    status = fields.Str()
    source = fields.Str()
    created_at = fields.DateTime(dump_only=True)

class DealSchema(Schema):
    id = fields.UUID(dump_only=True)
    name = fields.Str(required=True)
    customer_id = fields.UUID(required=True)
    stage = fields.Str()
    value = fields.Decimal(places=2)
    probability = fields.Int()
    close_date = fields.Date()

class ExpenseSchema(Schema):
    id = fields.UUID(dump_only=True)
    description = fields.Str(required=True)
    category = fields.Str(required=True)
    amount = fields.Decimal(required=True, places=2)
    date = fields.Date(required=True)
    vendor = fields.Str()
    created_at = fields.DateTime(dump_only=True)

class SupplierSchema(Schema):
    id = fields.UUID(dump_only=True)
    name = fields.Str(required=True)
    contact_info = fields.Str()

class PurchaseOrderSchema(Schema):
    id = fields.UUID(dump_only=True)
    po_number = fields.Str(required=True)
    supplier_id = fields.UUID(required=True)
    status = fields.Str()
    total_amount = fields.Decimal(places=2)
    order_date = fields.Date()


# Schema instances
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
order_item_schema = OrderItemSchema()
order_items_schema = OrderItemSchema(many=True)
dashboard_stats_schema = DashboardStatsSchema()
analytics_schema = AnalyticsSchema()
user_schema = UserSchema()
users_schema = UserSchema(many=True)
user_login_schema = UserLoginSchema()
user_settings_schema = UserSettingsSchema()
attendance_schema = AttendanceSchema()
attendances_schema = AttendanceSchema(many=True)
project_schema = ProjectSchema()
projects_schema = ProjectSchema(many=True)
task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)
lead_schema = LeadSchema()
leads_schema = LeadSchema(many=True)
deal_schema = DealSchema()
deals_schema = DealSchema(many=True)
expense_schema = ExpenseSchema()
expenses_schema = ExpenseSchema(many=True)
supplier_schema = SupplierSchema()
suppliers_schema = SupplierSchema(many=True)
purchase_order_schema = PurchaseOrderSchema()
purchase_orders_schema = PurchaseOrderSchema(many=True)