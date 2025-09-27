from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Customer, Product, Order, OrderItem
import csv
import io
from datetime import datetime
import uuid

export_import_bp = Blueprint('export_import', __name__)

@export_import_bp.route('/export/customers', methods=['GET'])
@jwt_required()
def export_customers():
    """Export customers to CSV or Excel"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin', 'manager']:
            return jsonify({
                'success': False,
                'error': 'Insufficient permissions'
            }), 403
        
        format_type = request.args.get('format', 'csv').lower()
        
        if format_type not in ['csv', 'excel']:
            return jsonify({
                'success': False,
                'error': 'Invalid format. Use csv or excel'
            }), 400
        
        # Get all customers
        customers = Customer.query.all()
        
        # Prepare data
        data = []
        for customer in customers:
            data.append({
                'ID': str(customer.id),
                'Name': customer.name,
                'Email': customer.email,
                'Company': customer.company or '',
                'Phone': customer.phone or '',
                'Status': customer.status,
                'Join Date': customer.join_date.strftime('%Y-%m-%d') if customer.join_date else '',
                'Address': customer.address or '',
                'Total Orders': len(customer.orders),
                'Total Spent': sum(float(order.total) for order in customer.orders if order.status != 'Cancelled'),
                'Created At': customer.created_at.strftime('%Y-%m-%d %H:%M:%S') if customer.created_at else ''
            })
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'customers_export_{timestamp}'
        
        if format_type == 'csv':
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=data[0].keys() if data else [])
            writer.writeheader()
            writer.writerows(data)
            output.seek(0)
            
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'{filename}.csv'
            )
        else:  # excel - for now return CSV with excel extension
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=data[0].keys() if data else [])
            writer.writeheader()
            writer.writerows(data)
            output.seek(0)
            
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'{filename}.csv'
            )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@export_import_bp.route('/export/products', methods=['GET'])
@jwt_required()
def export_products():
    """Export products to CSV or Excel"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin', 'manager']:
            return jsonify({
                'success': False,
                'error': 'Insufficient permissions'
            }), 403
        
        format_type = request.args.get('format', 'csv').lower()
        
        if format_type not in ['csv', 'excel']:
            return jsonify({
                'success': False,
                'error': 'Invalid format. Use csv or excel'
            }), 400
        
        # Get all products
        products = Product.query.all()
        
        # Prepare data
        data = []
        for product in products:
            data.append({
                'ID': str(product.id),
                'Name': product.name,
                'SKU': product.sku,
                'Category': product.category,
                'Price': float(product.price),
                'Stock': product.stock,
                'Status': product.status,
                'Image': product.image or '',
                'Description': product.description or '',
                'Created At': product.created_at.strftime('%Y-%m-%d %H:%M:%S') if product.created_at else '',
                'Updated At': product.updated_at.strftime('%Y-%m-%d %H:%M:%S') if product.updated_at else ''
            })
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'products_export_{timestamp}'
        
        if format_type == 'csv':
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=data[0].keys() if data else [])
            writer.writeheader()
            writer.writerows(data)
            output.seek(0)
            
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'{filename}.csv'
            )
        else:  # excel - for now return CSV with excel extension
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=data[0].keys() if data else [])
            writer.writeheader()
            writer.writerows(data)
            output.seek(0)
            
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'{filename}.csv'
            )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@export_import_bp.route('/export/orders', methods=['GET'])
