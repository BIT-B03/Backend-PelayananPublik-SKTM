from datetime import timedelta
from functools import wraps
from flask import jsonify, current_app
from flask_jwt_extended import (
  JWTManager,
  create_access_token,
  create_refresh_token,
  verify_jwt_in_request,
  get_jwt,
  get_jwt_identity,
)
jwt = JWTManager()

def init_jwt(app):
  """
  Inisialisasi JWTManager; panggil di create_app setelah app.config di-set.
  Pastikan app.config['JWT_SECRET_KEY'] tersedia. Jika tidak, fallback ke SECRET_KEY.
  """
  if not app.config.get("JWT_SECRET_KEY"):
    app.config["JWT_SECRET_KEY"] = app.config.get("SECRET_KEY", "change-this-in-production")
  jwt.init_app(app)
  return jwt

def create_tokens_for_user(identity, role=None, access_expires_minutes=15, refresh_expires_days=30):
  """
  Buat access & refresh token. identity biasanya nik atau user id.
  role opsional: None untuk masyarakat (tanpa klaim role).
  """
  claims = {}
  if role:
    claims["role"] = role

  identity_str = str(identity)

  access = create_access_token(
    identity=identity_str,
    additional_claims=claims,
    expires_delta=timedelta(minutes=access_expires_minutes),
  )
  refresh = create_refresh_token(
    identity=identity_str,
    additional_claims=claims,
    expires_delta=timedelta(days=refresh_expires_days),
  )
  return {"access_token": access, "refresh_token": refresh}

def create_offline_token(identity: str, device_id: str, days_valid: int = 14):
    """
    Buat offline JWT RS256 berisi sub (identity) dan device_id.
    Menggunakan OFFLINE_PRIVATE_KEY (PEM) dari config; jika tidak ada, return None.
    """
    import jwt as pyjwt
    from datetime import datetime, timedelta

    private_pem = current_app.config.get("OFFLINE_PRIVATE_KEY")
    if not private_pem:
      return None
    now = datetime.utcnow()
    payload = {
      "sub": identity,
      "device_id": device_id,
      "iat": int(now.timestamp()),
      "exp": int((now + timedelta(days=days_valid)).timestamp()),
      "type": "offline",
    }
    token = pyjwt.encode(payload, private_pem, algorithm="RS256")
    return token

def jwt_required_custom(fn=None, *, fresh=False, optional=False, refresh=False, locations=None):
  """
  Pengganti @jwt_required() yang mengembalikan JSON 401 jika token invalid.
  Bisa dipakai langsung: @jwt_required_custom
  atau dengan opsi: @jwt_required_custom(optional=True)
  """
  def decorator(inner_fn):
    @wraps(inner_fn)
    def wrapper(*args, **kwargs):
      try:
        verify_jwt_in_request(fresh=fresh, optional=optional, refresh=refresh, locations=locations)
        from utils.supabase_client import is_jti_revoked, is_device_revoked
        claims = get_jwt()
        jti = claims.get("jti")
        device_id = claims.get("device_id")
        if jti and is_jti_revoked(jti):
          return jsonify({"error": "Unauthorized", "message": "token_revoked"}), 401
        if device_id and is_device_revoked(device_id):
          return jsonify({"error": "Unauthorized", "message": "device_revoked"}), 401
      except Exception as e:
        return jsonify({"error": "Unauthorized", "message": str(e)}), 401
      return inner_fn(*args, **kwargs)

    return wrapper
  if fn:
    return decorator(fn)
  return decorator

def role_required(*allowed_roles):
  """
  Decorator sederhana untuk cek klaim 'role' pada JWT.
  Contoh: @role_required('admin','petugas')
"""
  def decorator(fn):
    @wraps(fn)
    @jwt_required_custom()
    def wrapper(*args, **kwargs):
      claims = get_jwt()
      role = claims.get("role")
      if role not in allowed_roles:
        return jsonify({"error": "Forbidden", "message": "insufficient role"}), 403
      return fn(*args, **kwargs)
    return wrapper
  return decorator

def get_current_identity():
  """Ambil identity dari token (mis. nik)."""
  return get_jwt_identity()
