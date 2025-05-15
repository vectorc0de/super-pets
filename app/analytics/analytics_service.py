from flask import jsonify, session, current_app
from datetime import datetime, timedelta
from typing import Tuple, Dict, Union, Optional
from collections import defaultdict
from dataclasses import dataclass

@dataclass
class TimeRange:
    start_time: datetime
    end_time: datetime

class AnalyticsService:
    TIME_FILTERS = {
        'day': lambda: timedelta(days=1),
        'week': lambda: timedelta(weeks=1),
        'month': lambda: timedelta(days=30),
        'year': lambda: timedelta(days=365),
        'all': lambda: timedelta(days=36500)
    }

    @staticmethod
    def get_client_id() -> Tuple[Optional[str], Optional[Dict], Optional[int]]:
        client_id = session.get('user_id')
        if not client_id:
            return None, {"success": False, "error": "Client not logged in"}, 401
        return client_id, None, None

    @staticmethod
    def get_time_range(time_filter: str) -> Union[TimeRange, Tuple[Dict, int]]:
        if time_filter not in AnalyticsService.TIME_FILTERS:
            return {"success": False, "error": "Invalid time filter"}, 400
        
        end_time = datetime.utcnow()
        delta = AnalyticsService.TIME_FILTERS[time_filter]()
        start_time = end_time - delta
        
        if time_filter == 'all':
            start_time = datetime(2020, 1, 1)
        
        return TimeRange(start_time, end_time)

    @staticmethod
    def get_previous_time_range(time_filter: str) -> Union[TimeRange, Tuple[Dict, int]]:
        if time_filter not in AnalyticsService.TIME_FILTERS:
            return {"success": False, "error": "Invalid time filter"}, 400
        
        end_time = datetime.utcnow()
        delta = AnalyticsService.TIME_FILTERS[time_filter]()
        start_time = end_time - delta
        prev_end_time = start_time
        prev_start_time = prev_end_time - delta
        
        return TimeRange(prev_start_time, prev_end_time)

    @staticmethod
    def calculate_change(current_total: int, previous_total: int) -> Tuple[str, str, str]:
        if previous_total == 0:
            change_percentage = "+100%" if current_total > 0 else "0%"
            change_value = str(current_total)
            change_type = "increase" if current_total > 0 else "no change"
        else:
            change_value = current_total - previous_total
            change_percentage = f"{((change_value / previous_total) * 100):.2f}%"
            change_type = "increase" if change_value >= 0 else "decrease"
        
        return str(change_value), change_percentage, change_type

    @staticmethod
    def get_interval_key(time_filter, date):
        if time_filter == 'day':
            return date.strftime("%Y-%m-%d")
        elif time_filter == 'week':
            return date.strftime("%Y-%W")
        elif time_filter == 'month':
            return date.strftime("%Y-%m")
        elif time_filter == 'year':
            return date.strftime("%Y")
        return date.strftime("%Y-%m-%d")

    @staticmethod
    def group_by_time_interval(data, time_filter, time_range) -> Dict:
        interval_data = defaultdict(int)
        current_time = time_range.start_time
        
        while current_time <= time_range.end_time:
            date_key = current_time.strftime("%Y-%m-%d")
            interval_data[date_key] = 0
            current_time += timedelta(days=1)
        
        for record in data:
            created_at = datetime.fromisoformat(record['created_at']).strftime("%Y-%m-%d")
            if created_at in interval_data:
                interval_data[created_at] += 1
        
        return [{"date": date, "count": count} for date, count in interval_data.items()]
    
    @classmethod
    def fetch_data_by_time(cls, table: str, time_filter: str) -> Tuple[Dict, int]:
        client_id, error_response, status_code = cls.get_client_id()
        if error_response:
            return error_response, status_code

        current_range = cls.get_time_range(time_filter)
        if isinstance(current_range, tuple):
            return current_range

        previous_range = cls.get_previous_time_range(time_filter)
        if isinstance(previous_range, tuple):
            return previous_range

        try:
            current_query = current_app.supabase.table(table) \
                .select('*') \
                .eq('client_id', client_id) \
                .gte('created_at', current_range.start_time.isoformat()) \
                .lte('created_at', current_range.end_time.isoformat()) \
                .execute()

            current_total = len(current_query.data)

            previous_query = current_app.supabase.table(table) \
                .select('*') \
                .eq('client_id', client_id) \
                .gte('created_at', previous_range.start_time.isoformat()) \
                .lte('created_at', previous_range.end_time.isoformat()) \
                .execute()

            previous_total = len(previous_query.data)

            change_value, change_percentage, change_type = cls.calculate_change(current_total, previous_total)

            time_series_data = cls.group_by_time_interval(current_query.data, time_filter, current_range)

            return {
                "success": True,
                "total_count": current_total,
                "change_value": change_value,
                "change_percentage": change_percentage,
                "change_type": change_type,
                "time_series": time_series_data,
                "debug_info": {
                    "table": table,
                    "time_filter": time_filter,
                    "current_start_time": current_range.start_time.isoformat(),
                    "current_end_time": current_range.end_time.isoformat(),
                    "previous_start_time": previous_range.start_time.isoformat(),
                    "previous_end_time": previous_range.end_time.isoformat(),
                }
            }, 200
        except Exception as e:
            return {"success": False, "error": f"An error occurred: {str(e)}"}, 500

    @classmethod
    def get_pets_by_time(cls, time_filter: str) -> Tuple[Dict, int]:
        return cls.fetch_data_by_time('pets', time_filter)

    @classmethod
    def get_people_by_time(cls, time_filter: str) -> Tuple[Dict, int]:
        return cls.fetch_data_by_time('people', time_filter)

    @classmethod
    def get_donations_by_time(cls, time_filter: str) -> Tuple[Dict, int]:
        return cls.fetch_data_by_time('donations', time_filter)

    @classmethod
    def get_partners_by_time(cls, time_filter: str) -> Tuple[Dict, int]:
        return cls.fetch_data_by_time('partners', time_filter)

    @classmethod
    def get_all_data(cls, time_filter: str = 'all') -> Tuple[Dict, int]:
        try:
            pets_data, _ = cls.get_pets_by_time(time_filter)
            people_data, _ = cls.get_people_by_time(time_filter)
            donations_data, _ = cls.get_donations_by_time(time_filter)
            partners_data, _ = cls.get_partners_by_time(time_filter)

            return {
                "success": True,
                "pets": pets_data,
                "people": people_data,
                "donations": donations_data,
                "partners": partners_data
            }, 200
        except Exception as e:
            return {"success": False, "error": f"An error occurred: {str(e)}"}, 500
