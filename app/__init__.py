from flask import Flask
from app.config import load_configurations, configure_logging
from .views import webhook_blueprint
from .tasks import make_celery

def create_app():
    app = Flask(__name__)

    # Load configurations and logging settings
    load_configurations(app)
    configure_logging()


    # Initialize Celery
    celery = make_celery(app)
    celery.set_default()

    # Import and register blueprints, if any
    app.register_blueprint(webhook_blueprint)

    return app, celery
    # return app
