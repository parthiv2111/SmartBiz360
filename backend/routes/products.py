from flask import Blueprint, request, jsonify
from models import db, Product
from schemas import product_schema, products_schema
from sqlalchemy.exc import IntegrityError
import uuid

products_bp = Blueprint('products', __name__)

@products_bp.route('/products', methods=['GET'])
def get_products():
    """Get all products with pagination and filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        category = request.args.get('category', '')
        status = request.args.get('status', '')
        
        # Build query
        query = Product.query
        
        if search:
            query = query.filter(
                db.or_(
                    Product.name.ilike(f'%{search}%'),
                    Product.sku.ilike(f'%{search}%'),
                    Product.category.ilike(f'%{search}%')
                )
            )
        
        if category:
            query = query.filter(Product.category == category)
            
        if status:
            query = query.filter(Product.status == status)
        
        # Pagination
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        products = pagination.items
        
        return jsonify({
            'success': True,
            'data': products_schema.dump(products),
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

@products_bp.route('/products/<uuid:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a specific product by ID"""
    try:
        product = Product.query.get_or_404(product_id)
        return jsonify({
            'success': True,
            'data': product_schema.dump(product)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@products_bp.route('/products', methods=['POST'])
def create_product():
    """Create a new product"""
    try:
        data = request.get_json()
        
        # Validate data
        errors = product_schema.validate(data)
        if errors:
            return jsonify({
                'success': False,
                'error': 'Validation error',
                'details': errors
            }), 400
        
        # Check if SKU already exists
        existing_product = Product.query.filter_by(sku=data['sku']).first()
        if existing_product:
            return jsonify({
                'success': False,
                'error': 'SKU already exists'
            }), 400
        
        # Create product
        product = Product(
            name=data['name'],
            sku=data['sku'],
            category=data['category'],
            price=data['price'],
            stock=data.get('stock', 0),
            status=data.get('status', 'In Stock'),
            image=data.get('image'),
            description=data.get('description')
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Product created successfully',
            'data': product_schema.dump(product)
        }), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'SKU already exists'
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@products_bp.route('/products/<uuid:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update an existing product"""
    try:
        product = Product.query.get_or_404(product_id)
        data = request.get_json()
        
        # Validate data
        errors = product_schema.validate(data, partial=True)
        if errors:
            return jsonify({
                'success': False,
                'error': 'Validation error',
                'details': errors
            }), 400
        
        # Check if SKU already exists (if changing SKU)
        if 'sku' in data and data['sku'] != product.sku:
            existing_product = Product.query.filter_by(sku=data['sku']).first()
            if existing_product:
                return jsonify({
                    'success': False,
                    'error': 'SKU already exists'
                }), 400
        
        # Update fields
        for field, value in data.items():
            if hasattr(product, field):
                setattr(product, field, value)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Product updated successfully',
            'data': product_schema.dump(product)
        }), 200
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'SKU already exists'
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@products_bp.route('/products/<uuid:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a product"""
    try:
        product = Product.query.get_or_404(product_id)
        
        # Check if product is used in orders
        if product.order_items:
            return jsonify({
                'success': False,
                'error': 'Cannot delete product that is used in orders'
            }), 400
        
        db.session.delete(product)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Product deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@products_bp.route('/products/stats', methods=['GET'])
def get_product_stats():
    """Get product statistics"""
    try:
        total_products = Product.query.count()
        in_stock = Product.query.filter_by(status='In Stock').count()
        low_stock = Product.query.filter_by(status='Low Stock').count()
        out_of_stock = Product.query.filter_by(status='Out of Stock').count()
        
        return jsonify({
            'success': True,
            'data': {
                'total_products': total_products,
                'in_stock': in_stock,
                'low_stock': low_stock,
                'out_of_stock': out_of_stock
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
