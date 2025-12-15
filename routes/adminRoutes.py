from flask import Blueprint
from utils.auth import role_required, jwt_required_custom
from controllers.adminKkController import (
    get_all_kartu_keluarga_admin_controller,
    get_kartu_keluarga_detail_admin_controller,
    update_kartu_keluarga_status_controller,
    update_human_capital_status_controller,
    delete_kartu_keluarga_controller,
)
from controllers.adminKtpController import (
    get_all_ktp_admin_controller,
    get_ktp_detail_admin_controller,
    update_ktp_status_controller,
    delete_ktp_controller,
)
from controllers.adminAsetNonfinansialController import (
    list_asets,
    get_aset_by_nik,
    update_aset_admin,
    delete_aset_admin,
)
from controllers.adminKondisiEkonomiController import (
    list_kondisi_admin,
    get_kondisi_admin,
    update_kondisi_admin,
    delete_kondisi_admin,
)
from controllers.adminPetugasController import create_petugas_controller

admin_bp = Blueprint('admin', __name__)

# KK routes
@jwt_required_custom()
@admin_bp.route('/kk', methods=['GET'])
def admin_list_kk():
    return get_all_kartu_keluarga_admin_controller()

@jwt_required_custom()
@admin_bp.route('/kk/<int:nik>', methods=['GET'])
def admin_get_kk(nik):
    return get_kartu_keluarga_detail_admin_controller(nik)

@jwt_required_custom()
@role_required('petugas')
@admin_bp.route('/kk/<int:nik>', methods=['PUT'])
def admin_update_kk_status(nik):
    return update_kartu_keluarga_status_controller(nik)

@jwt_required_custom()
@admin_bp.route('/kk/<int:nik>', methods=['DELETE'])
def admin_delete_kk(nik):
    return delete_kartu_keluarga_controller(nik)

@jwt_required_custom()
@role_required('petugas')
@admin_bp.route('/kk/<int:nik>/human-capital', methods=['PUT'])
def admin_update_hc_status(nik):
    return update_human_capital_status_controller(nik)

# KTP routes
@jwt_required_custom()
@admin_bp.route('/ktp', methods=['GET'])
def admin_list_ktp():
    return get_all_ktp_admin_controller()

@jwt_required_custom()
@admin_bp.route('/ktp/<int:nik>', methods=['GET'])
def admin_get_ktp(nik):
    return get_ktp_detail_admin_controller(nik)

@jwt_required_custom()
@role_required('petugas')
@admin_bp.route('/ktp/<int:nik>', methods=['PUT'])
def admin_update_ktp_status(nik):
    return update_ktp_status_controller(nik)

@jwt_required_custom()
@admin_bp.route('/ktp/<int:nik>', methods=['DELETE'])
def admin_delete_ktp(nik):
    return delete_ktp_controller(nik)


# Aset Non-Finansial routes
@jwt_required_custom()
@admin_bp.route('/asetNonFinansial', methods=['GET'])
def admin_list_aset():
    from flask import request
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 100))
    return list_asets(page=page, per_page=per_page)


@jwt_required_custom()
@admin_bp.route('/asetNonFinansial/<int:nik>', methods=['GET'])
def admin_get_aset(nik: int):
    return get_aset_by_nik(nik)


@jwt_required_custom()
@role_required('petugas')
@admin_bp.route('/asetNonFinansial/<int:nik>/status', methods=['PUT', 'PATCH'])
def admin_update_aset_status(nik: int):
    from flask import request
    payload = request.get_json() or request.form.to_dict()
    return update_aset_admin(nik, payload)


@jwt_required_custom()
@admin_bp.route('/asetNonFinansial/<int:nik>', methods=['DELETE'])
def admin_delete_aset(nik: int):
    return delete_aset_admin(nik)


# Kondisi Ekonomi / Rumah (admin)
@jwt_required_custom()
@admin_bp.route('/kondisiEkonomi', methods=['GET'])
def admin_list_kondisi():
    from flask import request
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 100))
    return list_kondisi_admin(page=page, per_page=per_page)


@jwt_required_custom()
@admin_bp.route('/kondisiEkonomi/<int:nik>', methods=['GET'])
def admin_get_kondisi(nik: int):
    return get_kondisi_admin(nik)


@jwt_required_custom()
@role_required('petugas')
@admin_bp.route('/kondisiEkonomi/<int:nik>', methods=['PUT'])
def admin_update_kondisi(nik: int):
    from flask import request
    # pass form and files to controller; controller will return jsonify tuple
    form = request.form.to_dict()
    files = request.files
    return update_kondisi_admin(nik, form, files)

@jwt_required_custom()
@admin_bp.route('/kondisiEkonomi/<int:nik>', methods=['DELETE'])
def admin_delete_kondisi(nik: int):
    return delete_kondisi_admin(nik)
# TODO: add jwt_required 
# add logika admin create akun petugas (confirm status)


@jwt_required_custom()
@admin_bp.route('/petugas', methods=['POST'])
def admin_create_petugas():
    from flask import request
    payload = request.get_json() or request.form.to_dict()
    return create_petugas_controller(payload)
