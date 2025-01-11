from flask import Blueprint, request, jsonify, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
from werkzeug.utils import secure_filename
from app import db
from app.models import Profile, Address, Account
from app import create_app
from datetime import datetime

bp = Blueprint("profile", __name__, url_prefix="/profile")
@bp.route("/", methods=["POST"])
@jwt_required()
def create_profile():
    id_account = get_jwt_identity()
    data = request.json

    # Check if a profile already exists for this account
    existing_profile = db.session.query(Profile).filter_by(id_account=id_account).first()
    if existing_profile:
        return jsonify({"error": "Profile already exists for this account."}), 400

    # Convert dob to a Python date object
    try:
        dob = datetime.strptime(data.get("dob"), "%d-%m-%Y").date()
    except ValueError:
        return jsonify({"error": "Invalid date format for dob. Use DD-MM-YYYY."}), 400

    # Save profile data
    new_profile = Profile(
        id_account=id_account,
        nik=data.get("nik"),
        name=data.get("name"),
        pob=data.get("pob"),
        dob=dob,
        gender=data.get("gender"),
        religion=data.get("religion"),
        marital_status=data.get("marital_status"),
        nationality=data.get("nationality"),
        occupation=data.get("occupation"),
        photo_url=data.get("photo_url"),
        ktp_url=data.get("ktp_url"),
    )
    db.session.add(new_profile)

    # Save address data
    new_address = Address(
        id_user=id_account,
        province=data.get("province"),
        city=data.get("city"),
        subdistrict=data.get("subdistrict"),
        village=data.get("village"),
        address=data.get("address"),
        rt=data.get("rt"),
        rw=data.get("rw"),
    )
    db.session.add(new_address)
    db.session.commit()
    return jsonify({"message": "Profile created successfully"}), 201


@bp.route("/<string:user_id>", methods=["GET"])
@jwt_required()
def get_user_info(user_id):
    # Fetch Account information
    account = db.session.query(Account).filter_by(id=user_id).first()
    if not account:
        return jsonify({"error": "User not found"}), 404

    # Fetch Profile information
    profile = db.session.query(Profile).filter_by(id_account=user_id).first()

    # Fetch Address information
    address = db.session.query(Address).filter_by(id_user=user_id).first()

    # Construct response data
    response = {
        "data": {
            "id": account.id,
            "email": account.email,
            "phone": account.phone,
            "nik": profile.nik if profile else None,
            "name": profile.name if profile else None,
            "pob": profile.pob if profile else None,
            "dob": profile.dob.strftime("%Y-%m-%d") if profile and profile.dob else None,
            "gender": profile.gender if profile else None,
            "religion": profile.religion if profile else None,
            "marital_status": profile.marital_status if profile else None,
            "occupation": profile.occupation if profile else None,
            "nationality": profile.nationality if profile else None,
            "photo_url": profile.photo_url if profile else None,
            "ktp_url": profile.ktp_url if profile else None,
            "province": address.province if address else None,
            "city": address.city if address else None,
            "subdistrict": address.subdistrict if address else None,
            "village": address.village if address else None,
            "address": address.address if address else None,
            "rt": address.rt if address else None,
            "rw": address.rw if address else None,
        },
    }
    return jsonify(response), 200