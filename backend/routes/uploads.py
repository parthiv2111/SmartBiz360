from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from models import db, User, Product
import os
import uuid
from PIL import Image
import io

uploads_bp = Blueprint('uploads', __name__)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def resize_image(image_data, max_size=(800, 800)):
    """Resize image to max_size while maintaining aspect ratio"""
    try:
        img = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # Resize while maintaining aspect ratio
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save to bytes
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        output.seek(0)
        
        return output.getvalue()
    except Exception as e:
        raise Exception(f"Image processing failed: {str(e)}")

@uploads_bp.route('/upload/avatar', methods=['POST'])
@jwt_required()
def upload_avatar():
    """Upload user avatar"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'File type not allowed. Allowed types: PNG, JPG, JPEG, GIF, WEBP'
            }), 400
        
        # Read file data
        file_data = file.read()
        
        # Resize image
        try:
            resized_data = resize_image(file_data, max_size=(400, 400))
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400
        
        # Generate unique filename
        filename = f"avatar_{current_user_id}_{uuid.uuid4().hex}.jpg"
        
        # Ensure upload directory exists
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(resized_data)
        
        # Update user avatar path
        avatar_url = f"/api/v1/files/avatars/{filename}"
        user.avatar = avatar_url
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Avatar uploaded successfully',
            'data': {
                'avatar_url': avatar_url,
                'filename': filename
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@uploads_bp.route('/upload/product-image', methods=['POST'])
@jwt_required()
def upload_product_image():
    """Upload product image"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Check if user has permission to upload product images
        if user.role not in ['admin', 'manager']:
            return jsonify({
                'success': False,
                'error': 'Insufficient permissions'
            }), 403
        
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'File type not allowed. Allowed types: PNG, JPG, JPEG, GIF, WEBP'
            }), 400
        
        # Read file data
        file_data = file.read()
        
        # Resize image
        try:
            resized_data = resize_image(file_data, max_size=(800, 800))
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400
        
        # Generate unique filename
        filename = f"product_{uuid.uuid4().hex}.jpg"
        
        # Ensure upload directory exists
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'products')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(resized_data)
        
        # Return image URL
        image_url = f"/api/v1/files/products/{filename}"
        
        return jsonify({
            'success': True,
            'message': 'Product image uploaded successfully',
            'data': {
                'image_url': image_url,
                'filename': filename
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@uploads_bp.route('/files/<path:filename>', methods=['GET'])
def serve_file(filename):
    """Serve uploaded files"""
    try:
        # Determine file type and directory
        if filename.startswith('avatar_'):
            directory = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
        elif filename.startswith('product_'):
            directory = os.path.join(current_app.config['UPLOAD_FOLDER'], 'products')
        else:
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404
        
        # Check if file exists
        file_path = os.path.join(directory, filename)
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404
        
        return send_from_directory(directory, filename)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@uploads_bp.route('/files/avatars/<filename>', methods=['GET'])
def serve_avatar(filename):
    """Serve avatar files"""
    try:
        directory = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
        return send_from_directory(directory, filename)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@uploads_bp.route('/files/products/<filename>', methods=['GET'])
def serve_product_image(filename):
    """Serve product image files"""
    try:
        directory = os.path.join(current_app.config['UPLOAD_FOLDER'], 'products')
        return send_from_directory(directory, filename)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
