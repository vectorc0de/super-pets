from flask import Blueprint, request
from app.partners.partner_service import PartnerService
from flask_cors import CORS

partners_bp = Blueprint('partners_bp', __name__)
CORS(partners_bp, supports_credentials=True)


@partners_bp.route('/partners/create', methods=['POST'])
def create_partner():
    data = request.json
    return PartnerService.create_partner(data)

@partners_bp.route('/partners/list', methods=['GET'])
def list_partners():
    return PartnerService.get_all_partners()

@partners_bp.route('/partners/<partner_id>', methods=['GET'])
def get_partner_by_id(partner_id):
    return PartnerService.get_partner_by_id(partner_id)

@partners_bp.route('/partners/update/<partner_id>', methods=['PUT'])
def update_partner(partner_id):
    data = request.json
    return PartnerService.update_partner(partner_id, data)

@partners_bp.route('/partners/delete/<partner_id>', methods=['DELETE'])
def delete_partner(partner_id):
    return PartnerService.delete_partner(partner_id)
