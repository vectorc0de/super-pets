from flask import Blueprint, request, jsonify
from app.rag.health_rag_service import analyze_pdf_and_classify, insert_data_to_supabase
from flask_cors import CORS

health_rag = Blueprint('health_rag', __name__, url_prefix='/health_rag')

CORS(health_rag)

@health_rag.route('/analyze_pdf', methods=['POST'])
def analyze_pdf():
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"success": False, "error": "No file selected for uploading"}), 400

    pet_id = request.form.get('pet_id')
    if not pet_id:
        return jsonify({"success": False, "error": "pet_id is required in the request"}), 400

    try:
        classified_data = analyze_pdf_and_classify(file, pet_id)

        return jsonify({
            "success": True,
            "message": "PDF analyzed successfully",
            "classified_data": classified_data
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@health_rag.route('/import_to_supabase', methods=['POST'])
def import_to_supabase():
    json_data = request.get_json()

    results = {}
    try:
        for table_name, data in json_data.items():
            if not data:
                continue
            try:
                result = insert_data_to_supabase(table_name, data)
                results[table_name] = {"success": True, "result": result}
            except Exception as e:
                results[table_name] = {"success": False, "error": str(e)}

        return jsonify({
            "success": True,
            "message": "Data processing completed",
            "results": results
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


    # table_name = json_data.get('table_name')
    # if not table_name:
    #     return jsonify({"success": False, "error": "Table name is required"}), 400

    # data = json_data.get('data')
    # if not data:
    #     return jsonify({"success": False, "error": "Data is required"}), 400

    # try:
    #     result = insert_data_to_supabase(table_name, data)

    #     return jsonify({
    #         "success": True,
    #         "message": f"Data successfully inserted into {table_name}",
    #         "result": result
    #     }), 200
