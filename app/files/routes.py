from flask import Blueprint, request, jsonify, current_app
from flask_cors import CORS
from app.files.file_service import FileService
from functools import wraps

file_bp = Blueprint('file', __name__, url_prefix='/files')

CORS(file_bp, supports_credentials=True)

def init_file_service():
    if not hasattr(current_app, 'file_service'):
        current_app.file_service = FileService(current_app.supabase, 'file_system')
    return current_app.file_service

def with_file_service(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            file_service = init_file_service()
            return f(file_service, *args, **kwargs)
        except Exception:
            return jsonify({"error": "Internal server error"}), 500
    return wrapper

@file_bp.route('/upload', methods=['POST'])
@with_file_service
def upload_file_route(file_service):
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    folder_path = request.form.get('folder_path', '')
    response, status_code = file_service.upload_file(file, folder_path)
    return jsonify(response), status_code

@file_bp.route('/delete', methods=['DELETE'])
@with_file_service
def delete_file_route(file_service):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    file_name = data.get('file_name')
    if not file_name:
        return jsonify({"error": "File name is required"}), 400

    folder_path = data.get('folder_path', '')
    response, status_code = file_service.delete_file(file_name, folder_path)
    return jsonify(response), status_code

@file_bp.route('/list', methods=['GET'])
@with_file_service
def list_files_route(file_service):
    folder_path = request.args.get('folder_path', '')
    recursive = request.args.get('recursive', 'false').lower() == 'true'

    try:
        response, status_code = file_service.list_files(folder_path, recursive)
        return jsonify(response), status_code
    except Exception:
        return jsonify({"error": "Internal server error"}), 500

@file_bp.route('/metadata', methods=['GET'])
@with_file_service
def get_file_metadata_route(file_service):
    file_name = request.args.get('file_name')
    if not file_name:
        return jsonify({"error": "File name is required"}), 400

    folder_path = request.args.get('folder_path', '')
    response, status_code = file_service.get_file_metadata(file_name, folder_path)
    return jsonify(response), status_code

@file_bp.route('/download', methods=['POST'])
@with_file_service
def download_file_route(file_service):
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    file_name = data.get('file_name')
    folder_path = data.get('folder_path')
    
    if not file_name or not folder_path:
        return jsonify({"error": "Both file name and folder path are required"}), 400

    try:
        response, status_code = file_service.get_download_url(file_name, folder_path)
        return jsonify(response), status_code
    except Exception:
        return jsonify({"error": "Internal server error"}), 500

@file_bp.route('/create-folder', methods=['POST'])
@with_file_service
def create_folder_route(file_service):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    folder_name = data.get('folder_name')
    folder_path = data.get('folder_path', '')

    if not folder_name:
        return jsonify({"error": "Folder name is required"}), 400

    response, status_code = file_service.create_folder(folder_name, folder_path)
    return jsonify(response), status_code

@file_bp.route('/delete-folder', methods=['DELETE'])
@with_file_service
def delete_folder_route(file_service):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    folder_name = data.get('folder_name')
    folder_path = data.get('folder_path', '')

    if not folder_name:
        return jsonify({"error": "Folder name is required"}), 400

    response, status_code = file_service.delete_folder(folder_name, folder_path)
    return jsonify(response), status_code
