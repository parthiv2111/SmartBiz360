from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user or user.role not in ['admin', 'manager']:
                return jsonify({
                    'success': False,
                    'error': 'Admins or managers access required'
                }), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper