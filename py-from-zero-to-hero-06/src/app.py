import os
import sys
import logging

# map SRC folder
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from flask import Flask

# DB Settings
from src.database import db

# Import the config class
from config import config_class

# Import user routes
from src.resources import info_bp

# Configure logging
logging.basicConfig(level=logging.INFO)

def create_app():
    config_class.print_config()

    app = Flask(__name__)
    # Load configurations from config.py
    app.config.from_object(config_class)
    # Bind SQLAlchemy to Flask app
    db.init_app(app)
    # Register Blueprints
    app.register_blueprint(info_bp)
    # for the first request, inits DB
    @app.before_request
    def create_db_tables():
        logging.info("app:create_db_tables")
        db.create_all()

    return app


app = create_app()

# Run the Flask App
if __name__ == '__main__':
   if config_class.DEBUG:
     app.run(debug=True, port=config_class.PORT)
   else:
     print(f"Running without debug mode PORT: {config_class.PORT}")
     from waitress import serve
     serve(app, host="0.0.0.0", port=config_class.PORT)