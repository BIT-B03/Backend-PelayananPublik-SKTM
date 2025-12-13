from flask import Blueprint, request, jsonify
from controllers.userKondisiEkonomiController import (
    create_user_kondisi,
    get_user_kondisi,
    update_user_kondisi,
)
from utils.auth import jwt_required_custom

user_kondisi_bp = Blueprint("user_kondisi", __name__, url_prefix="/userKondisiEkonomi")


@user_kondisi_bp.route("/", methods=["POST"])
@jwt_required_custom()
def create():
    # Expect multipart/form-data with files + form fields
    form = request.form.to_dict()
    files = request.files
    result, status = create_user_kondisi(form, files)
    return jsonify(result), status


@user_kondisi_bp.route("/<int:nik>", methods=["GET"])
@jwt_required_custom()
def get_by_nik(nik: int):
    data = get_user_kondisi(nik)
    if not data:
        return jsonify({"message": "Not found"}), 404
    return jsonify({"data": data}), 200


@user_kondisi_bp.route("/<int:nik>", methods=["PUT"])
@jwt_required_custom()
def update(nik: int):
    form = request.form.to_dict()
    files = request.files
    result, status = update_user_kondisi(nik, form, files)
    return jsonify(result), status
