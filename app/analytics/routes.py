from flask import Blueprint
from app.analytics.analytics_service import AnalyticsService
from flask_cors import CORS

analytics_bp = Blueprint('analytics_bp', __name__)
CORS(analytics_bp, supports_credentials=True)

@analytics_bp.route('/analytics/donations/<time_filter>', methods=['GET'])
def get_donations_analytics(time_filter):
    return AnalyticsService.get_donations_by_time(time_filter)

@analytics_bp.route('/analytics/pets/<time_filter>', methods=['GET'])
def get_pets_analytics(time_filter):
    return AnalyticsService.get_pets_by_time(time_filter)

@analytics_bp.route('/analytics/people/<time_filter>', methods=['GET'])
def get_people_analytics(time_filter):
    return AnalyticsService.get_people_by_time(time_filter)

@analytics_bp.route('/analytics/partners/<time_filter>', methods=['GET'])
def get_partners_analytics(time_filter):
    return AnalyticsService.get_partners_by_time(time_filter)

@analytics_bp.route('/analytics/all/<time_filter>', methods=['GET'])
def get_all_analytics(time_filter):
    return AnalyticsService.get_all_data(time_filter)
