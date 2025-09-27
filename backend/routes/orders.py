from flask import Blueprint, request, jsonify
from models import db, Order, OrderItem, Product, Customer
from schemas import order_schema, orders_schema, order_item_schema
from sqlalchemy.exc import IntegrityError
from decimal import Decimal
import uuid
from datetime import datetime

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/orders', methods=['GET'])
def get_orders():
    """Get all orders with pagination and filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        status = request.args.get('status', '')
        customer_id = request.args.get('customer_id', '')
        
        # Build query
        query = Order.query
        
        if search:
            query = query.join(Customer).filter(
                db.or_(
                    Order.order_number.ilike(f'%{search}%'),
                    Customer.name.ilike(f'%{search}%')
                )
            )
        
        if status:
            query = query.filter(Order.status == status)
            
        if customer_id:
            query = query.filter(Order.customer_id == customer_id)
        
        # Pagination
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        orders = pagination.items
        
        return jsonify({
            'success': True,
            'data': orders_schema.dump(orders),
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

@orders_bp.route('/orders/<uuid:order_id>', methods=['GET'])
def get_order(order_id):
    """Get a specific order by ID"""
    try:
        order = Order.query.get_or_404(order_id)
        return jsonify({
            'success': True,
            'data': order_schema.dump(order)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@orders_bp.route('/orders', methods=['POST'])
def create_order():
    """Create a new order"""
    try:
        data = request.get_json()
        
        # Validate data
        errors = order_schema.validate(data)
        if errors:
            return jsonify({
                'success': False,
                'error': 'Validation error',
                'details': errors
            }), 400
        
        # Check if customer exists
        customer = Customer.query.get(data['customer_id'])
        if not customer:
            return jsonify({
                'success': False,
                'error': 'Customer not found'
            }), 404
        
        # Check if order number already exists
        existing_order = Order.query.filter_by(order_number=data['order_number']).first()
        if existing_order:
            return jsonify({
                'success': False,
                'error': 'Order number already exists'
            }), 400
        
        # Calculate total and validate products
        total = Decimal('0.0')
        order_items_data = []
        
        for item_data in data['order_items']:
            product = Product.query.get(item_data['product_id'])
            if not product:
                return jsonify({
                    'success': False,
                    'error': f'Product with ID {item_data["product_id"]} not found'
                }), 404
            
            if product.stock < item_data['quantity']:
                return jsonify({
                    'success': False,
                    'error': f'Insufficient stock for product {product.name}'
                }), 400
            
            subtotal = Decimal(str(item_data['unit_price'])) * item_data['quantity']
            total += subtotal
            
            order_items_data.append({
                'product_id': item_data['product_id'],
                'quantity': item_data['quantity'],
                'unit_price': item_data['unit_price'],
                'subtotal': float(subtotal)
            })
        
        # Create order
        order = Order(
            order_number=data['order_number'],
            customer_id=data['customer_id'],
            total=total,
            status=data.get('status', 'Pending'),
            order_date=data.get('order_date'),
            payment_method=data.get('payment_method'),
            shipping_address=data.get('shipping_address'),
            notes=data.get('notes')
        )
        
        db.session.add(order)
        db.session.flush()  # Get the order ID
        
        # Create order items and update stock
        for item_data in order_items_data:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data['product_id'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                subtotal=item_data['subtotal']
            )
            db.session.add(order_item)
            
            # Update product stock
            product = Product.query.get(item_data['product_id'])
            product.stock -= item_data['quantity']
            
            # Update product status based on stock
            if product.stock == 0:
                product.status = 'Out of Stock'
            elif product.stock <= 10:
                product.status = 'Low Stock'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Order created successfully',
            'data': order_schema.dump(order)
        }), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Order number already exists'
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@orders_bp.route('/orders/<uuid:order_id>', methods=['PUT'])
def update_order(order_id):
    """Update an existing order"""
    try:
        order = Order.query.get_or_404(order_id)
        data = request.get_json()
        
        # Validate data
        errors = order_schema.validate(data, partial=True)
        if errors:
            return jsonify({
                'success': False,
                'error': 'Validation error',
                'details': errors
            }), 400
        
        # Check if order number already exists (if changing order number)
        if 'order_number' in data and data['order_number'] != order.order_number:
            existing_order = Order.query.filter_by(order_number=data['order_number']).first()
            if existing_order:
                return jsonify({
                    'success': False,
                    'error': 'Order number already exists'
                }), 400
        
        # Update basic fields
        for field in ['status', 'payment_method', 'shipping_address', 'notes']:
            if field in data:
                setattr(order, field, data[field])
        
        # Update order items if provided
        if 'order_items' in data:
            # Remove existing order items
            for item in order.order_items:
                # Restore product stock
                product = Product.query.get(item.product_id)
                product.stock += item.quantity
                
                # Update product status
                if product.stock > 10:
                    product.status = 'In Stock'
                elif product.stock > 0:
                    product.status = 'Low Stock'
                else:
                    product.status = 'Out of Stock'
                
                db.session.delete(item)
            
            # Add new order items
            total = Decimal('0.0')
            for item_data in data['order_items']:
                product = Product.query.get(item_data['product_id'])
                if not product:
                    return jsonify({
                        'success': False,
                        'error': f'Product with ID {item_data["product_id"]} not found'
                    }), 404
                
                if product.stock < item_data['quantity']:
                    return jsonify({
                        'success': False,
                        'error': f'Insufficient stock for product {product.name}'
                    }), 400
                
                subtotal = Decimal(str(item_data['unit_price'])) * item_data['quantity']
                total += subtotal
                
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item_data['product_id'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                    subtotal=float(subtotal)
                )
                db.session.add(order_item)
                
                # Update product stock
                product.stock -= item_data['quantity']
                
                # Update product status
                if product.stock == 0:
                    product.status = 'Out of Stock'
                elif product.stock <= 10:
                    product.status = 'Low Stock'
            
            order.total = total
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Order updated successfully',
            'data': order_schema.dump(order)
        }), 200
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Order number already exists'
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@orders_bp.route('/orders/<uuid:order_id>', methods=['DELETE'])
def delete_order(order_id):
    """Delete an order"""
    try:
        order = Order.query.get_or_404(order_id)
        
        # Restore product stock
        for item in order.order_items:
            product = Product.query.get(item.product_id)
            product.stock += item.quantity
            
            # Update product status
            if product.stock > 10:
                product.status = 'In Stock'
            elif product.stock > 0:
                product.status = 'Low Stock'
            else:
                product.status = 'Out of Stock'
        
        db.session.delete(order)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Order deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@orders_bp.route('/orders/stats', methods=['GET'])
def get_order_stats():
    """Get order statistics"""
    try:
        total_orders = Order.query.count()
        completed_orders = Order.query.filter_by(status='Completed').count()
        processing_orders = Order.query.filter_by(status='Processing').count()
        shipped_orders = Order.query.filter_by(status='Shipped').count()
        pending_orders = Order.query.filter_by(status='Pending').count()
        cancelled_orders = Order.query.filter_by(status='Cancelled').count()
        
        return jsonify({
            'success': True,
            'data': {
                'total_orders': total_orders,
                'completed': completed_orders,
                'processing': processing_orders,
                'shipped': shipped_orders,
                'pending': pending_orders,
                'cancelled': cancelled_orders
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
