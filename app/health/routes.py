from flask import Blueprint, request
from app.health.health_service import HealthRecordService
from flask_cors import CORS

health_bp = Blueprint('health_bp', __name__)
CORS(health_bp, supports_credentials=True)

# Treatments
@health_bp.route('/health/treatment/create', methods=['POST'])
def create_treatment():
    data = request.json
    return HealthRecordService.create_record('treatments', data)

@health_bp.route('/health/treatment/list', methods=['GET'])
def list_treatments():
    return HealthRecordService.get_records('treatments')

@health_bp.route('/health/treatment/<treatment_id>', methods=['GET'])
def get_treatment_by_id(treatment_id):
    return HealthRecordService.get_record_by_id('treatments', treatment_id)

@health_bp.route('/health/treatment/update/<treatment_id>', methods=['PUT'])
def update_treatment(treatment_id):
    data = request.json
    return HealthRecordService.update_record('treatments', treatment_id, data)

@health_bp.route('/health/treatment/delete/<treatment_id>', methods=['DELETE'])
def delete_treatment(treatment_id):
    return HealthRecordService.delete_record('treatments', treatment_id)

# Vet Checks
@health_bp.route('/health/vetcheck/create', methods=['POST'])
def create_vetcheck():
    data = request.json
    return HealthRecordService.create_record('vet_checks', data)

@health_bp.route('/health/vetcheck/list', methods=['GET'])
def list_vetchecks():
    return HealthRecordService.get_records('vet_checks')

@health_bp.route('/health/vetcheck/<vetcheck_id>', methods=['GET'])
def get_vetcheck_by_id(vetcheck_id):
    return HealthRecordService.get_record_by_id('vet_checks', vetcheck_id)

@health_bp.route('/health/vetcheck/update/<vetcheck_id>', methods=['PUT'])
def update_vetcheck(vetcheck_id):
    data = request.json
    return HealthRecordService.update_record('vet_checks', vetcheck_id, data)

@health_bp.route('/health/vetcheck/delete/<vetcheck_id>', methods=['DELETE'])
def delete_vetcheck(vetcheck_id):
    return HealthRecordService.delete_record('vet_checks', vetcheck_id)

# Vaccinations
@health_bp.route('/health/vaccination/create', methods=['POST'])
def create_vaccination():
    data = request.json
    return HealthRecordService.create_record('vaccinations', data)

@health_bp.route('/health/vaccination/list', methods=['GET'])
def list_vaccinations():
    return HealthRecordService.get_records('vaccinations')

@health_bp.route('/health/vaccination/<vaccination_id>', methods=['GET'])
def get_vaccination_by_id(vaccination_id):
    return HealthRecordService.get_record_by_id('vaccinations', vaccination_id)

@health_bp.route('/health/vaccination/update/<vaccination_id>', methods=['PUT'])
def update_vaccination(vaccination_id):
    data = request.json
    return HealthRecordService.update_record('vaccinations', vaccination_id, data)

@health_bp.route('/health/vaccination/delete/<vaccination_id>', methods=['DELETE'])
def delete_vaccination(vaccination_id):
    return HealthRecordService.delete_record('vaccinations', vaccination_id)

# Procedures
@health_bp.route('/health/procedure/create', methods=['POST'])
def create_procedure():
    data = request.json
    return HealthRecordService.create_record('procedures', data)

@health_bp.route('/health/procedure/list', methods=['GET'])
def list_procedures():
    return HealthRecordService.get_records('procedures')

@health_bp.route('/health/procedure/<procedure_id>', methods=['GET'])
def get_procedure_by_id(procedure_id):
    return HealthRecordService.get_record_by_id('procedures', procedure_id)

@health_bp.route('/health/procedure/update/<procedure_id>', methods=['PUT'])
def update_procedure(procedure_id):
    data = request.json
    return HealthRecordService.update_record('procedures', procedure_id, data)

@health_bp.route('/health/procedure/delete/<procedure_id>', methods=['DELETE'])
def delete_procedure(procedure_id):
    return HealthRecordService.delete_record('procedures', procedure_id)

# Diagnostic Tests
@health_bp.route('/health/diagnostic/create', methods=['POST'])
def create_diagnostic_test():
    data = request.json
    return HealthRecordService.create_record('diagnostic_tests', data)

@health_bp.route('/health/diagnostic/list', methods=['GET'])
def list_diagnostic_tests():
    return HealthRecordService.get_records('diagnostic_tests')

@health_bp.route('/health/diagnostic/<diagnostic_id>', methods=['GET'])
def get_diagnostic_by_id(diagnostic_id):
    return HealthRecordService.get_record_by_id('diagnostic_tests', diagnostic_id)

@health_bp.route('/health/diagnostic/update/<diagnostic_id>', methods=['PUT'])
def update_diagnostic_test(diagnostic_id):
    data = request.json
    return HealthRecordService.update_record('diagnostic_tests', diagnostic_id, data)

@health_bp.route('/health/diagnostic/delete/<diagnostic_id>', methods=['DELETE'])
def delete_diagnostic_test(diagnostic_id):
    return HealthRecordService.delete_record('diagnostic_tests', diagnostic_id)
