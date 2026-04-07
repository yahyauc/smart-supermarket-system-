from flask import Blueprint, request, jsonify
from models import db
from models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json()

    username = data.get("username", "").strip()
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not username or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken"}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    user = User(username=username, email=email, role="customer")
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Account created successfully", "user": user.to_dict()}), 201


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()

    identifier = data.get("identifier", "").strip()  # username or email
    password   = data.get("password", "")

    if not identifier or not password:
        return jsonify({"error": "All fields are required"}), 400

    user = User.query.filter(
        (User.username == identifier) | (User.email == identifier)
    ).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({"message": "Login successful", "user": user.to_dict()}), 200


@auth_bp.route("/auth/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([u.to_dict() for u in users]), 200
