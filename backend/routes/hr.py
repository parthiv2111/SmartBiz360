from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Attendance, Expense
from schemas import users_schema, user_schema, attendance_schema, attendances_schema
from datetime import datetime, date
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from decimal import Decimal
import uuid

hr_bp = Blueprint('hr', __name__)

@hr_bp.route('/employees', methods=['GET'])
@jwt_required()
def get_employees():
    """Get a list of all employees"""
    # Note: Add role-based access control here for production
    try:
        users = User.query.all()
        # Format user data with status field for frontend compatibility
        employees_data = []
        for user in users:
            user_dict = user_schema.dump(user)
            # Add status field based on is_active
            user_dict['status'] = 'Active' if user.is_active else 'Inactive'
            # Add department, position, join_date if they exist
            user_dict['department'] = user.department
            user_dict['position'] = user.position
            user_dict['joinDate'] = user.join_date.isoformat() if user.join_date else None
            user_dict['join_date'] = user.join_date.isoformat() if user.join_date else None
            employees_data.append(user_dict)
        
        return jsonify({
            'success': True,
            'data': employees_data
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@hr_bp.route('/employees/<uuid:employee_id>', methods=['GET'])
@jwt_required()
def get_employee(employee_id):
    """Get a specific employee by ID"""
    try:
        user = User.query.get_or_404(employee_id)
        user_dict = user_schema.dump(user)
        # Add status field based on is_active
        user_dict['status'] = 'Active' if user.is_active else 'Inactive'
        user_dict['department'] = user.department
        user_dict['position'] = user.position
        user_dict['joinDate'] = user.join_date.isoformat() if user.join_date else None
        user_dict['join_date'] = user.join_date.isoformat() if user.join_date else None
        
        return jsonify({
            'success': True,
            'data': user_dict
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@hr_bp.route('/employees', methods=['POST'])
@jwt_required()
def create_employee():
    """Create a new employee"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('first_name') or not data.get('last_name'):
            return jsonify({
                'success': False,
                'error': 'First name and last name are required'
            }), 400
        
        if not data.get('email'):
            return jsonify({
                'success': False,
                'error': 'Email is required'
            }), 400
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({
                'success': False,
                'error': 'Email already exists'
            }), 400
        
        # Parse join_date if provided
        join_date = None
        if data.get('joinDate'):
            try:
                join_date = datetime.strptime(data['joinDate'], '%Y-%m-%d').date()
            except ValueError:
                pass
        elif data.get('join_date'):
            try:
                join_date = datetime.strptime(data['join_date'], '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # Determine status from is_active or status field
        is_active = True
        if 'status' in data:
            is_active = data['status'] == 'Active'
        elif 'is_active' in data:
            is_active = data['is_active']
        
        # Create user/employee
        user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            company=data.get('company'),
            phone=data.get('phone'),
            department=data.get('department'),
            position=data.get('position'),
            join_date=join_date,
            role=data.get('role', 'user'),
            is_active=is_active
        )
        
        # Set password (default password if not provided)
        password = data.get('password', 'TempPassword123!')
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        user_dict = user_schema.dump(user)
        user_dict['status'] = 'Active' if user.is_active else 'Inactive'
        user_dict['department'] = user.department
        user_dict['position'] = user.position
        user_dict['joinDate'] = user.join_date.isoformat() if user.join_date else None
        
        return jsonify({
            'success': True,
            'message': 'Employee created successfully',
            'data': user_dict
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

@hr_bp.route('/employees/<uuid:employee_id>', methods=['PUT'])
@jwt_required()
def update_employee(employee_id):
    """Update an existing employee"""
    try:
        user = User.query.get_or_404(employee_id)
        data = request.get_json()
        
        # Update fields if provided
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'email' in data:
            # Check if email already exists (if changing email)
            if data['email'] != user.email:
                existing_user = User.query.filter_by(email=data['email']).first()
                if existing_user:
                    return jsonify({
                        'success': False,
                        'error': 'Email already exists'
                    }), 400
            user.email = data['email']
        if 'company' in data:
            user.company = data['company']
        if 'phone' in data:
            user.phone = data['phone']
        if 'department' in data:
            user.department = data['department']
        if 'position' in data:
            user.position = data['position']
        if 'role' in data:
            user.role = data['role']
        
        # Handle join_date
        if 'joinDate' in data or 'join_date' in data:
            join_date_str = data.get('joinDate') or data.get('join_date')
            if join_date_str:
                try:
                    user.join_date = datetime.strptime(join_date_str, '%Y-%m-%d').date()
                except ValueError:
                    pass
        
        # Handle status
        if 'status' in data:
            user.is_active = data['status'] == 'Active'
        elif 'is_active' in data:
            user.is_active = data['is_active']
        
        # Update password if provided
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        
        user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        user_dict = user_schema.dump(user)
        user_dict['status'] = 'Active' if user.is_active else 'Inactive'
        user_dict['department'] = user.department
        user_dict['position'] = user.position
        user_dict['joinDate'] = user.join_date.isoformat() if user.join_date else None
        user_dict['join_date'] = user.join_date.isoformat() if user.join_date else None
        
        return jsonify({
            'success': True,
            'message': 'Employee updated successfully',
            'data': user_dict
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

@hr_bp.route('/employees/<uuid:employee_id>', methods=['DELETE'])
@jwt_required()
def delete_employee(employee_id):
    """Delete an employee"""
    try:
        user = User.query.get_or_404(employee_id)
        
        # Prevent deleting yourself
        current_user_id = get_jwt_identity()
        if str(user.id) == str(current_user_id):
            return jsonify({
                'success': False,
                'error': 'You cannot delete your own account'
            }), 400
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Employee deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@hr_bp.route('/hr/stats', methods=['GET'])
@jwt_required()
def get_hr_stats():
    """Get HR dashboard statistics"""
    try:
        total_employees = User.query.count()
        today = date.today()
        present_today = Attendance.query.filter_by(date=today, status='Present').count()
        on_leave = Attendance.query.filter_by(date=today, status='On Leave').count()
        
        # Payroll: Sum of expenses in 'Payroll' or 'Salary' category for current month
        current_month = datetime.now().month
        current_year = datetime.now().year
        payroll_expenses = db.session.query(func.sum(Expense.amount)).filter(
            func.extract('month', Expense.date) == current_month,
            func.extract('year', Expense.date) == current_year,
            Expense.category.in_(['Payroll', 'Salary', 'Employee Benefits'])
        ).scalar() or Decimal('0.0')
        
        # If no payroll expenses found, calculate from all expenses this month (fallback)
        if payroll_expenses == 0:
            payroll_expenses = db.session.query(func.sum(Expense.amount)).filter(
                func.extract('month', Expense.date) == current_month,
                func.extract('year', Expense.date) == current_year
            ).scalar() or Decimal('0.0')
        
        payroll_this_month = f"${float(payroll_expenses):,.2f}" 
        
        return jsonify({
            'success': True,
            'data': {
                'total_employees': total_employees,
                'present_today': present_today,
                'on_leave': on_leave,
                'payroll': payroll_this_month
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@hr_bp.route('/attendance', methods=['GET'])
@jwt_required()
def get_attendance():
    """Get attendance records for a specific date"""
    try:
        date_str = request.args.get('date')
        if date_str:
            query_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            query_date = date.today()
            
        attendance_records = Attendance.query.filter_by(date=query_date).all()
        
        return jsonify({
            'success': True,
            'data': attendances_schema.dump(attendance_records)
        }), 200
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@hr_bp.route('/attendance', methods=['POST'])
@jwt_required()
def mark_attendance():
    """Mark attendance for the current user (check-in/check-out)"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        action = data.get('action') # 'check_in' or 'check_out'
        
        if not action in ['check_in', 'check_out']:
            return jsonify({'success': False, 'error': "Action must be 'check_in' or 'check_out'"}), 400

        today = date.today()
        attendance_record = Attendance.query.filter_by(user_id=current_user_id, date=today).first()
        
        if action == 'check_in':
            if attendance_record and attendance_record.check_in:
                return jsonify({'success': False, 'error': 'Already checked in today'}), 400
            
            if not attendance_record:
                attendance_record = Attendance(user_id=current_user_id, date=today)
                db.session.add(attendance_record)
                
            attendance_record.status = 'Present'
            attendance_record.check_in = datetime.utcnow()
            
        elif action == 'check_out':
            if not attendance_record or not attendance_record.check_in:
                return jsonify({'success': False, 'error': 'Cannot check out without checking in first'}), 400
            
            if attendance_record.check_out:
                return jsonify({'success': False, 'error': 'Already checked out today'}), 400
                
            attendance_record.check_out = datetime.utcnow()

        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully {action.replace("_", " ")}',
            'data': attendance_schema.dump(attendance_record)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500