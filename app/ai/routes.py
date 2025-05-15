from flask import Blueprint, request, jsonify
from app.ai.ai_service import process_pets_csv_with_ai, process_people_csv_with_ai
from flask_cors import CORS

ai_bp = Blueprint('ai_bp', __name__)
CORS(ai_bp, supports_credentials=True)

@ai_bp.route('/import/pets', methods=['POST'])
def import_pets():
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"success": False, "error": "No file selected for uploading"}), 400

    return process_pets_csv_with_ai(file)

@ai_bp.route('/import/people', methods=['POST'])
def import_people():
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"success": False, "error": "No file selected for uploading"}), 400

    return process_people_csv_with_ai(file)
