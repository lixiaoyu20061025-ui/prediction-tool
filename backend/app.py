"""
Main Flask Application Entry Point
预测工具 - Flask 主应用程序
"""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import logging
import os
from datetime import datetime

# Initialize SQLAlchemy
db = SQLAlchemy()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_name='config'):
    """
    Application Factory Pattern
    创建Flask应用实例
    
    Args:
        config_name: Configuration module name
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    try:
        if os.path.exists('config.py'):
            app.config.from_pyfile('config.py')
        else:
            app.config.from_pyfile('config.example.py')
            logger.warning('Using config.example.py - Please create config.py with your settings')
    except Exception as e:
        logger.error(f'Failed to load configuration: {e}')
        raise
    
    # Initialize database
    db.init_app(app)
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        logger.info('Database tables created')
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'Prediction Tool'
        }), 200
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def index():
        """API root endpoint"""
        return jsonify({
            'name': 'Prediction Tool API',
            'version': '1.0.0',
            'description': '多功能预测工具 - 足球、术数、财务预测',
            'endpoints': {
                'football': '/api/football',
                'divination': '/api/divination',
                'finance': '/api/finance',
                'health': '/health'
            }
        }), 200
    
    logger.info('Flask application created successfully')
    return app


def register_blueprints(app):
    """
    Register all blueprints
    注册所有蓝图
    """
    # Football blueprint (to be created)
    try:
        from api.routes import create_football_blueprint
        app.register_blueprint(create_football_blueprint(), url_prefix='/api/football')
        logger.info('Football blueprint registered')
    except ImportError:
        logger.warning('Football blueprint not found')
    
    # Divination blueprint (to be created)
    try:
        from api.routes import create_divination_blueprint
        app.register_blueprint(create_divination_blueprint(), url_prefix='/api/divination')
        logger.info('Divination blueprint registered')
    except ImportError:
        logger.warning('Divination blueprint not found')
    
    # Finance blueprint (to be created)
    try:
        from api.routes import create_finance_blueprint
        app.register_blueprint(create_finance_blueprint(), url_prefix='/api/finance')
        logger.info('Finance blueprint registered')
    except ImportError:
        logger.warning('Finance blueprint not found')


def register_error_handlers(app):
    """
    Register error handlers
    注册错误处理器
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request', 'message': str(error)}), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found', 'message': 'The requested resource was not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f'Internal server error: {error}')
        return jsonify({'error': 'Internal server error', 'message': str(error)}), 500


if __name__ == '__main__':
    app = create_app()
    app.run(
        host=app.config.get('HOST', '0.0.0.0'),
        port=app.config.get('PORT', 5000),
        debug=app.config.get('DEBUG', True)
    )