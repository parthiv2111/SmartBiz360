from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, 
    jwt_required, 
    get_jwt_identity,
    create_refresh_token,
    get_jwt
)
from models import db, User, UserSettings
from schemas import user_schema, user_login_schema, user_settings_schema
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import uuid

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/login', methods=['OPTIONS'])
def login_options():
    return ('', 204)

@auth_bp.route('/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate data
        errors = user_schema.validate(data)
        if errors:
            return jsonify({
                'success': False,
                'error': 'Validation error',
                'details': errors
            }), 400
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({
                'success': False,
                'error': 'Email already exists'
            }), 400
        
        # Create user
        user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            company=data.get('company'),
            phone=data.get('phone'),
            role=data.get('role', 'user')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.flush()  # Get the user ID
        
        # Create default settings for the user
        settings = UserSettings(
            user_id=user.id,
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            company=data.get('company'),
            phone=data.get('phone')
        )
        db.session.add(settings)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'data': {
                'user': user_schema.dump(user),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
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

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    try:
        data = request.get_json()
        
        # Validate data
        errors = user_login_schema.validate(data)
        if errors:
            return jsonify({
                'success': False,
                'error': 'Validation error',
                'details': errors
            }), 400
        
        # Find user by email
        user = User.query.filter_by(email=data['email']).first()
        if not user or not user.check_password(data['password']):
            return jsonify({
                'success': False,
                'error': 'Invalid email or password'
            }), 401
        
        if not user.is_active:
            return jsonify({
                'success': False,
                'error': 'Account is deactivated'
            }), 401
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Create tokens
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'data': {
                'user': user_schema.dump(user),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({
                'success': False,
                'error': 'User not found or inactive'
            }), 401
        
        new_token = create_access_token(identity=current_user_id)
        
        return jsonify({
            'success': True,
            'data': {
                'access_token': new_token
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (client should discard token)"""
    try:
        # In a more sophisticated setup, you might want to blacklist the token
        # For now, we'll just return success and let the client handle token removal
        return jsonify({
            'success': True,
            'message': 'Logout successful'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/auth/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': user_schema.dump(user)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/auth/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        data = request.get_json()
        
        # Validate data (excluding password)
        validation_data = {k: v for k, v in data.items() if k != 'password'}
        errors = user_schema.validate(validation_data, partial=True)
        if errors:
            return jsonify({
                'success': False,
                'error': 'Validation error',
                'details': errors
            }), 400
        
        # Check if email already exists (if changing email)
        if 'email' in data and data['email'] != user.email:
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user:
                return jsonify({
                    'success': False,
                    'error': 'Email already exists'
                }), 400
        
        # Update user fields
        for field in ['first_name', 'last_name', 'email', 'company', 'phone']:
            if field in data:
                setattr(user, field, data[field])
        
        # Update password if provided
        if 'password' in data:
            user.set_password(data['password'])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'data': user_schema.dump(user)
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

@auth_bp.route('/auth/forgot-password', methods=['POST'])
def forgot_password():
    """Send OTP for password reset"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email is required'
            }), 400
        
        # Import services
        from services.otp_service import otp_service
        from services.email_service import email_service
        
        # Create OTP for user
        otp_result = otp_service.create_otp_for_user(email)
        
        if not otp_result['success']:
            # Don't reveal if email exists or not for security
            return jsonify({
                'success': True,
                'message': 'If the email exists, an OTP has been sent to your email address'
            }), 200
        
        # Send OTP email
        email_sent = email_service.send_otp_email(
            to_email=email,
            otp_code=otp_result.get('otp_code', ''),
            user_name=otp_result.get('user_name')
        )
        
        if email_sent:
            return jsonify({
                'success': True,
                'message': 'OTP has been sent to your email address',
                'expires_at': otp_result.get('expires_at')
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send OTP email. Please try again.'
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/auth/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP code"""
    try:
        data = request.get_json()
        email = data.get('email')
        otp_code = data.get('otp_code')
        
        if not email or not otp_code:
            return jsonify({
                'success': False,
                'error': 'Email and OTP code are required'
            }), 400
        
        from services.otp_service import otp_service
        
        # Verify OTP
        verification_result = otp_service.verify_otp(email, otp_code)
        
        if verification_result['success']:
            return jsonify({
                'success': True,
                'message': 'OTP verified successfully',
                'user_id': verification_result.get('user_id')
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': verification_result['error']
            }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/auth/reset-password', methods=['POST'])
def reset_password():
    """Reset password with OTP verification"""
    try:
        data = request.get_json()
        email = data.get('email')
        otp_code = data.get('otp_code')
        new_password = data.get('password')
        
        if not email or not otp_code or not new_password:
            return jsonify({
                'success': False,
                'error': 'Email, OTP code, and new password are required'
            }), 400
        
        # Import services
        from services.otp_service import otp_service
        from services.email_service import email_service
        
        # Verify OTP first
        verification_result = otp_service.verify_otp(email, otp_code)
        
        if not verification_result['success']:
            return jsonify({
                'success': False,
                'error': verification_result['error']
            }), 400
        
        # Get user and update password
        user = User.query.get(verification_result['user_id'])
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Update password
        user.set_password(new_password)
        db.session.commit()
        
        # Send success email
        email_service.send_password_reset_success_email(
            to_email=email,
            user_name=f"{user.first_name} {user.last_name}".strip()
        )
        
        return jsonify({
            'success': True,
            'message': 'Password has been reset successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/auth/otp-status', methods=['POST'])
def otp_status():
    """Check OTP status for an email"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email is required'
            }), 400
        
        from services.otp_service import otp_service
        
        status = otp_service.get_otp_status(email)
        
        return jsonify({
            'success': True,
            'data': status
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
