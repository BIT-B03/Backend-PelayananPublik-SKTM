from typing import Tuple
from flask import jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow import ValidationError
from extension import db
from models.masyarakatModel import Masyarakat
from utils.auth import create_tokens_for_user, create_offline_token
from utils.supabase_client import (
    create_device_record,
    get_device_by_id,
    is_device_revoked,
    add_jti_block,
)
import uuid
from schema.authSchema import RegisterSchema, LoginSchema


def register_controller(payload: dict) -> Tuple[dict, int]:
    try:
        data = RegisterSchema().load(payload)
    except ValidationError as err:
        return {"error": "Bad Request", "message": err.messages}, 400

    if Masyarakat.query.filter_by(nik=data["nik"]).first():
        return {"error": "Conflict", "message": "NIK already in use"}, 409

    password_hash = generate_password_hash(data["password"])

    masyarakat = Masyarakat(
        nik=data["nik"],
        nama=data["nama"],
        jenis_kelamin=data["jenis_kelamin"],
        email=data["email"],
        nomor_hp=data["nomor_hp"],
        password=password_hash,
    )
    db.session.add(masyarakat)
    db.session.commit()

    return {"message": "Registrasi berhasil", "nik": data["nik"], "nama":data["nama"]}, 201


def login_controller(payload: dict) -> Tuple[dict, int]:
    try:
        data = LoginSchema().load(payload)
    except ValidationError as err:
        return {"error": "Bad Request", "message": err.messages}, 400

    user = Masyarakat.query.filter_by(nik=data["nik"]).first()
    if not user:
        return {"error": "Unauthorized", "message": "Invalid NIK"}, 401

    if not check_password_hash(user.password, data["password"]):
        return {"error": "Unauthorized", "message": "Invalid Password"}, 401

    device_id = payload.get("device_id") or str(uuid.uuid4())
    device_name = payload.get("device_name")

    existing = get_device_by_id(device_id)
    if not existing:
        create_device_record(device_id=device_id, nik=user.nik, device_name=device_name)
    else:
        if existing.get("nik") != user.nik:
            return {"error": "Forbidden", "message": "Device tidak sesuai pemilik"}, 403

    if is_device_revoked(device_id):
        return {"error": "Forbidden", "message": "Device diblokir"}, 403

    tokens = create_tokens_for_user(identity=user.nik, role=None)
    offline_token = create_offline_token(identity=str(user.nik), device_id=device_id)
    resp = {"message": "Login success", **tokens}
    if offline_token:
        resp["offline_token"] = offline_token
        resp["device_id"] = device_id
    return resp, 200


def logout_controller(payload: dict) -> Tuple[dict, int]:
    claims = get_jwt()
    identity = get_jwt_identity()
    jti = claims.get("jti")
    device_id = payload.get("device_id")

    if jti:
        add_jti_block(jti=jti, token_type=claims.get("type", "access"), identity=str(identity))

    if device_id:
        # Optional: soft revoke device via Supabase
        from utils.supabase_client import revoke_device
        try:
            revoke_device(device_id)
        except Exception:
            pass

    return {"message": "Logout success"}, 200


def refresh_controller(payload: dict) -> Tuple[dict, int]:
    """Rotate refresh token: block current refresh jti and issue new access+refresh."""
    claims = get_jwt()
    identity = get_jwt_identity()
    jti = claims.get("jti")

    if jti:
        try:
            add_jti_block(jti=jti, token_type=claims.get("type", "refresh"), identity=str(identity))
        except Exception:
            pass

    tokens = create_tokens_for_user(identity=identity, role=None)
    return tokens, 200
