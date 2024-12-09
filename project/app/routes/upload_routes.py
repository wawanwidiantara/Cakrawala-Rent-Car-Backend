from flask import Blueprint, request, jsonify, send_from_directory, current_app, url_for
from app.services.ocr_service import extract_id_card
from app.services.photo_profile import extract_face
import os
import uuid
from app import create_app

bp = Blueprint("upload", __name__, url_prefix="/upload")


@bp.route("/id-card", methods=["POST"])
def extract_id():
    if "id_card" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["id_card"]
    file_extension = file.filename.rsplit(".", 1)[-1].lower()
    unique_filename = f"{uuid.uuid4()}.{file_extension}"

    # Ensure the upload folder exists
    upload_folder = create_app().config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    id_card_folder = os.path.join(upload_folder, "ktp")
    os.makedirs(id_card_folder, exist_ok=True)

    file_path = os.path.join(id_card_folder, unique_filename)
    print(f"Attempting to save file to: {file_path}")

    try:
        file.save(file_path)
        print(f"File saved successfully: {file_path}")
        print(os.path.abspath(file_path))
    except Exception as e:
        print(f"Error saving file: {e}")
        return jsonify({"error": "Failed to save file"}), 500
    
    # Extract face from image and save to profile folder
    profile_folder = os.path.join(upload_folder, "profile")
    os.makedirs(profile_folder, exist_ok=True)
    face_filename = f"{uuid.uuid4()}.jpg"
    face_file_path = os.path.join(profile_folder, face_filename)

    try:
        extracted_face = extract_face(file_path)
        extracted_face.save(face_file_path)  # Save extracted face image
    except Exception as e:
        return jsonify({"error": f"Failed to extract face: {str(e)}"}), 500

    # Generate the absolute URL for the extracted face image
    face_url = url_for("upload.serve_media_file", filename=f"profile/{face_filename}", _external=True)


    # Generate the absolute URL for the uploaded file
    absolute_url = url_for("upload.serve_media_file", filename=f"ktp/{unique_filename}", _external=True)

    # Run OCR extraction
    try:
        extracted_data = extract_id_card(file_path)
        extracted_data["ktp_url"] = absolute_url
        extracted_data["photo_url"] = face_url
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "message": "Extraction successful",
        "data": extracted_data,
    }), 200


# Serve media files
@bp.route("/media/<path:filename>", methods=["GET"])
def serve_media_file(filename):
    media_folder = current_app.config["UPLOAD_FOLDER"]
    return send_from_directory(media_folder, filename)