@jwt_required()
def export_orders():
    """Export orders to CSV or Excel"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin', 'manager']:
            return jsonify({
                'success': False,
                'error': 'Insufficient permissions'
            }), 403
        
        format_type = request.args.get('format', 'csv').lower()
        
        if format_type not in ['csv', 'excel']:
            return jsonify({
                'success': False,
                'error': 'Invalid format. Use csv or excel'
            }), 400
        
        # Get all orders
        orders = Order.query.all()
        
        # Prepare data
        data = []
        for order in orders:
            products_list = ', '.join([item.product.name for item in order.order_items])
            data.append({
                'ID': str(order.id),
                'Order Number': order.order_number,
                'Customer': order.customer.name if order.customer else '',
                'Customer Email': order.customer.email if order.customer else '',
                'Products': products_list,
                'Total': float(order.total),
                'Status': order.status,
                'Order Date': order.order_date.strftime('%Y-%m-%d') if order.order_date else '',
                'Payment Method': order.payment_method or '',
                'Shipping Address': order.shipping_address or '',
                'Notes': order.notes or '',
                'Created At': order.created_at.strftime('%Y-%m-%d %H:%M:%S') if order.created_at else '',
                'Updated At': order.updated_at.strftime('%Y-%m-%d %H:%M:%S') if order.updated_at else ''
            })
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'orders_export_{timestamp}'
        
        if format_type == 'csv':
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=data[0].keys() if data else [])
            writer.writeheader()
            writer.writerows(data)
            output.seek(0)
            
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'{filename}.csv'
            )
        else:  # excel - for now return CSV with excel extension
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=data[0].keys() if data else [])
            writer.writeheader()
            writer.writerows(data)
            output.seek(0)
            
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'{filename}.csv'
            )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@export_import_bp.route('/import/customers', methods=['POST'])
@jwt_required()
def import_customers():
    """Import customers from CSV or Excel"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin', 'manager']:
            return jsonify({
                'success': False,
                'error': 'Insufficient permissions'
            }), 403
        
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Read file based on extension
        filename = file.filename.lower()
        if filename.endswith('.csv'):
            # Read CSV file
            file_content = file.read().decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(file_content))
            data_rows = list(csv_reader)
        elif filename.endswith(('.xlsx', '.xls')):
            return jsonify({
                'success': False,
                'error': 'Excel files not supported yet. Please use CSV format.'
            }), 400
        else:
            return jsonify({
                'success': False,
                'error': 'Unsupported file format. Use CSV files'
            }), 400
        
        if not data_rows:
            return jsonify({
                'success': False,
                'error': 'No data found in file'
            }), 400
        
        # Validate required columns
        required_columns = ['Name', 'Email']
        missing_columns = [col for col in required_columns if col not in data_rows[0].keys()]
        if missing_columns:
            return jsonify({
                'success': False,
                'error': f'Missing required columns: {", ".join(missing_columns)}'
            }), 400
        
        # Process data
        imported_count = 0
        errors = []
        
        for index, row in enumerate(data_rows):
            try:
                # Check if customer already exists
                existing_customer = Customer.query.filter_by(email=row['Email']).first()
                if existing_customer:
                    errors.append(f"Row {index + 1}: Email {row['Email']} already exists")
                    continue
                
                # Create customer
                customer = Customer(
                    name=row['Name'],
                    email=row['Email'],
                    company=row.get('Company', ''),
                    phone=row.get('Phone', ''),
                    status=row.get('Status', 'Active'),
                    address=row.get('Address', '')
                )
                
                db.session.add(customer)
                imported_count += 1
                
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully imported {imported_count} customers',
            'data': {
                'imported_count': imported_count,
                'errors': errors[:10]  # Limit errors to first 10
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@export_import_bp.route('/import/products', methods=['POST'])
@jwt_required()
def import_products():
    """Import products from CSV or Excel"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin', 'manager']:
            return jsonify({
                'success': False,
                'error': 'Insufficient permissions'
            }), 403
        
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Read file based on extension
        filename = file.filename.lower()
        if filename.endswith('.csv'):
            # Read CSV file
            file_content = file.read().decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(file_content))
            data_rows = list(csv_reader)
        elif filename.endswith(('.xlsx', '.xls')):
            return jsonify({
                'success': False,
                'error': 'Excel files not supported yet. Please use CSV format.'
            }), 400
        else:
            return jsonify({
                'success': False,
                'error': 'Unsupported file format. Use CSV files'
            }), 400
        
        if not data_rows:
            return jsonify({
                'success': False,
                'error': 'No data found in file'
            }), 400
        
        # Validate required columns
        required_columns = ['Name', 'SKU', 'Category', 'Price']
        missing_columns = [col for col in required_columns if col not in data_rows[0].keys()]
        if missing_columns:
            return jsonify({
                'success': False,
                'error': f'Missing required columns: {", ".join(missing_columns)}'
            }), 400
        
        # Process data
        imported_count = 0
        errors = []
        
        for index, row in enumerate(data_rows):
            try:
                # Check if product already exists
                existing_product = Product.query.filter_by(sku=row['SKU']).first()
                if existing_product:
                    errors.append(f"Row {index + 1}: SKU {row['SKU']} already exists")
                    continue
                
                # Create product
                product = Product(
                    name=row['Name'],
                    sku=row['SKU'],
                    category=row['Category'],
                    price=float(row['Price']),
                    stock=int(row.get('Stock', 0)),
                    status=row.get('Status', 'In Stock'),
                    description=row.get('Description', '')
                )
                
                db.session.add(product)
                imported_count += 1
                
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully imported {imported_count} products',
            'data': {
                'imported_count': imported_count,
                'errors': errors[:10]  # Limit errors to first 10
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
