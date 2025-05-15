from flask import Blueprint, request, jsonify, render_template
from app.donations.donation_service import (
    process_credit_donation,
    process_cash_donation,
    get_donation_analytics,
    delete_donation,
    update_donation,
    create_invoice,
    get_all_donations,
    process_credit_donation_auto,
    get_donation_info
)
from flask_cors import CORS

donation_bp = Blueprint('donation_bp', __name__)
CORS(donation_bp, supports_credentials=True)

@donation_bp.route('/donate/credit', methods=['POST'])
def credit_donation():
    data = request.json
    if not data or 'donation_id' not in data or 'payment_method_id' not in data:
        return jsonify({'success': False, 'message': 'Required fields are missing: donation_id, payment_method_id'}), 400

    donation_id = data['donation_id']
    payment_method_id = data['payment_method_id']
    return process_credit_donation(donation_id, payment_method_id)

@donation_bp.route('/donate/cash', methods=['POST'])
def cash_donation():
    data = request.json
    if not data or 'person_id' not in data or 'amount' not in data or 'title' not in data or 'description' not in data:
        return jsonify({'success': False, 'message': 'Required fields are missing: person_id, amount, title, description'}), 400

    return process_cash_donation(data)

@donation_bp.route('/donation/<uuid:donation_id>', methods=['DELETE'])
def delete_donation_route(donation_id):
    return delete_donation(donation_id)

@donation_bp.route('/donation/<uuid:donation_id>', methods=['PUT'])
def update_donation_route(donation_id):
    data = request.json
    if not data:
        return jsonify({'success': False, 'message': 'No data provided for update'}), 400
    return update_donation(donation_id, data)

@donation_bp.route('/donations/analytics', methods=['GET'])
def get_donation_analytics_route():
    return get_donation_analytics()

@donation_bp.route('/create_invoice', methods=['POST'])
def create_invoice_route():
    data = request.json
    if not data or 'customer_id' not in data or 'amount' not in data or 'title' not in data or 'description' not in data:
        return jsonify({'success': False, 'message': 'Required fields are missing: customer_id, amount, title, description'}), 400

    return create_invoice(data)

@donation_bp.route('/donate/credit/auto', methods=['POST'])
def credit_donation_auto():
    data = request.json
    if not data or 'amount' not in data or 'payment_method_id' not in data or 'email' not in data:
        return jsonify({'success': False, 'message': 'Required fields are missing: amount, payment_method_id, email'}), 400

    return process_credit_donation_auto(data)

@donation_bp.route('/donations', methods=['GET'])
def get_all_donations_route():
    return get_all_donations()

@donation_bp.route('/donation/<uuid:donation_id>', methods=['GET'])
def get_donation_info_route(donation_id):
    return get_donation_info(donation_id)