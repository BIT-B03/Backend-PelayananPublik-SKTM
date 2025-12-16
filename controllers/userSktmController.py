import os
import time
from flask import jsonify
from io import BytesIO
from templates.sktm.reportlab_layout import generate_sktm_pdf_bytes
from datetime import datetime

from utils.supabase_client import upload_file, create_signed_url, list_files, delete_file, resolve_image_url
import re
from datetime import datetime

from models.ktpModel import KTP
from models.kartukeluargaModel import KartuKeluarga
from models.kondisiekonomiModel import KondisiEkonomi
from models.kondisirumahModel import KondisiRumah
from models.asetnonfinansialModel import AsetNonFinancial
from models.masyarakatModel import Masyarakat

# Static defaults for SKTM header (can be overridden via env)
VILLAGE_HEAD = os.environ.get("SKTM_KEPALA_DESA", "Kepala Desa: Muhammad Muslich")
KECAMATAN = os.environ.get("SKTM_KECAMATAN", "Kecamatan: Candi")
KABUPATEN = os.environ.get("SKTM_KABUPATEN", "Kabupaten: Sidoarjo")


def _check_statuses(nik: int):
    failures = []

    ktp = KTP.query.filter_by(nik=nik).first()
    if not ktp or getattr(ktp, 'status', None) != 'B':
        failures.append({'field': 'ktp', 'status': getattr(ktp, 'status', None) if ktp else None})

    kk_list = KartuKeluarga.query.filter_by(nik=nik).all()
    if not kk_list:
        failures.append({'field': 'kartu_keluarga', 'status': None})
    else:
        for kk in kk_list:
            if getattr(kk, 'status', None) != 'B':
                failures.append({'field': 'kartu_keluarga', 'status': getattr(kk, 'status', None)})
                break

    kondisi_rumah = KondisiRumah.query.filter_by(nik=nik).first()
    if not kondisi_rumah or getattr(kondisi_rumah, 'status', None) != 'B':
        failures.append({'field': 'kondisi_rumah', 'status': getattr(kondisi_rumah, 'status', None) if kondisi_rumah else None})

    kondisi_ekonomi = KondisiEkonomi.query.filter_by(nik=nik).first()
    if not kondisi_ekonomi or getattr(kondisi_ekonomi, 'status', None) != 'B':
        failures.append({'field': 'kondisi_ekonomi', 'status': getattr(kondisi_ekonomi, 'status', None) if kondisi_ekonomi else None})

    aset = AsetNonFinancial.query.filter_by(nik=nik).first()
    if not aset or getattr(aset, 'status', None) != 'B':
        failures.append({'field': 'aset_non_financial', 'status': getattr(aset, 'status', None) if aset else None})

    # Optionally check masyarakat exists
    m = Masyarakat.query.filter_by(nik=nik).first()
    if not m:
        failures.append({'field': 'masyarakat', 'status': None})

    ok = len(failures) == 0
    return ok, failures, m


def can_download_sktm_controller(nik: int):
    ok, failures, _ = _check_statuses(nik)
    if ok:
        return jsonify({"can_download": True}), 200
    return jsonify({"can_download": False, "reason": "statuses_not_ready", "failures": failures}), 403


