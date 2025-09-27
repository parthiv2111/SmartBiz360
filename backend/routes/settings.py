from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, UserSettings
from schemas import user_settings_schema
from sqlalchemy.exc import IntegrityError
from datetime import datetime

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings/profile', methods=['GET'])
@jwt_required()
def get_profile_settings():
    """Get user profile settings"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Get or create settings
        settings = UserSettings.query.filter_by(user_id=current_user_id).first()
        if not settings:
            settings = UserSettings(user_id=current_user_id)
            db.session.add(settings)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'data': settings.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/settings/profile', methods=['PUT'])
@jwt_required()
def update_profile_settings():
    """Update user profile settings"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        data = request.get_json()
        
        # Get or create settings
        settings = UserSettings.query.filter_by(user_id=current_user_id).first()
        if not settings:
            settings = UserSettings(user_id=current_user_id)
            db.session.add(settings)
        
        # Update profile fields
        profile_fields = ['first_name', 'last_name', 'email', 'company', 'phone']
        for field in profile_fields:
            if field in data:
                setattr(settings, field, data[field])
                # Also update the user record
                setattr(user, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile settings updated successfully',
            'data': settings.to_dict()
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

@settings_bp.route('/settings/notifications', methods=['GET'])
@jwt_required()
def get_notification_settings():
    """Get user notification settings"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get or create settings
        settings = UserSettings.query.filter_by(user_id=current_user_id).first()
        if not settings:
            settings = UserSettings(user_id=current_user_id)
            db.session.add(settings)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'notifications': {
                    'email_notifications': settings.email_notifications,
                    'push_notifications': settings.push_notifications,
                    'order_updates': settings.order_updates,
                    'marketing_emails': settings.marketing_emails,
                    'weekly_reports': settings.weekly_reports
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/settings/notifications', methods=['PUT'])
@jwt_required()
def update_notification_settings():
    """Update user notification settings"""
    try:
        current_user_id = get_jwt_identity()
        
        data = request.get_json()
        
        # Get or create settings
        settings = UserSettings.query.filter_by(user_id=current_user_id).first()
        if not settings:
            settings = UserSettings(user_id=current_user_id)
            db.session.add(settings)
        
        # Update notification fields
        notification_fields = [
            'email_notifications', 'push_notifications', 'order_updates',
            'marketing_emails', 'weekly_reports'
        ]
        for field in notification_fields:
            if field in data:
                setattr(settings, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Notification settings updated successfully',
            'data': {
                'notifications': {
                    'email_notifications': settings.email_notifications,
                    'push_notifications': settings.push_notifications,
                    'order_updates': settings.order_updates,
                    'marketing_emails': settings.marketing_emails,
                    'weekly_reports': settings.weekly_reports
                }
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/settings/security', methods=['GET'])
@jwt_required()
def get_security_settings():
    """Get user security settings"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get or create settings
        settings = UserSettings.query.filter_by(user_id=current_user_id).first()
        if not settings:
            settings = UserSettings(user_id=current_user_id)
            db.session.add(settings)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'security': {
                    'two_factor_auth': settings.two_factor_auth,
                    'session_timeout': settings.session_timeout,
                    'password_expiry': settings.password_expiry
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/settings/security', methods=['PUT'])
@jwt_required()
def update_security_settings():
    """Update user security settings"""
    try:
        current_user_id = get_jwt_identity()
        
        data = request.get_json()
        
        # Get or create settings
        settings = UserSettings.query.filter_by(user_id=current_user_id).first()
        if not settings:
            settings = UserSettings(user_id=current_user_id)
            db.session.add(settings)
        
        # Update security fields
        security_fields = ['two_factor_auth', 'session_timeout', 'password_expiry']
        for field in security_fields:
            if field in data:
                setattr(settings, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Security settings updated successfully',
            'data': {
                'security': {
                    'two_factor_auth': settings.two_factor_auth,
                    'session_timeout': settings.session_timeout,
                    'password_expiry': settings.password_expiry
                }
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/settings/general', methods=['GET'])
@jwt_required()
def get_general_settings():
    """Get user general settings"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get or create settings
        settings = UserSettings.query.filter_by(user_id=current_user_id).first()
        if not settings:
            settings = UserSettings(user_id=current_user_id)
            db.session.add(settings)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'general': {
                    'language': settings.language,
                    'timezone': settings.timezone,
                    'theme': settings.theme
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/settings/general', methods=['PUT'])
@jwt_required()
def update_general_settings():
    """Update user general settings"""
    try:
        current_user_id = get_jwt_identity()
        
        data = request.get_json()
        
        # Get or create settings
        settings = UserSettings.query.filter_by(user_id=current_user_id).first()
        if not settings:
            settings = UserSettings(user_id=current_user_id)
            db.session.add(settings)
        
        # Update general fields
        general_fields = ['language', 'timezone', 'theme']
        for field in general_fields:
            if field in data:
                setattr(settings, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'General settings updated successfully',
            'data': {
                'general': {
                    'language': settings.language,
                    'timezone': settings.timezone,
                    'theme': settings.theme
                }
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
