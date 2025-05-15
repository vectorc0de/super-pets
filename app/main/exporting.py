import csv
import io
from flask import session, jsonify, make_response
from app.models.people_model import PeopleModel
from app.models.pet_model import PetModel

def export_people(supabase_client):
    try:
        client_id = session.get('user_id')
        if not client_id:
            return jsonify({"success": False, "error": "Client not logged in"}), 401

        people_model = PeopleModel(supabase_client)
        result = people_model.get_all_people(client_id)

        if not result['success']:
            return jsonify({"success": False, "error": result['message']}), 404

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            "person_id", "client_id", "person_first_name", "person_last_name", "person_email",
            "person_phone", "person_address", "person_zipcode", "person_state", "person_city", "person_age", "person_gender", "created_at"
        ])
        writer.writeheader()
        writer.writerows(result['data'])

        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = "attachment; filename=people.csv"
        response.headers["Content-type"] = "text/csv"
        return response

    except Exception as e:
        return jsonify({"success": False, "error": f"An error occurred while exporting people data: {str(e)}"}), 500


def export_pets(supabase_client):
    try:
        client_id = session.get('user_id')
        if not client_id:
            return jsonify({"success": False, "error": "Client not logged in"}), 401

        pet_model = PetModel(supabase_client)
        result = pet_model.get_all_pets(client_id)

        if not result['success']:
            return jsonify({"success": False, "error": result['message']}), 404

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            "pet_id", "pet_name", "pet_owner_id", "pet_breed", "pet_type", "pet_sex", "pet_photo",
            "pet_color", "pet_background", "pet_status", "client_id", "created_at"
        ])
        writer.writeheader()
        writer.writerows(result['data'])

        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = "attachment; filename=pets.csv"
        response.headers["Content-type"] = "text/csv"
        return response

    except Exception as e:
        return jsonify({"success": False, "error": f"An error occurred while exporting pets data: {str(e)}"}), 500
