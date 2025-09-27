from flask import Blueprint, request, jsonify
from models import db, Customer
from schemas import customer_schema, customers_schema
from sqlalchemy.exc import IntegrityError
import uuid

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('/customers', methods=['GET'])
def get_customers():
    """Get all customers with pagination and filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        status = request.args.get('status', '')
        company = request.args.get('company', '')
        
        # Build query
        query = Customer.query
        
        if search:
            query = query.filter(
                db.or_(
                    Customer.name.ilike(f'%{search}%'),
                    Customer.email.ilike(f'%{search}%'),
                    Customer.company.ilike(f'%{search}%')
                )
            )
        
        if status:
            query = query.filter(Customer.status == status)
            
        if company:
            query = query.filter(Customer.company == company)
        
        # Pagination
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        customers = pagination.items
        
        # Add calculated fields for each customer
        customers_data = []
        for customer in customers:
            customer_dict = customer_schema.dump(customer)
            customer_dict['total_orders'] = len(customer.orders)
            customer_dict['total_spent'] = float(sum(order.total for order in customer.orders if order.status != 'Cancelled'))
            customers_data.append(customer_dict)
        
        return jsonify({
            'success': True,
            'data': customers_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@customers_bp.route('/customers/<uuid:customer_id>', methods=['GET'])
def get_customer(customer_id):
    """Get a specific customer by ID"""
    try:
        customer = Customer.query.get_or_404(customer_id)
        customer_data = customer_schema.dump(customer)
        customer_data['total_orders'] = len(customer.orders)
        customer_data['total_spent'] = float(sum(order.total for order in customer.orders if order.status != 'Cancelled'))
        
        return jsonify({
            'success': True,
            'data': customer_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@customers_bp.route('/customers', methods=['POST'])
def create_customer():
    """Create a new customer"""
    try:
        data = request.get_json()
        
        # Validate data
        errors = customer_schema.validate(data)
        if errors:
            return jsonify({
                'success': False,
                'error': 'Validation error',
                'details': errors
            }), 400
        
        # Check if email already exists
        existing_customer = Customer.query.filter_by(email=data['email']).first()
        if existing_customer:
            return jsonify({
                'success': False,
                'error': 'Email already exists'
            }), 400
        
        # Create customer
        customer = Customer(
            name=data['name'],
            email=data['email'],
            company=data.get('company'),
            phone=data.get('phone'),
            status=data.get('status', 'Active'),
            join_date=data.get('join_date'),
            address=data.get('address')
        )
        
        db.session.add(customer)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Customer created successfully',
            'data': customer_schema.dump(customer)
        }), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Email already exists'
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@customers_bp.route('/customers/<uuid:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    """Update an existing customer"""
    try:
        customer = Customer.query.get_or_404(customer_id)
        data = request.get_json()
        
        # Validate data
        errors = customer_schema.validate(data, partial=True)
        if errors:
            return jsonify({
                'success': False,
                'error': 'Validation error',
                'details': errors
            }), 400
        
        # Check if email already exists (if changing email)
        if 'email' in data and data['email'] != customer.email:
            existing_customer = Customer.query.filter_by(email=data['email']).first()
            if existing_customer:
                return jsonify({
                    'success': False,
                    'error': 'Email already exists'
                }), 400
        
        # Update fields
        for field, value in data.items():
            if hasattr(customer, field):
                setattr(customer, field, value)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Customer updated successfully',
            'data': customer_schema.dump(customer)
        }), 200
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Email already exists'
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@customers_bp.route('/customers/<uuid:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    """Delete a customer"""
    try:
        customer = Customer.query.get_or_404(customer_id)
        
        # Check if customer has orders
        if customer.orders:
            return jsonify({
                'success': False,
                'error': 'Cannot delete customer that has orders'
            }), 400
        
        db.session.delete(customer)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Customer deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@customers_bp.route('/customers/stats', methods=['GET'])
def get_customer_stats():
    """Get customer statistics"""
    try:
        total_customers = Customer.query.count()
        active_customers = Customer.query.filter_by(status='Active').count()
        inactive_customers = Customer.query.filter_by(status='Inactive').count()
        
        return jsonify({
            'success': True,
            'data': {
                'total_customers': total_customers,
                'active_customers': active_customers,
                'inactive_customers': inactive_customers
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