def download_sktm_controller(nik: int):
    ok, failures, masyarakat = _check_statuses(nik)
    if not ok:
        return jsonify({"message": "Dokumen belum bisa diunduh. Beberapa bagian belum berstatus 'B'", "failures": failures}), 403
    # Generate a simple PDF for SKTM on-the-fly and upload to Supabase Storage
    ktp = KTP.query.filter_by(nik=nik).first()

    nama = getattr(masyarakat, 'nama', '') if masyarakat else ''
    no_ktp = str(nik)
    tempat_lahir = getattr(ktp, 'tempat_lahir', '') if ktp else ''
    tanggal_lahir = ''
    if ktp and getattr(ktp, 'tanggal_lahir', None):
        try:
            tanggal_lahir = ktp.tanggal_lahir.strftime('%d %B %Y')
        except Exception:
            tanggal_lahir = str(ktp.tanggal_lahir)

    jenis_kelamin_code = getattr(masyarakat, 'jenis_kelamin', '') if masyarakat else ''
    jenis_kelamin = 'Laki-laki' if jenis_kelamin_code == 'L' else ('Perempuan' if jenis_kelamin_code == 'P' else jenis_kelamin_code)
    alamat = getattr(ktp, 'alamat', '') if ktp else ''

    # Build data dict for layout helper
    data = {
        'kepala_desa': VILLAGE_HEAD.replace('Kepala Desa: ', '') if VILLAGE_HEAD else '',
        'kecamatan': KECAMATAN.replace('Kecamatan: ', '') if KECAMATAN else '',
        'kabupaten': KABUPATEN.replace('Kabupaten: ', '') if KABUPATEN else '',
        'nama': nama,
        'no_ktp': no_ktp,
        'tempat_tanggal_lahir': f"{tempat_lahir} / {tanggal_lahir}".strip(' / '),
        'jenis_kelamin': jenis_kelamin,
        'alamat': alamat,
        'pernyataan_paragraf': None,
        'kota_tanggal': f"{os.environ.get('SKTM_KOTA', '')}",
        'kepala_nama': os.environ.get('SKTM_KEPALA_NAMA', ''),
    }

    start_all = time.time()

    t0 = time.time()
    file_bytes = generate_sktm_pdf_bytes(data)
    t1 = time.time()
    print(f"[TIMING] pdf_generate={(t1-t0):.2f}s")

    bucket = os.environ.get("SUPABASE_STORAGE_BUCKET") or os.environ.get("SUPABASE_SKTM_BUCKET") or os.environ.get("SUPABASE_SKTm_BUCKET") or os.environ.get("SUPABASE_BUCKET") or "sktm"
    timestamp = int(time.time())
    filename = f"sktm_{nik}_{timestamp}.pdf"
    path = f"{nik}/sktm/{filename}"

    try:
        t0 = time.time()
        url_after_upload = upload_file(bucket, path, file_bytes, content_type="application/pdf")
        t1 = time.time()
        print(f"[TIMING] upload={(t1-t0):.2f}s")
    except Exception as e:
        return jsonify({"message": "Gagal mengunggah ke storage", "error": str(e)}), 500

    if not url_after_upload:
        return jsonify({"message": "Gagal mendapatkan URL setelah upload"}), 500

    # Create signed URL (preferred for private buckets) with configurable expiry
    # default signed URL expiry set to 5 minutes (300s) unless overridden in env
    expires_in = int(os.environ.get("SUPABASE_SIGNED_EXPIRES", "300"))

    t0 = time.time()
    signed_url = create_signed_url(bucket, path, expires=expires_in)
    t1 = time.time()
    print(f"[TIMING] sign_url={(t1-t0):.2f}s")

    # If create_signed_url failed, fallback to returned URL from upload_file
    final_url = signed_url or url_after_upload
    # normalize to absolute URL if backend returned a relative signed path
    final_url = resolve_image_url(final_url) if final_url else final_url
    print(f"[DEBUG sktm] final_url={final_url}")

    # if upload occurred, measure upload time
    try:
        # upload_file may have been called above inside try/except; if url_after_upload exists, we infer upload happened
        pass
    except Exception:
        pass

    print(f"[TIMING] total={(time.time()-start_all):.2f}s")

    # record creation metadata
    created_at = datetime.utcnow().isoformat() + "Z"

    # Cleanup old files: keep latest N (configurable)
    keep_count = int(os.environ.get("SUPABASE_SKTm_KEEP", "3"))
    try:
        items = list_files(bucket, f"{nik}/sktm")
        # normalize to list of names
        paths = []
        for it in items:
            name = None
            if isinstance(it, dict):
                # common keys
                name = it.get('name') or it.get('id') or it.get('path') or it.get('Key')
            elif isinstance(it, str):
                name = it
            if not name:
                continue
            # ensure full path
            if name.startswith(f"{nik}/"):
                paths.append(name)
            else:
                # if list returned just filenames
                paths.append(f"{nik}/sktm/{name}" if not name.startswith('/') else name.lstrip('/'))

        # extract timestamp from filename pattern sktm_<nik>_<ts>.pdf
        def ts_from_path(pth):
            m = re.search(r'sktm_\d+_(\d+)\.pdf$', pth)
            return int(m.group(1)) if m else 0

        paths_sorted = sorted(paths, key=ts_from_path, reverse=True)
        to_delete = paths_sorted[keep_count:]
        for old in to_delete:
            try:
                delete_file(bucket, old)
            except Exception:
                pass
    except Exception:
        pass

    return jsonify({"url": final_url, "path": path, "created_at": created_at, "expires_in": expires_in}), 200
