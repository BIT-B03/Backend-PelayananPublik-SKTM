from flask import Blueprint
from utils.auth import jwt_required_custom
from controllers.userKkController import (
    create_kartu_keluarga_controller,
    get_kartu_keluarga_detail_controller,
    update_kartu_keluarga_controller,
)
from controllers.userKtpController import (
    create_ktp_controller,
    get_ktp_detail_controller,
    update_ktp_controller,
)
from controllers.userKondisiEkonomiController import (
    create_user_kondisi_controller,
    get_user_kondisi_controller,
    update_user_kondisi_controller,
)
from controllers.userasetNonfinansialController import (
    create_user_aset,
    get_user_aset,
    update_user_aset,
)

user_bp = Blueprint('user', __name__)

# --- Kartu Keluarga (KK) routes ---
@user_bp.route('/kk/<int:nik>', methods=['GET'])
@jwt_required_custom
def get_kartu_keluarga(nik: int):
    return get_kartu_keluarga_detail_controller(nik)

@user_bp.route('/kk', methods=['POST'])
@jwt_required_custom
def create_kartu_keluarga():
    return create_kartu_keluarga_controller()

@user_bp.route('/kk/<int:nik>', methods=['PUT'])
@jwt_required_custom
def update_kartu_keluarga(nik: int):
    return update_kartu_keluarga_controller(nik)

# --- KTP routes ---
@user_bp.route('/ktp/<int:nik>', methods=['GET'])
@jwt_required_custom
def get_ktp(nik: int):
    return get_ktp_detail_controller(nik)

@user_bp.route('/ktp', methods=['POST'])
@jwt_required_custom
def create_ktp():
    return create_ktp_controller()

@user_bp.route('/ktp/<int:nik>', methods=['PUT'])
@jwt_required_custom
def update_ktp(nik: int):
    return update_ktp_controller(nik)

# --- Kondisi Ekonomi routes ---
@user_bp.route("/kondisiEkonomi", methods=["POST"])
@jwt_required_custom()
def create():
    return create_user_kondisi_controller()

@user_bp.route("/kondisiEkonomi/<int:nik>", methods=["GET"])
@jwt_required_custom()
def get_by_nik(nik: int):
    return get_user_kondisi_controller(nik)

@user_bp.route("/kondisiEkonomi/<int:nik>", methods=["PUT"])
@jwt_required_custom()
def update(nik: int):
    return update_user_kondisi_controller(nik)


# --- Aset Non-Finansial routes ---
@user_bp.route('/asetNonFinansial', methods=['POST'])
@jwt_required_custom()
def create_aset():
    from flask import request
    payload = request.get_json() or request.form.to_dict()
    return create_user_aset(payload)


@user_bp.route('/asetNonFinansial/<int:nik>', methods=['GET'])
@jwt_required_custom()
def get_aset(nik: int):
    return get_user_aset(nik)


@user_bp.route('/asetNonFinansial/<int:nik>', methods=['PUT'])
@jwt_required_custom()
def update_aset(nik: int):
    from flask import request
    payload = request.get_json() or request.form.to_dict()
    return update_user_aset(nik, payload)
