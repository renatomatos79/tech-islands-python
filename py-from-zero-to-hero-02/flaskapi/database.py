from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy (without Flask app)
db = SQLAlchemy()

class User(db.Model):
    """User model for storing user details."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
