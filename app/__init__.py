from flask import Flask
from app.config import load_configurations, configure_logging
from .views import webhook_blueprint
from .ui_views import ui_blueprint
from .tasks import make_celery

def create_app():
    app = Flask(__name__)
    
    # Configure Flask app
    app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes

    # Load configurations and logging settings
    load_configurations(app)
    configure_logging()

    # Initialize Celery
    celery = make_celery(app)
    celery.set_default()

    # Import and register blueprints
    app.register_blueprint(webhook_blueprint, url_prefix="/webhook")
    app.register_blueprint(ui_blueprint)

    return app, celery
