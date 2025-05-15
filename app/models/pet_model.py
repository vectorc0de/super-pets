import uuid

class PetModel:
    def __init__(self, supabase_client):
        self.supabase = supabase_client

    def get_pets_from_person(self, person_id):
        try:
            response = self.supabase.table('pets').select('*').eq('pet_owner_id', person_id).execute()

            if response.data:
                return {"success": True, "data": response.data}
            else:
                if response.error:
                    return {"success": False, "message": response.error['message']}
                return {"success": False, "message": "No pets found for this person"}
        except Exception as e:
            return {"success": False, "message": f"An error occurred: {str(e)}"}

    def get_pet_by_id(self, pet_id):
        try:
            response = self.supabase.table('pets').select('*').eq('pet_id', str(pet_id)).single().execute()
            if hasattr(response, 'data') and response.data:
                return {"success": True, "data": response.data}
            else:
                return {"success": False, "message": "Pet not found."}
        except Exception as e:
            return {"success": False, "message": f"An error occurred: {str(e)}"}

    def delete_pet(self, pet_id):
        try:
            response = self.supabase.table('pets').delete().eq('pet_id', str(pet_id)).execute()
            if hasattr(response, 'data') and response.data:
                return {"success": True}
            elif hasattr(response, 'error') and response.error:
                return {"success": False, "message": response.error['message']}
            else:
                return {"success": False, "message": "Failed to delete pet. No data returned from the database."}
        except Exception as e:
            return {"success": False, "message": f"An error occurred: {str(e)}"}

    def get_all_pets(self, client_id):
        try:
            response = self.supabase.table('pets').select('*').eq('client_id', client_id).eq('pet_status', 'Available').execute()

            if hasattr(response, 'data') and response.data:
        
                total_pets = len(response.data)
                return {"success": True, "total_pets": total_pets, "data": response.data}
            else:
                return {"success": False, "message": "No available pets found for this client."}
        except Exception as e:
            return {"success": False, "message": f"An error occurred: {str(e)}"}

    def upload_photo(self, file, bucket_name="pet-photos"):
        try:
            if file is None:
                return {"success": True, "url": None}
            
            if isinstance(file, str):
                return {"success": True, "url": file}

            file_extension = file.filename.split('.')[-1]
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            file_content = file.read()
            response = self.supabase.storage.from_(bucket_name).upload(unique_filename, file_content)

            if isinstance(response, dict) and 'error' in response:
                return {"success": False, "message": f"Failed to upload photo: {response['error']['message']}"}

            photo_url_response = self.supabase.storage.from_(bucket_name).get_public_url(unique_filename)

            if isinstance(photo_url_response, str):
                return {"success": True, "url": photo_url_response}
            elif isinstance(photo_url_response, dict) and 'publicURL' in photo_url_response:
                return {"success": True, "url": photo_url_response['publicURL']}
            else:
                return {"success": False, "message": "Failed to retrieve the public URL of the uploaded photo."}
        except Exception as e:
            return {"success": False, "message": f"An error occurred: {str(e)}"}

    def add_pet(self, owner_id, pet_name, breed, pet_type, sex, color, background, status, photo_file, client_id):
        try:
            if photo_file is None:
                photo_url = None
            elif isinstance(photo_file, str):
                photo_url = photo_file
            else:
                upload_result = self.upload_photo(photo_file)
                if not upload_result['success']:
                    return {"success": False, "message": upload_result['message']}
                photo_url = upload_result['url']

            pet_id = str(uuid.uuid4())

            response = self.supabase.table('pets').insert({
                'pet_id': pet_id,
                'pet_name': pet_name,
                'pet_owner_id': owner_id,
                'pet_breed': breed,
                'pet_type': pet_type,
                'pet_sex': sex,
                'pet_color': color,
                'pet_background': background,
                'pet_status': status,
                'pet_photo': photo_url,
                'client_id': client_id
            }).execute()

            if response.data:
                return {"success": True, "data": response.data, "pet_id": pet_id}
            else:
                return {"success": False, "message": f"Failed to add pet: {response}"}
        except Exception as e:
            return {"success": False, "message": f"An error occurred: {str(e)}"}

    def update_pet(self, pet_id, update_data):
        try:
            response = self.supabase.table('pets').update(update_data).eq('pet_id', str(pet_id)).execute()

            if hasattr(response, 'data') and response.data:
                return {"success": True, "data": response.data}
            else:
                return {"success": False, "message": "Failed to update pet. No data returned from the database."}
        except Exception as e:
            return {"success": False, "message": f"An error occurred: {str(e)}"}
