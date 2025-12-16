import os
import requests
from urllib.parse import quote
from uuid import uuid4
import time
from supabase import create_client
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

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
        res = _client.table("device").select("device_id").limit(1).execute()
        return getattr(res, "status_code", 200) in (200, 0) or bool(getattr(res, "data", None) is not None)
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


def upload_file(bucket: str, path: str, file_bytes: bytes, content_type: str | None = None):
    """Upload bytes to Supabase Storage and return public URL or signed URL.

    Args:
        bucket: bucket name
        path: destination path in bucket
        file_bytes: file content as bytes
        content_type: optional MIME type

    Returns:
        public URL string or signed URL, or None on failure
    """
    client = _ensure_client()
    storage = client.storage.from_(bucket)

    # try upload with content-type option first, fallback if needed
    file_options = {"content-type": content_type} if content_type else None

    def _do_upload(pth, opts):
        if opts:
            return storage.upload(pth, file_bytes, opts)
        return storage.upload(pth, file_bytes)

    try:
        try:
            res = _do_upload(path, file_options)
        except Exception as e:
            # if upload with options failed, retry without options
            try:
                res = _do_upload(path, None)
            except Exception as e2:
                # if duplicate or other error, try a unique filename
                err_text = str(e2)
                if 'already exists' in err_text or 'Duplicate' in err_text or '409' in err_text:
                    # append uuid to filename and retry
                    base, dot, ext = path.rpartition('.')
                    suffix = f"_{int(time.time())}_{uuid4().hex}"
                    new_path = (base + suffix + ('.' + ext if dot else ''))
                    try:
                        print(f"[DEBUG supabase] original path exists, retrying with unique path: {new_path}")
                        res = _do_upload(new_path, None)
                        path = new_path
                    except Exception as e3:
                        buckets_info = None
                        try:
                            url = SUPABASE_URL.rstrip('/') + '/storage/v1/bucket'
                            headers = {"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY}
                            r = requests.get(url, headers=headers, timeout=10)
                            buckets_info = r.json() if r.status_code == 200 else f"HTTP {r.status_code}"
                        except Exception:
                            buckets_info = "failed to list buckets"
                        raise RuntimeError(
                            f"Failed to upload to Supabase storage. bucket={bucket!r} path={path!r} "
                            f"error_primary={e!r} error_fallback={e2!r} error_retry={e3!r} buckets={buckets_info!r}"
                        ) from e3
                else:
                    # unknown error, raise with diagnostics
                    buckets_info = None
                    try:
                        url = SUPABASE_URL.rstrip('/') + '/storage/v1/bucket'
                        headers = {"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY}
                        r = requests.get(url, headers=headers, timeout=10)
                        buckets_info = r.json() if r.status_code == 200 else f"HTTP {r.status_code}"
                    except Exception:
                        buckets_info = "failed to list buckets"
                    raise RuntimeError(
                        f"Failed to upload to Supabase storage. bucket={bucket!r} path={path!r} "
                        f"error_primary={e!r} error_fallback={e2!r} buckets={buckets_info!r}"
                    ) from e2
    except Exception:
        # re-raise after handling above; let caller log/handle
        raise

    # debug: log upload response before trying to extract public URL
    try:
        try:
            info = {}
            if isinstance(res, dict):
                info = res
            else:
                info['repr'] = repr(res)
                info['data'] = getattr(res, 'data', None)
                info['status'] = getattr(res, 'status', getattr(res, 'status_code', None))
            print(f"[DEBUG supabase] upload response: {info}")
        except Exception as _:
            print(f"[DEBUG supabase] upload response raw: {repr(res)}")
    except NameError:
        print("[DEBUG supabase] upload did not set 'res'")

    # get public url
    # get public url (handle different response shapes)
    try:
        pub = storage.get_public_url(path)
        if isinstance(pub, dict):
            # keys may vary by version
            for key in ("publicURL", "public_url", "publicUrl", "public-url"):
                if key in pub and pub[key]:
                    return pub[key]
            # fallback to any string value
            for v in pub.values():
                if isinstance(v, str) and v.startswith('http'):
                    return v
        else:
            # object-like response
            for attr in ("publicURL", "public_url", "publicUrl"):
                val = getattr(pub, attr, None)
                if val:
                    return val

        # no public url (private bucket) -> try REST signed-url fallback
        try:
            sign_url = SUPABASE_URL.rstrip('/') + f"/storage/v1/object/sign/{bucket}/{path}"
            headers = {
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "apikey": SUPABASE_KEY,
                "Content-Type": "application/json",
            }
            payload = {"expiresIn": 60 * 60}
            r = requests.post(sign_url, headers=headers, json=payload, timeout=10)
            try:
                r.raise_for_status()
            except Exception as rexc:
                print(f"[DEBUG supabase] REST signed-url request failed status={r.status_code} text={r.text}")
                raise
            data = r.json()
            # try common response keys
            for key in ("signedURL", "signed_url", "signedUrl"):
                if key in data and data[key]:
                    return data[key]
            # fallback to any http string in response
            for v in data.values():
                if isinstance(v, str) and v.startswith('http'):
                    return v
        except Exception as se:
            print(f"[DEBUG supabase] create_signed_url_rest failed for bucket={bucket} path={path}: {se}")
        return None
    except Exception as e:
        print(f"[DEBUG supabase] get_public_url failed for bucket={bucket} path={path}: {e}")
        return None


def download_public_url(bucket: str, path: str):
    client = _ensure_client()
    storage = client.storage.from_(bucket)
    pub = storage.get_public_url(path)
    if isinstance(pub, dict):
        return pub.get("publicURL") or pub.get("public_url")
    return getattr(pub, "publicURL", None) or getattr(pub, "public_url", None)


def delete_file(bucket: str, path: str) -> bool:
    """Delete a file from Supabase storage. Returns True on success, False otherwise."""
    client = _ensure_client()
    storage = client.storage.from_(bucket)
    try:
        res = storage.remove([path])    
        return True
    except Exception as e:
        print(f"[DEBUG supabase] delete_file failed for bucket={bucket} path={path}: {e}")
        return False


def delete_file_by_url(bucket: str, url: str) -> bool:
    """Attempt to extract storage path from a public/signed URL and delete the file.

    Handles common Supabase public URL formats like:
      https://<project>.supabase.co/storage/v1/object/public/<bucket>/<path>
    or direct public URLs that include '/<bucket>/' in the path.
    """
    if not url:
        return False
    try:
        # try to find '/<bucket>/' and take the rest as path
        marker = f"/{bucket}/"
        if marker in url:
            path = url.split(marker, 1)[1]
            # strip query params
            path = path.split('?', 1)[0]
            return delete_file(bucket, path)

        # Try common storage API path
        parts = url.split('/storage/v1/object/public/')
        if len(parts) == 2:
            rest = parts[1]
            if rest.startswith(bucket + '/'):
                path = rest[len(bucket) + 1 :].split('?', 1)[0]
                return delete_file(bucket, path)

        # Fallback: last path segment
        from urllib.parse import urlparse
        parsed = urlparse(url)
        p = parsed.path.lstrip('/')
        # try to remove bucket prefix if present
        if p.startswith(bucket + '/'):
            path = p[len(bucket) + 1 :]
        else:
            # use entire path as last resort
            path = p
        path = path.split('?', 1)[0]
        return delete_file(bucket, path)
    except Exception as e:
        print(f"[DEBUG supabase] delete_file_by_url failed for url={url}: {e}")
        return False


def upload_file_from_storage(bucket: str, nik: int, file_storage, dest_folder: str, field_name: str):
    """Helper to upload a Flask/Werkzeug FileStorage to Supabase Storage.

    Args:
        bucket: bucket name
        nik: identity used as folder prefix
        file_storage: FileStorage object (has .filename, .read(), .mimetype)
        dest_folder: folder under nik (e.g. 'kk' or 'ktp')
        field_name: fallback name when filename missing

    Returns:
        public or signed URL string, or None on failure
    """
    if not file_storage:
        return None
    from werkzeug.utils import secure_filename
    import os
    from uuid import uuid4

    filename = secure_filename(getattr(file_storage, 'filename', None) or field_name)
    base, ext = os.path.splitext(filename)
    unique_name = f"{base}_{uuid4().hex}{ext}"
    path = f"{nik}/{dest_folder}/{unique_name}"
    file_bytes = file_storage.read()
    return upload_file(bucket, path, file_bytes, content_type=getattr(file_storage, 'mimetype', None))


def make_absolute_signed_url(value: str) -> str:
    if not value or not isinstance(value, str):
        return value
    if value.startswith('/'):
        if SUPABASE_URL:
            return f"{SUPABASE_URL}/storage/v1{value}"
    return value


def resolve_image_url(value: str, expires: int = 3600) -> str:
    if not value or not isinstance(value, str):
        return value

    if value.startswith('http://') or value.startswith('https://'):
        return value

    prefix = '/object/sign/'
    if value.startswith(prefix):
        rest = value[len(prefix):]
        path_part = rest.split('?', 1)[0]
        if '/' not in path_part:
            return make_absolute_signed_url(value)
        bucket, object_path = path_part.split('/', 1)

        service_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or SUPABASE_KEY
        if not SUPABASE_URL or not service_key:
            return make_absolute_signed_url(value)

        encoded = quote(object_path, safe='/')
        sign_endpoint = f"{SUPABASE_URL}/storage/v1/object/sign/{bucket}/{encoded}"
        headers = {"Authorization": f"Bearer {service_key}", "Content-Type": "application/json"}
        payload = {"expiresIn": expires}
        try:
            r = requests.post(sign_endpoint, headers=headers, json=payload, timeout=10)
            if r.status_code == 200:
                try:
                    data = r.json()
                    for key in ("signedURL", "signedUrl", "signed_url", "url"):
                        if key in data and isinstance(data[key], str):
                            url = data[key]
                            if url.startswith('/'):
                                return f"{SUPABASE_URL}/storage/v1{url}"
                            return url
                except Exception:
                    text = r.text
                    if isinstance(text, str) and text.startswith('/'):
                        return f"{SUPABASE_URL}/storage/v1{text}"
                    return text
            # non-200 -> fallback
            return make_absolute_signed_url(value)
        except requests.RequestException:
            return make_absolute_signed_url(value)

    return make_absolute_signed_url(value)
