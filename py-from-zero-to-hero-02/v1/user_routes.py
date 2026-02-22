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
