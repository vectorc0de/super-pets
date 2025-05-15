import uuid

class PeopleModel:
    def __init__(self, supabase_client):
        self.supabase = supabase_client

    def get_person_by_id(self, person_id):
        try:
            response = self.supabase.table('people').select('*').eq('person_id', person_id).single().execute()
            if hasattr(response, 'data') and response.data:
                return {"success": True, "data": response.data}
            else:
                return {"success": False, "message": "Person not found."}
        except Exception as e:
            return {"success": False, "message": f"An error occurred: {str(e)}"}

    def create_person(self, first_name, last_name, email, phone, address, zipcode, state, city, age, gender, client_id):
        try:
            person_id = str(uuid.uuid4())
            response = self.supabase.table('people').insert({
                'person_id': person_id,
                'client_id': client_id,
                'person_first_name': first_name,
                'person_last_name': last_name,
                'person_email': email,
                'person_phone': phone,
                'person_address': address,
                'person_zipcode': zipcode,
                'person_state': state,
                'person_city': city,
                'person_age': age,
                'person_gender': gender
            }).execute()

            if response.data:
                return {"success": True, "data": response.data}
            else:
                return {"success": False, "message": f"Failed to create person: {response}"}
        except Exception as e:
            return {"success": False, "message": f"An error occurred: {str(e)}"}

    def delete_person(self, person_id):
        try:
            response = self.supabase.table('people').delete().eq('person_id', str(person_id)).execute()
            if hasattr(response, 'data') and response.data:
                return {"success": True}
            else:
                return {"success": False, "message": "Failed to delete person. No data returned from the database."}
        except Exception as e:
            return {"success": False, "message": f"An error occurred: {str(e)}"}

    def get_all_people(self, client_id):
        try:
            response = self.supabase.table('people').select('*').eq('client_id', client_id).execute()
            if hasattr(response, 'data') and response.data:
                return {"success": True, "data": response.data}
            else:
                return {"success": False, "message": "No people found for this client."}
        except Exception as e:
            return {"success": False, "message": f"An error occurred: {str(e)}"}

    def update_person(self, person_id, update_data):
        try:
            response = self.supabase.table('people').update(update_data).eq('person_id', str(person_id)).execute()
            
            if hasattr(response, 'data') and response.data:
                return {"success": True, "data": response.data}
            else:
                return {"success": False, "message": "Failed to update person. No data returned from the database."}
        except Exception as e:
            return {"success": False, "message": f"An error occurred: {str(e)}"}
