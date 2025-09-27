from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Attendance
from schemas import users_schema, attendance_schema, attendances_schema
from datetime import datetime, date

hr_bp = Blueprint('hr', __name__)

@hr_bp.route('/employees', methods=['GET'])
@jwt_required()
def get_employees():
    """Get a list of all employees"""
    # Note: Add role-based access control here for production
    try:
        users = User.query.all()
        return jsonify({
            'success': True,
            'data': users_schema.dump(users)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@hr_bp.route('/hr/stats', methods=['GET'])
@jwt_required()
def get_hr_stats():
    """Get HR dashboard statistics"""
    try:
        total_employees = User.query.count()
        today = date.today()
        present_today = Attendance.query.filter_by(date=today, status='Present').count()
        on_leave = Attendance.query.filter_by(date=today, status='On Leave').count()
        
        # Payroll is a placeholder as it's a complex domain
        payroll_this_month = "$150,000" 
        
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