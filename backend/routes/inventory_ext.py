from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from models import db, Supplier, PurchaseOrder
from schemas import supplier_schema, suppliers_schema, purchase_order_schema, purchase_orders_schema
from sqlalchemy.exc import IntegrityError

inventory_ext_bp = Blueprint('inventory_ext', __name__)

# --- Supplier Management Endpoints ---

@inventory_ext_bp.route('/suppliers', methods=['GET'])
@jwt_required()
def get_suppliers():
    """Get all suppliers"""
    try:
        suppliers = Supplier.query.all()
        return jsonify({
            'success': True,
            'data': suppliers_schema.dump(suppliers)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@inventory_ext_bp.route('/suppliers', methods=['POST'])
@jwt_required()
def create_supplier():
    """Create a new supplier"""
    try:
        data = request.get_json()
        errors = supplier_schema.validate(data)
        if errors:
            return jsonify({'success': False, 'error': errors}), 400
        
        new_supplier = Supplier(**data)
        db.session.add(new_supplier)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Supplier created successfully',
            'data': supplier_schema.dump(new_supplier)
        }), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Supplier with this name already exists'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@inventory_ext_bp.route('/suppliers/<uuid:supplier_id>', methods=['GET'])
@jwt_required()
def get_supplier(supplier_id):
    """Get a single supplier by ID"""
    try:
        supplier = Supplier.query.get_or_404(supplier_id)
        return jsonify({'success': True, 'data': supplier_schema.dump(supplier)}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@inventory_ext_bp.route('/suppliers/<uuid:supplier_id>', methods=['PUT'])
@jwt_required()
def update_supplier(supplier_id):
    """Update an existing supplier"""
    try:
        supplier = Supplier.query.get_or_404(supplier_id)
        data = request.get_json()
        errors = supplier_schema.validate(data, partial=True)
        if errors:
            return jsonify({'success': False, 'error': errors}), 400
            
        for field, value in data.items():
            setattr(supplier, field, value)
            
        db.session.commit()
        return jsonify({
            'success': True, 
            'message': 'Supplier updated successfully',
            'data': supplier_schema.dump(supplier)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@inventory_ext_bp.route('/suppliers/<uuid:supplier_id>', methods=['DELETE'])
@jwt_required()
def delete_supplier(supplier_id):
    """Delete a supplier"""
    try:
        supplier = Supplier.query.get_or_404(supplier_id)
        if supplier.purchase_orders:
            return jsonify({'success': False, 'error': 'Cannot delete supplier with existing purchase orders'}), 400
            
        db.session.delete(supplier)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Supplier deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# --- Purchase Order Management Endpoints ---

@inventory_ext_bp.route('/purchase-orders', methods=['GET'])
@jwt_required()
def get_purchase_orders():
    """Get all purchase orders"""
    try:
        purchase_orders = PurchaseOrder.query.all()
        return jsonify({
            'success': True,
            'data': purchase_orders_schema.dump(purchase_orders)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@inventory_ext_bp.route('/purchase-orders', methods=['POST'])
@jwt_required()
def create_purchase_order():
    """Create a new purchase order"""
    try:
        data = request.get_json()
        errors = purchase_order_schema.validate(data)
        if errors:
            return jsonify({'success': False, 'error': errors}), 400
        
        if not Supplier.query.get(data['supplier_id']):
            return jsonify({'success': False, 'error': 'Supplier not found'}), 404
            
        new_po = PurchaseOrder(**data)
        db.session.add(new_po)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Purchase order created successfully',
            'data': purchase_order_schema.dump(new_po)
        }), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Purchase order with this PO number already exists'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@inventory_ext_bp.route('/purchase-orders/<uuid:po_id>', methods=['GET'])
@jwt_required()
def get_purchase_order(po_id):
    """Get a single purchase order by ID"""
    try:
        po = PurchaseOrder.query.get_or_404(po_id)
        return jsonify({'success': True, 'data': purchase_order_schema.dump(po)}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@inventory_ext_bp.route('/purchase-orders/<uuid:po_id>', methods=['PUT'])
@jwt_required()
def update_purchase_order(po_id):
    """Update an existing purchase order"""
    try:
        po = PurchaseOrder.query.get_or_404(po_id)
        data = request.get_json()
        errors = purchase_order_schema.validate(data, partial=True)
        if errors:
            return jsonify({'success': False, 'error': errors}), 400
            
        for field, value in data.items():
            setattr(po, field, value)
            
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Purchase order updated successfully',
            'data': purchase_order_schema.dump(po)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@inventory_ext_bp.route('/purchase-orders/<uuid:po_id>', methods=['DELETE'])
@jwt_required()
def delete_purchase_order(po_id):
    """Delete a purchase order"""
    try:
        po = PurchaseOrder.query.get_or_404(po_id)
        db.session.delete(po)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Purchase order deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500