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
from controllers.userProfileController import (
    get_profile_controller,
    update_profile_controller,
    get_my_profile_controller,
    update_my_profile_controller,
)
from controllers.userSktmController import (
    can_download_sktm_controller,
    download_sktm_controller,
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


@user_bp.route("/kondisiEkonomi", methods=["PUT"])
@jwt_required_custom()
def update_kondisi_self():
    from controllers.userKondisiEkonomiController import update_user_kondisi_self_controller
    return update_user_kondisi_self_controller()


# --- Aset Non-Finansial routes ---
@user_bp.route('/asetNonFinansial', methods=['POST'])
@jwt_required_custom()
def create_aset():
    return create_user_aset()


@user_bp.route('/asetNonFinansial/<int:nik>', methods=['GET'])
@jwt_required_custom()
def get_aset(nik: int):
    return get_user_aset(nik)


@user_bp.route('/asetNonFinansial/<int:nik>', methods=['PUT'])
@jwt_required_custom()
def update_aset(nik: int):
    return update_user_aset(nik)


@user_bp.route('/asetNonFinansial', methods=['PUT'])
@jwt_required_custom()
def update_aset_self():
    from controllers.userasetNonfinansialController import update_user_aset_self_controller
    return update_user_aset_self_controller()


# --- Profil routes ---
@user_bp.route('/profil/<int:nik>', methods=['GET'])
@jwt_required_custom()
def get_profil(nik: int):
    return get_profile_controller(nik)


@user_bp.route('/profil/<int:nik>', methods=['PUT'])
@jwt_required_custom()
def update_profil(nik: int):
    return update_profile_controller(nik)


@user_bp.route('/profil', methods=['GET'])
@jwt_required_custom()
def get_my_profil():
    return get_my_profile_controller()


@user_bp.route('/profil', methods=['PUT'])
@jwt_required_custom()
def update_my_profil():
    return update_my_profile_controller()


# --- SKTM routes ---
@user_bp.route('/sktm/<int:nik>/can-download', methods=['GET'])
@jwt_required_custom()
def can_download_sktm(nik: int):
    return can_download_sktm_controller(nik)


@user_bp.route('/sktm/<int:nik>/download', methods=['GET'])
@jwt_required_custom()
def download_sktm(nik: int):
    return download_sktm_controller(nik)

# --- Form fill progress (computed from existing tables, no draft table required) ---
@user_bp.route('/forms/progress/<int:user_id>/<string:form_type>', methods=['GET'])
@jwt_required_custom()
def get_form_progress(user_id, form_type):
    from controllers.formDraftController import compute_fill_progress_controller
    return compute_fill_progress_controller(user_id, form_type)


@user_bp.route('/forms/progress/me/<string:form_type>', methods=['GET'])
@jwt_required_custom()
def get_my_form_progress(form_type):
    from utils.auth import get_current_identity
    from controllers.formDraftController import compute_fill_progress_controller
    identity = get_current_identity()
    try:
        nik = int(identity)
    except Exception:
        # if identity is not numeric, return error
        return {'message': 'invalid_identity'}, 400
    return compute_fill_progress_controller(nik, form_type)
