from flask import Blueprint, request, jsonify
from app import db
from app.models import Account
from flask_jwt_extended import create_access_token

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")
    confirm_password = data.get("confirm_password")
    phone = data.get("phone")

    if password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400

    # Save account
    new_account = Account(email=email, password=password, phone=phone)
    db.session.add(new_account)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


@bp.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = Account.query.filter_by(email=email, password=password).first()
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity=user.id)
    return jsonify({"token": token}), 200
