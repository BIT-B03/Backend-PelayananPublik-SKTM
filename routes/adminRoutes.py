from flask import Blueprint
from utils.auth import role_required
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

admin_bp = Blueprint('admin', __name__)

# KK routes
@admin_bp.route('/kk', methods=['GET'])
def admin_list_kk():
    return get_all_kartu_keluarga_admin_controller()

@admin_bp.route('/kk/<int:nik>', methods=['GET'])
def admin_get_kk(nik):
    return get_kartu_keluarga_detail_admin_controller(nik)

@admin_bp.route('/kk/<int:nik>', methods=['PUT'])
def admin_update_kk_status(nik):
    return update_kartu_keluarga_status_controller(nik)

@admin_bp.route('/kk/<int:nik>', methods=['DELETE'])
def admin_delete_kk(nik):
    return delete_kartu_keluarga_controller(nik)

@admin_bp.route('/kk/<int:nik>/human-capital', methods=['PUT'])
def admin_update_hc_status(nik):
    return update_human_capital_status_controller(nik)

# KTP routes
@admin_bp.route('/ktp', methods=['GET'])
def admin_list_ktp():
    return get_all_ktp_admin_controller()

@admin_bp.route('/ktp/<int:nik>', methods=['GET'])
def admin_get_ktp(nik):
    return get_ktp_detail_admin_controller(nik)

@admin_bp.route('/ktp/<int:nik>', methods=['PUT'])
def admin_update_ktp_status(nik):
    return update_ktp_status_controller(nik)

@admin_bp.route('/ktp/<int:nik>', methods=['DELETE'])
def admin_delete_ktp(nik):
    return delete_ktp_controller(nik)