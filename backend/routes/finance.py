from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from models import db, Expense
from schemas import expense_schema, expenses_schema
from sqlalchemy.exc import IntegrityError

finance_bp = Blueprint('finance', __name__)

@finance_bp.route('/expenses', methods=['GET'])
@jwt_required()
def get_expenses():
    """Get all expenses with pagination and filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        category = request.args.get('category', '')

        query = Expense.query
        if category:
            query = query.filter(Expense.category.ilike(f'%{category}%'))
            
        pagination = query.order_by(Expense.date.desc()).paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            'success': True,
            'data': expenses_schema.dump(pagination.items),
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@finance_bp.route('/expenses', methods=['POST'])
@jwt_required()
def add_expense():
    """Add a new expense record"""
    try:
        data = request.get_json()
        errors = expense_schema.validate(data)
        if errors:
            return jsonify({'success': False, 'error': errors}), 400
        
        new_expense = Expense(**data)
        db.session.add(new_expense)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Expense added successfully',
            'data': expense_schema.dump(new_expense)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@finance_bp.route('/expenses/<uuid:expense_id>', methods=['GET'])
@jwt_required()
def get_expense(expense_id):
    """Get a single expense by ID"""
    try:
        expense = Expense.query.get_or_404(expense_id)
        return jsonify({
            'success': True,
            'data': expense_schema.dump(expense)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@finance_bp.route('/expenses/<uuid:expense_id>', methods=['PUT'])
@jwt_required()
def update_expense(expense_id):
    """Update an existing expense"""
    try:
        expense = Expense.query.get_or_404(expense_id)
        data = request.get_json()
        errors = expense_schema.validate(data, partial=True)
        if errors:
            return jsonify({'success': False, 'error': errors}), 400
            
        for field, value in data.items():
            if hasattr(expense, field):
                setattr(expense, field, value)
        
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Expense updated successfully',
            'data': expense_schema.dump(expense)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@finance_bp.route('/expenses/<uuid:expense_id>', methods=['DELETE'])
@jwt_required()
def delete_expense(expense_id):
    """Delete an expense"""
    try:
        expense = Expense.query.get_or_404(expense_id)
        db.session.delete(expense)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Expense deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500