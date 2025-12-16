import traceback
from flask import jsonify




def compute_sktm_fill_progress(user_id: int) -> dict:
    """Compute fill progress for SKTM based on presence of required fields in existing tables.
    Returns dict with keys: fill_progress (0..100), total, satisfied, missing (list)
    """
    try:
        from models.masyarakatModel import Masyarakat
        from models.ktpModel import KTP
        from models.kartukeluargaModel import KartuKeluarga
        from models.kondisiekonomiModel import KondisiEkonomi
        from models.kondisirumahModel import KondisiRumah
        from models.asetnonfinansialModel import AsetNonFinancial
    except Exception:
        return {'fill_progress': 0.0, 'total': 0, 'satisfied': 0, 'missing': []}

    checks = []

    m = Masyarakat.query.filter_by(nik=user_id).first()
    ktp = KTP.query.filter_by(nik=user_id).first()
    kk_count = KartuKeluarga.query.filter_by(nik=user_id).count()
    kondisi_rumah = KondisiRumah.query.filter_by(nik=user_id).first()
    kondisi_ekonomi = KondisiEkonomi.query.filter_by(nik=user_id).first()
    aset = AsetNonFinancial.query.filter_by(nik=user_id).first()

    # Define simple presence checks
    checks.append(('masyarakat.nama', bool(m and getattr(m, 'nama', None))))
    checks.append(('ktp.tempat_lahir', bool(ktp and getattr(ktp, 'tempat_lahir', None))))
    checks.append(('ktp.tanggal_lahir', bool(ktp and getattr(ktp, 'tanggal_lahir', None))))
    checks.append(('ktp.alamat', bool(ktp and getattr(ktp, 'alamat', None))))
    checks.append(('kartu_keluarga.exists', kk_count > 0))
    checks.append(('kondisi_rumah.exists', bool(kondisi_rumah)))
    checks.append(('kondisi_ekonomi.exists', bool(kondisi_ekonomi)))
    checks.append(('aset_non_financial.exists', bool(aset)))

    total = len(checks)
    satisfied = sum(1 for _, ok in checks if ok)
    missing = [name for name, ok in checks if not ok]
    fill_progress = (satisfied / total) * 100.0 if total > 0 else 0.0

    return {
        'fill_progress': round(fill_progress, 2),
        'total': total,
        'satisfied': satisfied,
        'missing': missing,
    }


def compute_fill_progress_controller(user_id: int, form_type: str):
    if form_type == 'sktm':
        result = compute_sktm_fill_progress(user_id)
        return jsonify({'form_type': 'sktm', **result}), 200
    return jsonify({'form_type': form_type, 'fill_progress': 0.0, 'message': 'unknown form_type'}), 200
