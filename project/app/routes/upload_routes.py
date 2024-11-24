from flask import Blueprint, request, jsonify, send_from_directory, current_app
from app.services.ocr_service import extract_id_card
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

    file_path = os.path.join(upload_folder, unique_filename)
    print(f"Attempting to save file to: {file_path}")

    try:
        file.save(file_path)
        print(f"File saved successfully: {file_path}")
        print(os.path.abspath(file_path))
    except Exception as e:
        print(f"Error saving file: {e}")
        return jsonify({"error": "Failed to save file"}), 500

    # Run OCR extraction
    try:
        extracted_data = extract_id_card(file_path)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Extraction successful", "data": extracted_data}), 200

# Serve media files
@bp.route("/media/<path:filename>", methods=["GET"])
def serve_media_file(filename):
    return send_from_directory("/home/wawanwidiantara/Code/py_code/KTP-Information-Extraction-App/project/media", filename)


