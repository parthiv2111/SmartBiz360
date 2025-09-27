from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from models import db
from routes.products import products_bp
from routes.customers import customers_bp
from routes.orders import orders_bp
from routes.dashboard import dashboard_bp
from routes.analytics import analytics_bp
from routes.auth import auth_bp
from routes.settings import settings_bp
from routes.uploads import uploads_bp
from routes.export_import import export_import_bp
import os
from routes.hr import hr_bp
from routes.projects import projects_bp
from routes.finance import finance_bp
from routes.inventory_ext import inventory_ext_bp
from routes.crm import crm_bp


def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load configuration
    from config import config
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)
    
    # Configure CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Create upload directory
    upload_folder = app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    os.makedirs(os.path.join(upload_folder, 'avatars'), exist_ok=True)
    os.makedirs(os.path.join(upload_folder, 'products'), exist_ok=True)
    
    # Register blueprints
    app.register_blueprint(products_bp, url_prefix='/api/v1')
    app.register_blueprint(customers_bp, url_prefix='/api/v1')
    app.register_blueprint(orders_bp, url_prefix='/api/v1')
    app.register_blueprint(dashboard_bp, url_prefix='/api/v1')
    app.register_blueprint(analytics_bp, url_prefix='/api/v1')
    app.register_blueprint(auth_bp, url_prefix='/api/v1')
    app.register_blueprint(settings_bp, url_prefix='/api/v1')
    app.register_blueprint(uploads_bp, url_prefix='/api/v1')
    app.register_blueprint(export_import_bp, url_prefix='/api/v1')
    app.register_blueprint(hr_bp, url_prefix='/api/v1')
    app.register_blueprint(projects_bp, url_prefix='/api/v1')
    app.register_blueprint(crm_bp, url_prefix='/api/v1')
    app.register_blueprint(finance_bp, url_prefix='/api/v1')
    app.register_blueprint(inventory_ext_bp, url_prefix='/api/v1')
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'SmartBiz360 API is running'
        })
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            'message': 'Welcome to SmartBiz360 API',
            'version': '1.0.0',
            'endpoints': {
                'products': '/api/v1/products',
                'customers': '/api/v1/customers',
                'orders': '/api/v1/orders',
                'dashboard': '/api/v1/dashboard',
                'analytics': '/api/v1/analytics',
                'auth': '/api/v1/auth',
                'settings': '/api/v1/settings',
                'uploads': '/api/v1/upload',
                'export_import': '/api/v1/export'
            }
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Resource not found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 'Bad request'
        }), 400
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
