import logging
from app import create_app
from dotenv import load_dotenv

# from app import celery

load_dotenv()

# app = create_app()

app, celery = create_app()
app.app_context().push()

if __name__ == "__main__":
    logging.info("Flask app started")
    # app.run(host="0.0.0.0", port=800)


    app.run(host="0.0.0.0", port=8000)


