import csv
import io
import openai
from flask import jsonify, current_app, session
from app.models.pet_model import PetModel
from app.models.people_model import PeopleModel

EXPECTED_PET_COLUMNS = ['created_at', 'pet_name', 'pet_id', 'pet_breed', 'pet_sex', 'pet_photo',
                        'pet_color', 'pet_owner_id', 'pet_background', 'pet_type', 'pet_status']

EXPECTED_PEOPLE_COLUMNS = ['created_at', 'person_first_name', 'person_last_name',
                           'person_email', 'person_phone', 'person_address', 'person_zipcode',
                           'person_state', 'person_city', 'person_age', 'person_gender']

def read_csv(file):
    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
    reader = csv.DictReader(stream)
    return list(reader), reader.fieldnames

def format_data_with_chatgpt(rows, expected_columns):
    prompt = (
        f"Given the following data, format it to match the expected structure: "
        f"{expected_columns}. Here is the data:\n\n" +
        "\n".join(str(row) for row in rows) +
        "\nFormat the data in CSV format with the correct headers."
    )

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that formats data."},
            {"role": "user", "content": prompt}
        ]
    )

    formatted_text = response['choices'][0]['message']['content']
    formatted_stream = io.StringIO(formatted_text)
    reader = csv.DictReader(formatted_stream)
    return list(reader)

def normalize_sex(sex):
    normalized = sex.lower()
    if normalized in ['female', 'f']:
        return 'Female'
    elif normalized in ['male', 'm']:
        return 'Male'
    return None

def normalize_gender(gender):
    normalized = gender.lower()
    if normalized in ['female', 'f']:
        return 'Female'
    elif normalized in ['male', 'm']:
        return 'Male'
    return None

def handle_missing_data_pet(row):
    row['pet_sex'] = normalize_sex(row.get('pet_sex', ''))
    return {col: row.get(col, None) for col in EXPECTED_PET_COLUMNS}

def handle_missing_data_person(row):
    row['person_gender'] = normalize_gender(row.get('person_gender', ''))
    return {col: row.get(col, None) for col in EXPECTED_PEOPLE_COLUMNS}

def process_pets_csv_with_ai(file):
    try:
        client_id = session.get('user_id')
        rows, _ = read_csv(file)
        formatted_data = format_data_with_chatgpt(rows, EXPECTED_PET_COLUMNS)
        added_pets = []

        for row in formatted_data:
            row = handle_missing_data_pet(row)
            pet_model = PetModel(current_app.supabase)
            add_pet_result = pet_model.add_pet(
                owner_id=None,
                pet_name=row['pet_name'],
                breed=row['pet_breed'],
                pet_type=row['pet_type'],
                sex=row['pet_sex'],
                color=row['pet_color'],
                background=row['pet_background'],
                status=row['pet_status'],
                photo_file=row['pet_photo'],
                client_id=client_id
            )
            added_pets.append(add_pet_result)

        return jsonify({"success": True, "message": "File processed and pets added successfully.", "added_pets": added_pets}), 200

    except Exception as e:
        return jsonify({"success": False, "error": f"An error occurred while processing the file: {str(e)}"}), 500

def process_people_csv_with_ai(file):
    try:
        client_id = session.get('user_id')
        if not client_id:
            return jsonify({"success": False, "error": "Client not logged in"}), 401

        rows, _ = read_csv(file)
        formatted_data = format_data_with_chatgpt(rows, EXPECTED_PEOPLE_COLUMNS)
        added_people = []

        for row in formatted_data:
            row = handle_missing_data_person(row)
            people_model = PeopleModel(current_app.supabase)
            add_person_result = people_model.create_person(
                first_name=row['person_first_name'],
                last_name=row['person_last_name'],
                email=row['person_email'],
                phone=row['person_phone'],
                address=row['person_address'],
                zipcode=row['person_zipcode'],
                state=row['person_state'],
                city=row['person_city'],
                gender=row['person_gender'],
                age=row['person_age'],
                client_id=client_id
            )
            added_people.append(add_person_result)

        return jsonify({"success": True, "message": "File processed and people added successfully.", "added_people": added_people}), 200

    except Exception as e:
        return jsonify({"success": False, "error": f"An error occurred while processing the file: {str(e)}"}), 500
