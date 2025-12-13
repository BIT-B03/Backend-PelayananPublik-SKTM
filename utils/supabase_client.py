import os
from supabase import create_client
from datetime import datetime, timedelta

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Defaults (days)
DEVICE_EXPIRES_DAYS = int(os.environ.get("DEVICE_EXPIRES_DAYS", "14"))
TOKEN_BLOCKLIST_EXPIRES_DAYS = int(os.environ.get("TOKEN_BLOCKLIST_EXPIRES_DAYS", "30"))

_client = None
if SUPABASE_URL and SUPABASE_KEY:
    _client = create_client(SUPABASE_URL, SUPABASE_KEY)

def test_connection() -> bool:
    if not _client:
        return False
    try:
        res= _client.table("device").select("device_id").limit(1).execute()
        return getattr(res, "status_code", 200 ) in (200, 0) or bool(getattr(res, "data", None) is not None)
    except Exception:
        return False

def _ensure_client():
    if _client is None:
        raise RuntimeError("Supabase client not configured")
    return _client

def create_device_record(device_id: str, nik: int, device_name: str | None = None):
    client = _ensure_client()
    now = datetime.utcnow()
    data = {
        "device_id": device_id,
        "nik": nik,
        "issued_at": now.isoformat() + "Z",
        "expires_at": (now + timedelta(days=DEVICE_EXPIRES_DAYS)).isoformat() + "Z",
        "revoked": False,
    }
    if device_name:
        data["device_name"] = device_name
    res = client.table("device").insert(data).execute()
    return res.data

def get_device_by_id(device_id: str):
    client = _ensure_client()
    res = client.table("device").select("device_id, nik, revoked").eq("device_id", device_id).limit(1).execute()
    return res.data[0] if res.data else None

def is_device_revoked(device_id: str) -> bool:
    record = get_device_by_id(device_id)
    return bool(record and record.get("revoked"))

def add_jti_block(jti: str, token_type: str, identity: str | None = None, reason: str | None = None):
    client = _ensure_client()
    now = datetime.utcnow()
    data = {
        "jti": jti,
        "token_type": token_type,
        "issued_at": now.isoformat() + "Z",
        "expires_at": (now + timedelta(days=TOKEN_BLOCKLIST_EXPIRES_DAYS)).isoformat() + "Z",
    }
    if identity:
        data["identity"] = identity
    if reason:
        data["reason"] = reason
    res = client.table("token_blocklist").insert(data).execute()
    return res.data

def is_jti_revoked(jti: str) -> bool:
    client = _ensure_client()
    res = client.table("token_blocklist").select("id").eq("jti", jti).limit(1).execute()
    return bool(res.data)

def revoke_device(device_id: str):
    client = _ensure_client()
    res = client.table("device").update({"revoked": True}).eq("device_id", device_id).execute()
    return res.data
