from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import Profile

bp = Blueprint("profile", __name__, url_prefix="/profile")


@bp.route("/", methods=["POST"])
@jwt_required()
def create_profile():
    data = request.json

    # Save profile data
    new_profile = Profile(
        id_account=data.get("id_account"),
        nik=data.get("nik"),
        name=data.get("name"),
        pob=data.get("pob"),
        dob=data.get("dob"),
        gender=data.get("gender"),
        religion=data.get("religion"),
        marital_status=data.get("marital_status"),
        nationality=data.get("nationality"),
        photo_url=data.get("photo_url"),
        ktp_url=data.get("ktp_url"),
    )
    db.session.add(new_profile)
    db.session.commit()
    return jsonify({"message": "Profile created successfully"}), 201
