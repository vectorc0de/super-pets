import os
import json
import uuid
import PyPDF2
import openai
from dotenv import load_dotenv
from supabase import create_client
from langchain.utilities import SQLDatabase
from langchain_community.chat_models import ChatOpenAI
from langchain_experimental.sql import SQLDatabaseChain
from flask import session, current_app

class HealthRecordProcessor:
    TABLE_MAP = {
        'vet_checks': ['id', 'pet_id', 'vet_name', 'checkup_date', 'notes', 'follow_up_needed',
                       'next_checkup_date', 'vet_contact', 'client_id'],
        'vaccinations': ['id', 'pet_id', 'vaccine_name', 'date_administered', 'next_due_date', 'notes', 'client_id'],
        'treatments': ['id', 'pet_id', 'treatment_type', 'treatment_description', 'start_time', 'end_time',
                       'frequency', 'route', 'dose', 'status', 'location', 'client_id'],
        'procedures': ['id', 'pet_id', 'procedure_type', 'procedure_date', 'surgeon', 'notes', 'outcome', 'client_id'],
        'diagnostic_tests': ['id', 'pet_id', 'test_type', 'test_date', 'results', 'vet_notes', 'client_id']
    }

    def __init__(self):
        load_dotenv()
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        self.DB_URI = os.getenv('DB_URI')
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        self.llm = ChatOpenAI(temperature=0, openai_api_key=self.OPENAI_API_KEY)
        self.db = SQLDatabase.from_uri(self.DB_URI, include_tables=[
            'pets', 'people', 'events'], # 'treatments', 'vaccinations', 'vet_checks', 'procedures', 'diagnostic_tests'
            sample_rows_in_table_info=2
        )
        self.db_chain = SQLDatabaseChain.from_llm(self.llm, self.db, verbose=True)

    def extract_text_from_pdf(self, pdf_file):
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {e}")

    def generate_uuid(self):
        return str(uuid.uuid4())

    def use_gpt_for_mapping(self, text, enhanced_context=""):
        context_prompt = f"\nAdditional context about the pet:\n{enhanced_context}" if enhanced_context else ""

        prompt = (
            f"id should all be random uuids\n\n"
            f"Given the following medical data extracted from a pet's health records, "
            f"classify the data into the appropriate categories.{context_prompt}\n\n"
            f"Here is the extracted data:\n\n{text}\n\n"
            f"Please only return relevant fields that map to these headers:\n"
            f"{self.TABLE_MAP}\n"
            f"Return the result in valid JSON format, without any extra text."
        )

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a data classification assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        dump = json.loads(response.model_dump_json(indent=2))

        print(dump)

        formatted_text = dump['choices'][0]['message']['content']
        if not formatted_text.strip():
            raise Exception("GPT-3 returned an empty response. Unable to process the data.")

        try:
            classified_data = json.loads(formatted_text)
        except json.JSONDecodeError as e:
            raise Exception(f"Error parsing GPT response: {e}")

        return classified_data

    def get_enhanced_context(self, pet_id):
        """Retrieve additional information about the pet."""
        query = f"Get all relevant information about the pet with ID {pet_id}, including owner details, recent events"
        try:
            db_context = self.db_chain(query)
            return db_context['result'].strip()
        except Exception as e:
            current_app.logger.error(f"Error retrieving from database: {e}")
            return ""

    def fill_missing_columns(self, data, expected_columns, table_name, client_id, pet_id):
        filled_data = {}
        for column in expected_columns:
            if column == 'pet_id':
                filled_data[column] = pet_id
            elif column == 'client_id':
                filled_data[column] = client_id
            elif column in ['vaccination_id', 'treatment_id', 'procedure_id', 'diagnostic_test_id']:
                filled_data[column] = self.generate_uuid()
            else:
                filled_data[column] = data.get(column, None)
        return filled_data

    def insert_data_into_supabase(self, table_name, data):
        try:
            response = current_app.supabase.table(table_name).insert(data).execute()
            return response.data
        except Exception as e:
            raise Exception(f"Failed to insert data into {table_name}: {e}")


def analyze_pdf_and_classify(file, pet_id):
    processor = HealthRecordProcessor()
    client_id = session.get('user_id')
    extracted_text = processor.extract_text_from_pdf(file)
    enhanced_context = processor.get_enhanced_context(pet_id)
    classified_data = processor.use_gpt_for_mapping(extracted_text, enhanced_context)
    
    for table, records in classified_data.items():
        for record in records:
            record['client_id'] = client_id
            record['pet_id'] = pet_id
    return classified_data


def insert_data_to_supabase(table_name, data):
    processor = HealthRecordProcessor()
    return processor.insert_data_into_supabase(table_name, data)
