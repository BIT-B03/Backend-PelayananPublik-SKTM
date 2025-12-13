from flask import Blueprint, request, jsonify
from utils.auth import jwt_required_custom, role_required
from controllers.authController import register_controller, login_controller
from controllers.authController import logout_controller


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    payload = request.get_json() or {}
    body, status = register_controller(payload)
    return jsonify(body), status


@auth_bp.route("/login", methods=["POST"])
def login():
    payload = request.get_json() or {}
    body, status = login_controller(payload)
    return jsonify(body), status


@auth_bp.route("/logout", methods=["POST"])
@jwt_required_custom
def logout():
    payload = request.get_json() or {}
    body, status = logout_controller(payload)
    return jsonify(body), status

