from flask import jsonify, request
from werkzeug.security import check_password_hash
from extension import db
from models.petugasModel import Petugas
from schema.adminPetugasAuthSchema import petugas_login_schema
from marshmallow import ValidationError
from utils.auth import create_tokens_for_user


def petugas_login_controller():
    try:
        if request.method != 'POST':
            return jsonify({"message": "Method Not Allowed"}), 405

        payload = request.get_json() or {}
        try:
            data = petugas_login_schema.load(payload)
        except ValidationError as ve:
            return jsonify({"message": "Validation error", "errors": ve.messages}), 400

        nip = data.get('nip')
        password = data.get('password')

        petugas = Petugas.query.get(nip)
        if not petugas:
            return jsonify({"error": "Unauthorized", "message": "Invalid credentials"}), 401

        if not petugas.password or not check_password_hash(petugas.password, password):
            return jsonify({"error": "Unauthorized", "message": "Invalid credentials"}), 401

        tokens = create_tokens_for_user(identity=nip, role=petugas.role)
        return jsonify({"message": "Login success", **tokens, "role": petugas.role}), 200

    except Exception as e:
        return jsonify({"message": f"Server error: {str(e)}"}), 500
