from flask import jsonify, session, current_app
import uuid

def get_client_id():
    client_id = session.get('user_id')
    if not client_id:
        return None, jsonify({"success": False, "error": "Client not logged in"}), 401
    print(client_id)
    return client_id, None, None

class HealthRecordService:

    @staticmethod
    def create_record(table, record_data):
        client_id, error_response, status_code = get_client_id()
        if error_response:
            return error_response, status_code

        try:
            record_id = str(uuid.uuid4())
            record_data['id'] = record_id
            record_data['client_id'] = client_id

            response = current_app.supabase.table(table).insert(record_data).execute()
            if response.data:
                return jsonify({"success": True, "record": response.data[0]}), 201
            else:
                return jsonify({"success": False, "error": "Failed to create record"}), 500
        except Exception as e:
            print(e)
            return jsonify({"success": False, "error": f"An error occurred: {str(e)}"}), 500

    @staticmethod
    def get_records(table):
        client_id, error_response, status_code = get_client_id()
        if error_response:
            return error_response, status_code

        try:
            response = current_app.supabase.table(table).select('*').eq('client_id', client_id).execute()
            if response.data:
                return jsonify({"success": True, "records": response.data}), 200
            else:
                return jsonify({"success": False, "error": "No records found"}), 404
        except Exception as e:
            return jsonify({"success": False, "error": f"An error occurred: {str(e)}"}), 500

    @staticmethod
    def get_record_by_id(table, record_id):
        try:
            response = current_app.supabase.table(table).select('*').eq('id', record_id).execute()
            if response.data:
                return jsonify({"success": True, "record": response.data[0]}), 200
            else:
                return jsonify({"success": False, "error": "Record not found"}), 404
        except Exception as e:
            return jsonify({"success": False, "error": f"An error occurred: {str(e)}"}), 500

    @staticmethod
    def update_record(table, record_id, update_data):
        client_id, error_response, status_code = get_client_id()
        if error_response:
            return error_response, status_code

        try:
            response = current_app.supabase.table(table).update(update_data).eq('id', record_id).eq('client_id', client_id).execute()
            if response.data:
                return jsonify({"success": True, "record": response.data[0]}), 200
            else:
                return jsonify({"success": False, "error": "Failed to update record"}), 500
        except Exception as e:
            return jsonify({"success": False, "error": f"An error occurred: {str(e)}"}), 500

    @staticmethod
    def delete_record(table, record_id):
        client_id, error_response, status_code = get_client_id()
        if error_response:
            return error_response, status_code

        try:
            response = current_app.supabase.table(table).delete().eq('id', record_id).eq('client_id', client_id).execute()
            if response.data:
                return jsonify({"success": True, "message": "Record deleted successfully"}), 200
            else:
                return jsonify({"success": False, "error": "Failed to delete record"}), 500
        except Exception as e:
            return jsonify({"success": False, "error": f"An error occurred: {str(e)}"}), 500
