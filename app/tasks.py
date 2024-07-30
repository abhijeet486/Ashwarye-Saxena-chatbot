# app/tasks.py

from celery import Celery, shared_task
from flask import Flask
# glo



def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

from .views import process_whatsapp_message  # Import after make_celery

# celery = None  # This will be set when create_celery_app is called in __init__.py

# celery = make_celery(Flask(__name__))

@shared_task(bind=True)
def process_whatsapp_message_async(self, body, req_time):
    try:
        # Your existing logic for processing WhatsApp messages
        process_whatsapp_message(body, req_time)
    except Exception as e:
        # Handle exceptions appropriately
        raise e
