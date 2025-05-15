from flask import Blueprint, jsonify, request, session
from app.auth.auth_service import AuthService
from flask_cors import CORS

auth_bp = Blueprint('auth_bp', __name__)
CORS(auth_bp, supports_credentials=True)
auth_service = AuthService()

def create_user_response(user_data, message):
    return {
        'message': message,
        'user_id': user_data.get('user_id', session.get('user_id')),
        'user_email': user_data.get('user_email', session.get('user_email')),
        'first_name': user_data.get('first_name', session.get('first_name')),
        'last_name': user_data.get('last_name', session.get('last_name')),
        'profile_pic': user_data.get('profile_pic', session.get('profile_pic', ''))
    }

@auth_bp.route('/auth/signup', methods=['POST'])
def signup():
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        profile_pic_file = request.files.get('profile_pic')

        if not all([email, password, first_name, last_name]):
            return jsonify({'error': 'Missing required fields'}), 400

        result = auth_service.signup(email, password, first_name, last_name, profile_pic_file)

        if result['success']:
            response_data = create_user_response(
                {'user_id': result['user'].id, 'user_email': result['user'].email},
                'Account created successfully'
            )
            return jsonify(response_data), 201
        
        return jsonify({'error': result['error']}), result.get('status', 400)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not all([email, password]):
            return jsonify({'error': 'Missing email or password'}), 400

        result = auth_service.login(email, password)

        if result['success']:
            response_data = create_user_response({}, 'Login successful')
            return jsonify(response_data), 200
        
        return jsonify({'error': result['error']}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/auth/logout', methods=['POST'])
def logout():
    try:
        result = auth_service.logout()

        if result['success']:
            return jsonify({'message': 'Logged out successfully'}), 200
        
        return jsonify({'error': result['error']}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/auth/change-email', methods=['POST'])
def change_user_email():
    try:
        data = request.get_json()
        new_email = data.get('new_email')

        if not new_email:
            return jsonify({'error': 'New email is required'}), 400

        result = auth_service.change_email(new_email)

        if result['success']:
            return jsonify({'message': 'Email updated successfully'}), 200
        
        return jsonify({'error': result['error']}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/auth/change-password', methods=['POST'])
def change_user_password():
    try:
        data = request.get_json()
        old_password = data.get('old_password')
        new_password = data.get('new_password')

        if not all([old_password, new_password]):
            return jsonify({'error': 'Both old and new passwords are required'}), 400

        result = auth_service.change_password(old_password, new_password)

        if result['success']:
            return jsonify({'message': 'Password updated successfully'}), 200
        
        return jsonify({'error': result['error']}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/auth/edit-profile', methods=['PUT'])
def edit_profile():
    try:
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        profile_pic_file = request.files.get('profile_pic')

        if not all([first_name, last_name]):
            return jsonify({'error': 'First name and last name are required'}), 400

        result = auth_service.edit_profile(first_name, last_name, profile_pic_file)

        if result['success']:
            return jsonify(result['user']), 200
        
        return jsonify({'error': result['error']}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
