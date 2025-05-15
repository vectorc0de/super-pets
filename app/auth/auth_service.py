from flask import current_app, session

class AuthService:
    def signup(self, email, password, first_name, last_name, profile_pic_file=None):
        try:
            user_metadata = {
                'first_name': first_name,
                'last_name': last_name
            }
            
            user = current_app.supabase.auth.sign_up({
                'email': email,
                'password': password,
                'data': user_metadata
            })

            if user.user:
                if profile_pic_file:
                    try:
                        bucket_name = 'profile-pictures'
                        file_name = f"profile_pic_{user.user.id}.jpg"
                        file_content = profile_pic_file.read()
                        
                        current_app.supabase.storage.from_(bucket_name).upload(file_name, file_content)
                        profile_pic_url = current_app.supabase.storage.from_(bucket_name).get_public_url(file_name)
                        user_metadata['profile_pic'] = profile_pic_url
                        
                        current_app.supabase.auth.update_user({
                            'data': user_metadata
                        })
                    except Exception as upload_error:
                        return {
                            "success": True,
                            "user": user.user,
                            "warning": f"Profile picture upload failed: {str(upload_error)}"
                        }

                return {"success": True, "user": user.user}
            return {"success": False, "error": "Failed to create account"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def login(self, email, password):
        try:
            user = current_app.supabase.auth.sign_in_with_password({
                'email': email,
                'password': password
            })

            if user.user:
                first_name = user.user.user_metadata.get('first_name', 'N/A')
                last_name = user.user.user_metadata.get('last_name', 'N/A')
                profile_pic = user.user.user_metadata.get('profile_pic', '')

                session['user_id'] = user.user.id
                session['user_email'] = user.user.email
                session['first_name'] = first_name
                session['last_name'] = last_name
                session['profile_pic'] = profile_pic

                return {
                    "success": True,
                    "user": {
                        "id": user.user.id,
                        "email": user.user.email,
                        "first_name": first_name,
                        "last_name": last_name,
                        "profile_pic": profile_pic
                    }
                }
            return {"success": False, "error": "Invalid login credentials"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def logout(self):
        if 'user_id' in session:
            session.clear()
            return {"success": True}
        return {"success": False, "error": "No active session found"}

    def change_email(self, new_email):
        try:
            user_id = session.get('user_id')
            if not user_id:
                return {"success": False, "error": "User not logged in"}

            user = current_app.supabase.auth.update_user({
                'email': new_email
            })

            if user.user:
                session['user_email'] = new_email
                return {"success": True}
            return {"success": False, "error": "Failed to update email"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def change_password(self, old_password, new_password):
        try:
            user_email = session.get('user_email')
            if not user_email:
                return {"success": False, "error": "User not logged in"}
            
            user = current_app.supabase.auth.sign_in_with_password({
                'email': user_email, 
                'password': old_password
            })
            
            if user.user:
                update_response = current_app.supabase.auth.update_user({
                    'password': new_password
                })
                if update_response.user:
                    return {"success": True}
            return {"success": False, "error": "Failed to update password"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def edit_profile(self, first_name, last_name, profile_pic_file=None):
        try:
            user_id = session.get('user_id')
            if not user_id:
                return {"success": False, "error": "User not logged in"}

            metadata_update = {
                'first_name': first_name,
                'last_name': last_name
            }

            profile_pic_url = None
            if profile_pic_file:
                try:
                    bucket_name = 'profile-pictures'
                    file_name = f"profile_pic_{user_id}.jpg"
                    file_content = profile_pic_file.read()
                    
                    try:
                        current_app.supabase.storage.from_(bucket_name).remove([file_name])
                    except Exception:
                        pass
                    
                    current_app.supabase.storage.from_(bucket_name).upload(file_name, file_content)
                    profile_pic_url = current_app.supabase.storage.from_(bucket_name).get_public_url(file_name)
                    metadata_update['profile_pic'] = profile_pic_url
                except Exception as upload_error:
                    return {"success": False, "error": f"Profile picture upload failed: {str(upload_error)}"}

            update_response = current_app.supabase.auth.update_user({
                'data': metadata_update
            })

            if update_response.user:
                session['first_name'] = first_name
                session['last_name'] = last_name
                if profile_pic_url:
                    session['profile_pic'] = profile_pic_url

                return {
                    "success": True, 
                    "user": {
                        "user_id": user_id,
                        "user_email": session.get('user_email'),
                        "first_name": first_name,
                        "last_name": last_name,
                        "profile_pic": profile_pic_url or session.get('profile_pic', ''),
                        "message": "Profile updated successfully"
                    }
                }
            return {"success": False, "error": "Failed to update profile"}
        except Exception as e:
            return {"success": False, "error": str(e)}
