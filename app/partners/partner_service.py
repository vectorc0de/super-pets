from flask import jsonify, session, current_app
import uuid

def get_client_id():
    client_id = session.get('user_id')
    if not client_id:
        return None, jsonify({"success": False, "error": "Client not logged in"}), 401
    return client_id, None, None

class PartnerService:

    @staticmethod
    def create_partner(partner_data):
        client_id, error_response, status_code = get_client_id()
        if error_response:
            return error_response, status_code

        try:
            partner_id = str(uuid.uuid4())
            partner_data['id'] = partner_id
            partner_data['client_id'] = client_id

            response = current_app.supabase.table('partners').insert(partner_data).execute()
            if response.data:
                return jsonify({"success": True, "partner": response.data[0]}), 201
            else:
                return jsonify({"success": False, "error": "Failed to create partner"}), 500
        except Exception as e:
            return jsonify({"success": False, "error": f"An error occurred: {str(e)}"}), 500

    @staticmethod
    def get_all_partners():
        client_id, error_response, status_code = get_client_id()
        if error_response:
            return error_response, status_code

        try:
            response = current_app.supabase.table('partners').select('*').eq('client_id', client_id).execute()
            if response.data:
                return jsonify({"success": True, "partners": response.data}), 200
            else:
                return jsonify({"success": False, "error": "No partners found"}), 404
        except Exception as e:
            return jsonify({"success": False, "error": f"An error occurred: {str(e)}"}), 500

    @staticmethod
    def get_partner_by_id(partner_id):
        client_id, error_response, status_code = get_client_id()
        if error_response:
            return error_response, status_code

        try:
            response = current_app.supabase.table('partners').select('*').eq('id', partner_id).eq('client_id', client_id).execute()
            if response.data:
                return jsonify({"success": True, "partner": response.data[0]}), 200
            else:
                return jsonify({"success": False, "error": "Partner not found"}), 404
        except Exception as e:
            return jsonify({"success": False, "error": f"An error occurred: {str(e)}"}), 500

    @staticmethod
    def update_partner(partner_id, partner_data):
        client_id, error_response, status_code = get_client_id()
        if error_response:
            return error_response, status_code

        try:
            response = current_app.supabase.table('partners').update(partner_data).eq('id', partner_id).eq('client_id', client_id).execute()
            if response.data:
                return jsonify({"success": True, "partner": response.data[0]}), 200
            else:
                return jsonify({"success": False, "error": "Failed to update partner"}), 500
        except Exception as e:
            return jsonify({"success": False, "error": f"An error occurred: {str(e)}"}), 500

    @staticmethod
    def delete_partner(partner_id):
        client_id, error_response, status_code = get_client_id()
        if error_response:
            return error_response, status_code

        try:
            response = current_app.supabase.table('partners').delete().eq('id', partner_id).eq('client_id', client_id).execute()
            if response.data:
                return jsonify({"success": True, "message": "Partner deleted successfully"}), 200
            else:
                return jsonify({"success": False, "error": "Failed to delete partner"}), 500
        except Exception as e:
            return jsonify({"success": False, "error": f"An error occurred: {str(e)}"}), 500
