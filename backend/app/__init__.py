"""Flask application factory."""

import logging
from flask import Flask
from flask_cors import CORS
from backend.app.config import config
from backend.app.database.connection import DatabaseConnection
from backend.app.extensions import celery_app
from backend.app.modules.ingestion.routes import ingestion_bp
from backend.app.modules.dashboard.routes import dashboard_bp
from backend.app.modules.diagnostics.routes import diagnostics_bp
from backend.app.modules.forecasting.routes import forecasting_bp
from backend.app.modules.viz.routes import viz_bp

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if config.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def create_app():
    """Create and configure Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['DEBUG'] = config.DEBUG
    
    # Initialize CORS with explicit configuration
    origins = [origin.strip() for origin in config.CORS_ORIGINS.split(',')]
    CORS(
        app,
        origins=origins,
        supports_credentials=True,
        methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
        allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
        expose_headers=['Content-Type', 'X-Request-ID'],
        max_age=3600
    )
    
    # Initialize database connection pool
    try:
        DatabaseConnection.initialize_pool(min_conn=1, max_conn=20)
        logger.info("Database connection pool initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database pool: {e}")
    
    # Initialize Celery
    try:
        celery_app.conf.update(
            broker_url=config.CELERY_BROKER_URL,
            result_backend=config.CELERY_RESULT_BACKEND,
            task_serializer='json',
            accept_content=['json'],
            result_serializer='json',
            timezone='UTC',
            enable_utc=True,
        )
        logger.info("Celery initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Celery: {e}")
    
    # Register blueprints
    app.register_blueprint(ingestion_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(diagnostics_bp)
    app.register_blueprint(forecasting_bp)
    app.register_blueprint(viz_bp)
    
    # Health check route at root
    @app.route('/')
    def root():
        return {'message': 'Pharma Analytics API', 'version': '1.0.0'}, 200
    
    logger.info("Flask application created successfully")
    return app

