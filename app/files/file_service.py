import os
import datetime
from flask import session, jsonify
from supabase import Client
from storage3.utils import StorageException

class FileService:
    def __init__(self, supabase_client: Client, bucket_name: str):
        self.supabase = supabase_client
        self.bucket_name = bucket_name

    def get_client_id(self):
        client_id = session.get('user_id')
        if not client_id:
            return None, jsonify({"success": False, "error": "Client not logged in"}), 401
        return client_id, None, None

    def parse_folder_path(self, folder_path):
        if isinstance(folder_path, str):
            return [f for f in folder_path.split('/') if f]
        elif isinstance(folder_path, (list, tuple)):
            return [f for f in folder_path if f and isinstance(f, str)]
        return []

    def construct_file_path(self, client_id: str, filename: str = '', folder_path=None):
        folder_path_parts = self.parse_folder_path(folder_path)
        if not (folder_path_parts[:2] == ['clients', client_id]):
            folder_path_parts = ['clients', client_id] + folder_path_parts
        if filename:
            folder_path_parts.append(filename)
        return '/'.join(folder_path_parts)

    def upload_file(self, file, folder_path=None):
        try:
            client_id, error_response, status_code = self.get_client_id()
            if error_response:
                return error_response, status_code

            if not file or file.filename == '':
                return {"error": "No file provided or selected"}, 400  # Error if no file or empty filename

            # Construct the file path and read the file content
            file_path = self.construct_file_path(client_id, file.filename, folder_path)
            file_content = file.read()

            # Determine the file content type
            file_extension = os.path.splitext(file.filename)[1].lower()
            content_type = 'application/octet-stream'
            if file_extension == '.pdf':
                content_type = 'application/pdf'
            elif file_extension in ['.jpg', '.jpeg']:
                content_type = 'image/jpeg'
            elif file_extension == '.png':
                content_type = 'image/png'
            elif file_extension == '.gif':
                content_type = 'image/gif'

            # Upload the file to Supabase storage
            try:
                file_options = {"contentType": content_type}
                self.supabase.storage.from_(self.bucket_name).upload(file_path, file_content, file_options)

                metadata = {
                    "file_name": file.filename,
                    "client_id": client_id,
                    "folder_path": self.parse_folder_path(folder_path),
                    "upload_time": datetime.datetime.now().isoformat(),
                    "content_type": content_type
                }
                return {"message": "File uploaded successfully", "path": file_path, "metadata": metadata}, 200
            except StorageException as e:
                # Handle duplicate file errors and other issues
                if isinstance(e.args[0], dict) and e.args[0].get('statusCode') == 400 and e.args[0].get('error') == 'Duplicate':
                    return self.handle_duplicate_file(client_id, file, file_content, folder_path)
                return {"error": f"Failed to upload file: {str(e)}"}, 500

        except Exception as e:
            return {"error": f"Internal server error: {str(e)}"}, 500


    def handle_duplicate_file(self, client_id, file, file_content, folder_path):
        try:
            base, ext = os.path.splitext(file.filename)
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            new_filename = f"{base}_{timestamp}{ext}"
            file_path = self.construct_file_path(client_id, new_filename, folder_path)

            self.supabase.storage.from_(self.bucket_name).upload(file_path, file_content)

            metadata = {
                "file_name": new_filename,
                "client_id": client_id,
                "folder_path": self.parse_folder_path(folder_path),
                "upload_time": datetime.datetime.now().isoformat()
            }
            return {"message": f"File uploaded successfully as {new_filename}", "path": file_path, "metadata": metadata}, 200
        except Exception as e:
            return {"error": f"Failed to upload file with unique name: {str(e)}"}, 500

    def delete_file(self, file_name: str, folder_path=None):
        try:
            client_id, error_response, status_code = self.get_client_id()
            if error_response:
                return error_response, status_code

            full_path = self.construct_file_path(client_id, file_name, folder_path)
            self.supabase.storage.from_(self.bucket_name).remove([full_path])

            return {"message": "File deleted successfully"}, 200
        except StorageException as e:
            return {"error": f"Storage error: {str(e)}"}, 500
        except Exception as e:
            return {"error": f"Internal server error: {str(e)}"}, 500

    def list_files(self, folder_path=None, recursive=False):
        try:
            client_id, error_response, status_code = self.get_client_id()
            if error_response:
                return error_response, status_code

            base_path = self.construct_file_path(client_id, '', folder_path)
            all_files_and_folders = []

            if recursive:
                self.list_files_recursive(base_path, all_files_and_folders)
            else:
                response = self.supabase.storage.from_(self.bucket_name).list(base_path)

                if isinstance(response, list):
                    for entry in response:
                        # Exclude any .keep files from the list
                        if not entry['name'].endswith('.keep'):
                            if entry.get('metadata') is None:
                                all_files_and_folders.append({
                                    "name": entry['name'],
                                    "type": "folder",
                                    "path": f"{base_path}/{entry['name']}"
                                })
                            else:
                                all_files_and_folders.append({
                                    "name": entry['name'],
                                    "type": "file",
                                    "metadata": entry['metadata'],
                                    "path": f"{base_path}/{entry['name']}"
                                })
                else:
                    if isinstance(response, dict) and response.get("error"):
                        return {"error": response["error"]}, 500

            return {"files_and_folders": all_files_and_folders}, 200

        except Exception as e:
            return {"error": f"Internal server error: {str(e)}"}, 500


    def list_files_recursive(self, path: str, accumulated_files: list):
        try:
            response = self.supabase.storage.from_(self.bucket_name).list(path)

            for entry in response:
                if entry.get('metadata') is None:
                    folder_path = f"{path}/{entry['name']}"
                    accumulated_files.append({
                        "name": entry['name'],
                        "type": "folder",
                        "path": folder_path
                    })
                    self.list_files_recursive(folder_path, accumulated_files)
                else:
                    accumulated_files.append({
                        "name": entry['name'],
                        "type": "file",
                        "metadata": entry['metadata'],
                        "path": f"{path}/{entry['name']}"
                    })
        except Exception as e:
            pass

    def get_file_metadata(self, file_name: str, folder_path: str = '', expiry_duration: int = 3600):
        try:
            client_id, error_response, status_code = self.get_client_id()
            if error_response:
                return error_response, status_code

            # Construct the full file path
            file_path = self.construct_file_path(client_id, file_name, folder_path)

            # Get the public display URL
            public_response = self.supabase.storage.from_(self.bucket_name).get_public_url(file_path)
            public_url = public_response.get('publicURL') if public_response else None

            # Get the signed download URL (expires after `expiry_duration`)
            signed_response = self.supabase.storage.from_(self.bucket_name).create_signed_url(file_path, expiry_duration)
            signed_url = signed_response.get('signedURL') if signed_response else None

            if not public_url and not signed_url:
                return {"error": "Unable to retrieve URLs for the file"}, 500

            # Return both URLs
            metadata = {
                "file_name": file_name,
                "folder_path": folder_path,
                "full_path": file_path,
                "public_url": public_url,  # Display URL
                "download_url": signed_url  # Download URL
            }
            return {"metadata": metadata}, 200

        except Exception as e:
            return {"error": f"Internal server error: {str(e)}"}, 500

    def get_download_url(self, file_name: str, folder_path: str = '', expiry_duration: int = 3600):
        try:
            client_id, error_response, status_code = self.get_client_id()
            if error_response:
                return error_response, status_code

            file_path = self.construct_file_path(client_id, file_name, folder_path)
            response = self.supabase.storage.from_(self.bucket_name).create_signed_url(file_path, expiry_duration)
            
            if not response or 'signedURL' not in response:
                return {"error": "Unable to create signed URL"}, 500

            return {"download_url": response['signedURL']}, 200
        except Exception as e:
            return {"error": f"Internal server error: {str(e)}"}, 500
        
    def create_folder(self, folder_name: str, folder_path=None):
        try:
            client_id, error_response, status_code = self.get_client_id()
            if error_response:
                return error_response, status_code

            folder_path = self.construct_file_path(client_id, '', folder_path) + f"/{folder_name}/.keep"

            self.supabase.storage.from_(self.bucket_name).upload(folder_path, b'')

            return {"message": f"Folder '{folder_name}' created successfully"}, 200
        except Exception as e:
            return {"error": f"Failed to create folder: {str(e)}"}, 500

    def delete_folder(self, folder_name: str, folder_path=None):
        try:
            client_id, error_response, status_code = self.get_client_id()
            if error_response:
                return error_response, status_code

            full_folder_path = self.construct_file_path(client_id, '', folder_path) + f"/{folder_name}"

            # List all files and folders in the folder
            all_items = self.supabase.storage.from_(self.bucket_name).list(full_folder_path)

            # If there are any files or subfolders, delete them
            if isinstance(all_items, list):
                for item in all_items:
                    item_path = f"{full_folder_path}/{item['name']}"
                    if item.get('metadata') is None:  # It's a folder
                        self.delete_folder(item['name'], full_folder_path)  # Recursive delete
                    else:  # It's a file
                        self.supabase.storage.from_(self.bucket_name).remove([item_path])

            # Finally, remove the folder itself by removing the .keep file
            self.supabase.storage.from_(self.bucket_name).remove([full_folder_path + '/.keep'])

            return {"message": "Folder and its contents deleted successfully"}, 200
        except StorageException as e:
            return {"error": f"Storage error: {str(e)}"}, 500
        except Exception as e:
            return {"error": f"Internal server error: {str(e)}"}, 500



