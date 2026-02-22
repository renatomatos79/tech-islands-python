import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base config"""
    SECRET_KEY = os.environ.get("APP_SECRET_KEY", "default_secret_key")
    SQLALCHEMY_DATABASE_URI = os.environ.get("APP_DB_URL", "sqlite:///dev_users.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PORT = os.environ.get("APP_PORT", 8000)

class DevelopmentConfig(Config):
    # The server automatically restarts when you modify Python files
    # If an error occurs, Flask shows an interactive traceback in the browser.
    # We can inspect variables and execute Python code inside the error page.
    # When Debug is True  => RuntimeError: Division by zero
    # When Debug is False => 500 Internal Server Error
    DEBUG = True

class ProductionConfig(Config):
    # Running in production
    # uwsgi --http :8000 --wsgi-file app.py --callable app --master --processes 4 --threads 2
    # DO:
    # - Use Gunicorn, Waitress, or uWSGI
    # - Set DEBUG=False in config.py
    # - Use Nginx or Apache as a reverse proxy
    # Enable HTTPS with SSL
    #
    # DONT DO:
    # - Using (flask run) or app.run(debug=False) in production
    # - Running with DEBUG=True
    # - Exposing Flask directly to the internet
    # - Using only HTTP
    #
    # Windows:
    # python -m waitress --port=8000 app:app
    #
    # Linux:
    # uwsgi --http :8000 --wsgi-file app.py --callable app --master --processes 4 --threads 2
    DEBUG = False

## Current config
config_class = DevelopmentConfig if os.environ.get("APP_ENV") == "development" else ProductionConfig