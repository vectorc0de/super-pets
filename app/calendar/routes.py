from flask import Blueprint, request, jsonify, Response
from app.calendar.calendar_functions import EventService
from flask_cors import CORS

event_bp = Blueprint('event_bp', __name__)
CORS(event_bp, supports_credentials=True)
event_service = EventService()

@event_bp.route('/calendar/create-event', methods=['POST'])
def create_event():
    data = request.json
    title = data.get('title')
    start = data.get('start')
    end = data.get('end')
    description = data.get('description', "")
    location = data.get('location', "")

    result = event_service.create_event(title, start, end, description, location)

    if result['success']:
        ics_content = event_service.generate_ics_file(title, start, end, description, location)
        return jsonify({"message": "Event created successfully", "event": result['event'], "ics_content": ics_content}), 201
    else:
        return jsonify(result), 500

@event_bp.route('/calendar/get-events', methods=['GET'])
def get_events():
    result = event_service.retrieve_events()
    if result['success']:
        return jsonify({"events": result['events']}), 200
    else:
        return jsonify(result), 500

@event_bp.route('/calendar/download-ics/<event_id>', methods=['GET'])
def download_ics(event_id):
    result = event_service.retrieve_event_by_id(event_id)
    if result['success']:
        event = result['event']
        ics_content = event_service.generate_ics_file(event['title'], event['start'], event['end'], event['description'], event['location'])
        response = Response(ics_content, mimetype="text/calendar")
        response.headers["Content-Disposition"] = f"attachment; filename={event['title']}.ics"
        return response
    else:
        return jsonify(result), 404

@event_bp.route('/calendar/delete-event/<event_id>', methods=['DELETE'])
def delete_event(event_id):
    result = event_service.remove_event(event_id)
    if result['success']:
        return jsonify({"message": "Event deleted successfully"}), 200
    else:
        return jsonify(result), 500

@event_bp.route('/calendar/edit-event/<event_id>', methods=['PUT'])
def edit_event(event_id):
    data = request.json
    title = data.get('title')
    start = data.get('start')
    end = data.get('end')
    description = data.get('description', "")
    location = data.get('location', "")

    result = event_service.update_event(event_id, title, start, end, description, location)

    if result['success']:
        return jsonify({"message": "Event updated successfully", "event": result['event']}), 200
    else:
        return jsonify(result), 500
