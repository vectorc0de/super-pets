from flask import current_app, session
from ics import Calendar, Event
import uuid

class EventService:
    def create_event(self, title, start, end, description="", location=""):
        try:
            client_id = session.get('user_id')
            if not client_id:
                return {"success": False, "error": "User not logged in"}

            event_id = str(uuid.uuid4())

            event_data = {
                "id": event_id,
                "title": title,
                "start": start,
                "end": end,
                "description": description,
                "location": location,
                "client_id": client_id
            }
            
            response = current_app.supabase.table("events").insert(event_data).execute()
            if response.data:
                return {"success": True, "event": response.data[0]}
            else:
                return {"success": False, "error": "Failed to create event"}
        except Exception as e:
            return {"success": False, "error": f"An error occurred: {str(e)}"}

    def retrieve_events(self):
        try:
            client_id = session.get('user_id')
            if not client_id:
                return {"success": False, "error": "User not logged in"}

            response = current_app.supabase.table("events").select("*").eq("client_id", client_id).execute()
            if response.data:
                return {"success": True, "events": response.data}
            else:
                return {"success": False, "error": "No events found"}
        except Exception as e:
            return {"success": False, "error": f"An error occurred: {str(e)}"}

    def retrieve_event_by_id(self, event_id):
        try:
            client_id = session.get('user_id')
            if not client_id:
                return {"success": False, "error": "User not logged in"}

            response = current_app.supabase.table("events").select("*").eq("id", event_id).eq("client_id", client_id).execute()
            if response.data:
                return {"success": True, "event": response.data[0]}
            else:
                return {"success": False, "error": "Event not found"}
        except Exception as e:
            return {"success": False, "error": f"An error occurred: {str(e)}"}

    def remove_event(self, event_id):
        try:
            client_id = session.get('user_id')
            if not client_id:
                return {"success": False, "error": "User not logged in"}

            response = current_app.supabase.table("events").delete().eq("id", event_id).eq("client_id", client_id).execute()
            if response.data:
                return {"success": True, "message": "Event deleted successfully"}
            else:
                return {"success": False, "error": "Failed to delete event"}
        except Exception as e:
            return {"success": False, "error": f"An error occurred: {str(e)}"}

    def generate_ics_file(self, title, start, end, description="", location=""):
        calendar = Calendar()
        event = Event(
            name=title,
            begin=start,
            end=end,
            description=description,
            location=location
        )
        calendar.events.add(event)
        return str(calendar)

    def update_event(self, event_id, title, start, end, description="", location=""):
        try:
            client_id = session.get('user_id')
            if not client_id:
                return {"success": False, "error": "User not logged in"}

            event_data = {
                "title": title,
                "start": start,
                "end": end,
                "description": description,
                "location": location
            }

            response = current_app.supabase.table("events").update(event_data).eq("id", event_id).eq("client_id", client_id).execute()
            if response.data:
                return {"success": True, "event": response.data[0]}
            else:
                return {"success": False, "error": "Failed to update event"}
        except Exception as e:
            return {"success": False, "error": f"An error occurred: {str(e)}"}
