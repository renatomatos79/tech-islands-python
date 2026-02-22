from flask import Flask, request, jsonify

# Import the config class
from config import config_class

# Import the database and model
from database import db, User

# Import user routes
from user_routes import user_bp

app = Flask(__name__)

# Load configurations from config.py
app.config.from_object(config_class)

# Bind SQLAlchemy to Flask app
db.init_app(app)

# Register Blueprints
app.register_blueprint(user_bp)

# Initialize Database
with app.app_context():
    db.create_all()

# Run the Flask App
if __name__ == '__main__':
    if config_class.DEBUG:
        app.run(debug=True, port=config_class.PORT)
    else:
        print(f"Running without debug mode PORT: {config_class.PORT}")
        from waitress import serve
        serve(app, host="0.0.0.0", port=config_class.PORT)
