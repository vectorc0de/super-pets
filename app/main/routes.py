from flask import Blueprint, jsonify, request, current_app, session
from app.models.people_model import PeopleModel
from app.models.pet_model import PetModel
from app.main.exporting import export_people, export_pets
from flask_cors import CORS

main_bp = Blueprint('main_bp', __name__)
CORS(main_bp, supports_credentials=True)

def get_client_id():
    client_id = session.get('user_id')
    if not client_id:
        return None, jsonify({"success": False, "error": "Client not logged in"}), 401
    return client_id, None, None

@main_bp.route('/people', methods=['GET', 'OPTIONS'])
def get_people_for_client():
    client_id, error_response, status_code = get_client_id()
    if error_response:
        return error_response, status_code

    people_model = PeopleModel(current_app.supabase)
    result = people_model.get_all_people(client_id)

    if result['success']:
        return jsonify(result['data']), 200
    else:
        return jsonify({"success": False, "error": result['message']}), 404


@main_bp.route('/person/<uuid:person_id>/pets', methods=['GET'])
def get_pets_from_person(person_id):
    client_id, error_response, status_code = get_client_id()
    if error_response:
        return error_response, status_code

    pet_model = PetModel(current_app.supabase)
    result = pet_model.get_pets_from_person(person_id)

    if result['success']:
        return jsonify(result['data']), 200
    else:
        return jsonify({"success": False, "error": result['message']}), 404
 
    
@main_bp.route('/pets', methods=['GET'])
def get_pets_for_client():
    client_id, error_response, status_code = get_client_id()
    if error_response:
        return error_response, status_code

    pet_model = PetModel(current_app.supabase)
    result = pet_model.get_all_pets(client_id)
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify({"success": False, "error": result['message']}), 404

@main_bp.route('/person/<uuid:person_id>', methods=['GET'])
def get_person(person_id):
    people_model = PeopleModel(current_app.supabase)
    result = people_model.get_person_by_id(person_id)

    if result['success']:
        return jsonify(result['data']), 200
    else:
        return jsonify({"success": False, "error": result['message']}), 404

@main_bp.route('/pet/<uuid:pet_id>', methods=['GET'])
def get_pet(pet_id):
    pet_model = PetModel(current_app.supabase)
    result = pet_model.get_pet_by_id(pet_id)

    if result['success']:
        return jsonify(result['data']), 200
    else:
        return jsonify({"success": False, "error": result['message']}), 404

@main_bp.route('/add_person', methods=['POST'])
def add_person():
    if not request.is_json:
        return jsonify({"success": False, "error": "Invalid content type. Expected 'application/json'."}), 415

    data = request.get_json()
    required_fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'zipcode', 'state', 'city', 'age', 'gender']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"success": False, "error": f"Missing fields in request: {', '.join(missing_fields)}"}), 400

    client_id, error_response, status_code = get_client_id()
    if error_response:
        return error_response, status_code

    people_model = PeopleModel(current_app.supabase)
    new_person = people_model.create_person(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        phone=data['phone'],
        address=data['address'],
        zipcode=data['zipcode'],
        state=data['state'],
        city=data['city'],
        age=data['age'],
        gender=data['gender'],
        client_id=client_id
    )

    if new_person['success']:
        return jsonify({"success": True, "message": "Person added successfully", "data": new_person['data']}), 201
    else:
        return jsonify({"success": False, "error": new_person['message']}), 400

@main_bp.route('/add_pet', methods=['POST'])
def add_pet():
    if 'photo_file' not in request.files:
        return jsonify({"success": False, "message": "No file part in the request"}), 400

    file = request.files['photo_file']

    if file.filename == '':
        return jsonify({"success": False, "message": "No file selected for uploading"}), 400

    data = request.form
    client_id, error_response, status_code = get_client_id()
    if error_response:
        return error_response, status_code

    pet_model = PetModel(current_app.supabase)
    result = pet_model.add_pet(
        owner_id=data.get('pet_owner_id'),
        pet_name=data.get('pet_name'),
        breed=data.get('pet_breed'),
        pet_type=data.get('pet_type'),
        sex=data.get('pet_sex'),
        color=data.get('pet_color'),
        background=data.get('pet_background'),
        status=data.get('pet_status'),
        photo_file=file,
        client_id=client_id
    )

    print(result)

    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify({"success": False, "error": result['message']}), 400

@main_bp.route('/delete_person/<uuid:person_id>', methods=['DELETE'])
def delete_person(person_id):
    people_model = PeopleModel(current_app.supabase)
    result = people_model.delete_person(person_id)

    if result['success']:
        return jsonify({"message": "Person deleted successfully"}), 200
    else:
        return jsonify({"error": result['message']}), 400

@main_bp.route('/delete_pet/<uuid:pet_id>', methods=['DELETE'])
def delete_pet(pet_id):
    pet_model = PetModel(current_app.supabase)
    result = pet_model.delete_pet(pet_id)

    if result['success']:
        return jsonify({"message": "Pet deleted successfully"}), 200
    else:
        return jsonify({"error": result['message']}), 400

@main_bp.route('/upload_photo', methods=['POST'])
def upload_photo():
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"success": False, "message": "No file selected for uploading"}), 400

    pet_model = PetModel(current_app.supabase)
    result = pet_model.upload_photo(file)

    return jsonify(result), 200 if result['success'] else 400

@main_bp.route('/pet/<uuid:pet_id>', methods=['PUT'])
def update_pet(pet_id):
    if not request.is_json:
        return jsonify({"success": False, "error": "Invalid content type. Expected 'application/json'."}), 415

    data = request.get_json()

    pet_model = PetModel(current_app.supabase)
    result = pet_model.update_pet(pet_id, data)

    if result['success']:
        return jsonify({"success": True, "message": "Pet updated successfully", "data": result['data']}), 200
    else:
        return jsonify({"success": False, "error": result['message']}), 400

@main_bp.route('/person/<uuid:person_id>', methods=['PUT'])
def update_person(person_id):
    try:
        if not request.is_json:
            return jsonify({"success": False, "error": "Invalid content type. Expected 'application/json'."}), 415

        data = request.get_json()

        people_model = PeopleModel(current_app.supabase)
        result = people_model.update_person(person_id, data)

        if result['success']:
            return jsonify({"success": True, "message": "Person updated successfully", "data": result['data']}), 200
        else:
            return jsonify({"success": False, "error": result['message']}), 400

    except Exception as e:
        return jsonify({'success': False, 'error': f"An error occurred while updating the person: {str(e)}"}), 500

@main_bp.route('/export/people', methods=['GET'])
def export_people_route():
    return export_people(current_app.supabase)

@main_bp.route('/export/pets', methods=['GET'])
def export_pets_route():
    return export_pets(current_app.supabase)