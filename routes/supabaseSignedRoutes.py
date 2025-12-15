from flask import Blueprint, request, jsonify
import os
import requests
from urllib.parse import quote
from dotenv import load_dotenv
from utils.auth import jwt_required_custom, role_required

# ensure environment variables from .env are loaded when this module is imported
load_dotenv()

supabase_bp = Blueprint('supabase', __name__)

@supabase_bp.route('/supabase/signed-url', methods=['GET'])
@jwt_required_custom()
@role_required('petugas', 'admin')
def get_signed_url():
    """
    Return a signed URL for a storage object.

    Query params:
      - path: object path inside bucket, e.g. '1234567890123456/kondisi_ekonomi/file.png'
      - expires: seconds until expiry (optional, default 3600)
    """
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ.get('SUPABASE_KEY')
    BUCKET = os.environ.get('SUPABASE_STORAGE_BUCKET', 'public')

    path = request.args.get('path')
    if not path:
        return jsonify({"error": "path query param is required"}), 400

    # Basic sanitization
    if path.startswith('/') or '..' in path:
        return jsonify({"error": "invalid path"}), 400

    try:
        expires = int(request.args.get('expires', 3600))
    except Exception:
        return jsonify({"error": "expires must be integer seconds"}), 400

    if not SUPABASE_URL or not SERVICE_KEY:
        return jsonify({"error": "Supabase configuration missing on server"}), 500

    # URL-encode path
    encoded_path = quote(path, safe='/')
    sign_endpoint = f"{SUPABASE_URL}/storage/v1/object/sign/{BUCKET}/{encoded_path}"

    headers = {
        "Authorization": f"Bearer {SERVICE_KEY}",
        "Content-Type": "application/json"
    }
    body = {"expiresIn": expires}

    try:
        print(f"[DEBUG] Supabase sign request: endpoint={sign_endpoint} expires={expires}")
        resp = requests.post(sign_endpoint, headers=headers, json=body, timeout=10)
    except requests.RequestException as e:
        return jsonify({"error": "failed to contact supabase storage", "detail": str(e)}), 502

    if resp.status_code != 200:
        print(f"[DEBUG] Supabase sign failed: status={resp.status_code} text={resp.text}")
        return jsonify({"error": "failed to create signed url", "detail": resp.text}), 502

    try:
        return jsonify(resp.json()), 200
    except Exception:
        return jsonify({"signedURL": resp.text}), 200
