<p align="center">
  <img src="https://github.com/renatomatos79/cgi-python-adventure/blob/main/images/logo.PNG" height="400px" width="400px" alt="consoleapp">
</p>


# Quick setup

# Let´s build our first api

### Add a new folder "py-from-zero-to-hero-02"
```
mkdir py-from-zero-to-hero-02
cd py-from-zero-to-hero-02
```

### So, then let´s build a dynamic environment named "adminapi"
```
python -m venv adminapi 
```

### And activate our new dynamic env "capp"
```
.\adminapi\Scripts\activate
```

### Rather than installing packages one by one, let´s use our dependencies file :)
```
pip install -r .\requirements.txt
```

### Finally, we should confirm whether our packages were properly installed
```
pip list
```

# (1) Building a "Hello, Python API"

### (1.1) Create a hello.py file

Copy the this content right below and paste it into the hello.py file

```
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello, Python API!"})

# If the script is executed directly, __name__ is set to '__main__'.
# ===> python app.py
# If the script is imported into another module, __name__ will be the filename (e.g., 'app').

if __name__ == '__main__':
    app.run(debug=True)
```

### (1.2) Running the app
```
python hello.py
```


# (2) Building a real API

### (2.1) Env file

In order to avoid hardcoded content into our Admin API, we are going to build an .env file 
providing these four variables instead.

- APP_SECRET_KEY: 
  The SECRET_KEY is used to generate secure CSRF tokens
  encrypts and signs the session cookies to prevent tampering
  required to sign JSON Web Tokens (JWTs) which also prevents unauthorized modifications of JWT tokens

- APP_DB_URL:
  Connection string used to bind database  

- APP_ENV:
  Identify current env (development or production) 

- APP_PORT: 
  Customise API port number
 
```
APP_SECRET_KEY=super_secure_random_key_123
APP_DB_URL=sqlite:///dev_users.db
APP_ENV=development
APP_PORT=8000
```

### (2.2) Config file

This file contains three config classes: Common config (Config), Dev and Production settings.   

Attention!
config_class object is set according to the "APP_ENV" variable.
When APP_ENV is set to development config_class is a reference to DevelopmentConfig otherwise ProductionConfig.   

```
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
```

### (2.3) Setup database

Create a database.py file using the code right below

```
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy (without Flask app)
db = SQLAlchemy()

class User(db.Model):
"""User model for storing user details."""
id = db.Column(db.Integer, primary_key=True)
name = db.Column(db.String(100), nullable=False)
```

### (2.4) Setting CRUD operations for user entity

Create a user_routes.py file using the code right below in order to map these operations:

- POST: creates an user
- PUT: updates an user
- DELETE: removes an user
- GET: provides either the user list or information related to a single user

Attention!
Once we are handling specific route traffic "/users" we need to provide a
Blueprint to the main app.py

```
from flask import Blueprint, request, jsonify
from database import db, User

# Create a Blueprint for user routes
user_bp = Blueprint("user_bp", __name__)

# Create (POST)
@user_bp.route('/users', methods=['POST'])
def create_user():
    data = request.json
    new_user = User(name=data['name'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created!"}), 201

# Read (GET) - Get all users
@user_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{"id": user.id, "name": user.name} for user in users])

# Read by ID (GET)
@user_bp.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    if user:
        return jsonify({"id": user.id, "name": user.name})
    return jsonify({"message": "User not found"}), 404

# Update (PUT)
@user_bp.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = User.query.get(id)
    if user:
        data = request.json
        user.name = data['name']
        db.session.commit()
        return jsonify({"message": "User updated!"})
    return jsonify({"message": "User not found"}), 404

# Delete (DELETE)
@user_bp.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted!"})
    return jsonify({"message": "User not found"}), 404
```

### (2.5) Add an app.py file to handle the requests and setup the api

This is the entrypoint used by our API
This file is responsible to start a Flask API

```
app = Flask(__name__)
```

Loads the config settings and setup the app
```
from config import config_class
app.config.from_object(config_class)
db.init_app(app)
with app.app_context():
    db.create_all()
```

Maps the "user's routes" using user BluePrint
```
from user_routes import user_bp
app.register_blueprint(user_bp)
```


Use this code right below to fill up the app.py file
```
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

```

### (2.6) Running the app
```
python app.py
```

# (3) Setup Docker image and Container

### (3.1) Providing a Dockerfile

Create a Dockerfile and paste the content right below

```
# Use official Python image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose the port Flask runs on
EXPOSE 80

# Use environment variables for configuration
ENV APP_SECRET_KEY=super_secure_random_key_123
ENV APP_DB_URL=sqlite:///dev_users.db
ENV APP_ENV=development
ENV APP_PORT=80

# Run the application using waitress (production-ready)
CMD ["python", "-m", "waitress", "--port=80", "app:app"]
```

### (3.2) Building the image
```
docker build -t flask-app .
```

### (3.3) Running our container
```
docker run -d --name flask-container -p 8000:80 -e APP_SECRET_KEY=super_key_123 -e APP_DB_URL=sqlite:///dev_users.db -e APP_ENV=production flask-app
```

# So, let's run a quick demo to showcase what we've accomplished so far.
<p align="center">
  <img src="https://github.com/renatomatos79/cgi-python-adventure/blob/main/images/demo-api.gif" height="400px" width="100%" alt="consoleapp">
</p>
