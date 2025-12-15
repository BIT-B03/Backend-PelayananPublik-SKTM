from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity
from extension import db
from models.masyarakatModel import Masyarakat
from models.ktpModel import KTP
from models.kartukeluargaModel import KartuKeluarga
from schema.userProfileSchema import profil_schema, profil_update_schema
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError


def get_profile_controller(nik: int):
    try:
        if request.method != 'GET':
            return jsonify({"message": "Method Not Allowed"}), 405

        ms = Masyarakat.query.get(nik)
        ktp = KTP.query.filter_by(nik=nik).first()
        kk = KartuKeluarga.query.filter_by(nik=nik).first()

        if not ms and not ktp and not kk:
            return jsonify({"message": f"Profil untuk nik {nik} tidak ditemukan"}), 404

        data = {
            "nik": nik,
            "nama": ms.nama if ms else None,
            "alamat": ktp.alamat if ktp and ktp.alamat else (kk.alamat if kk and kk.alamat else None),
            "no_kk": kk.no_kk if kk else None,
            "tempat_lahir": ktp.tempat_lahir if ktp else None,
            "tanggal_lahir": ktp.tanggal_lahir if ktp else None,
            "nomor_hp": ms.nomor_hp if ms else None,
            "email": ms.email if ms else None,
        }

        return jsonify({"message": "Data profil berhasil diambil", "data": profil_schema.dump(data)}), 200

    except Exception as e:
        return jsonify({"message": f"Terjadi kesalahan server: {str(e)}"}), 500


def update_profile_controller(nik: int):
    try:
        if request.method != 'PUT':
            return jsonify({"message": "Method Not Allowed"}), 405

        identity = get_jwt_identity()
        try:
            nik_from_token = int(identity)
        except Exception:
            return jsonify({"message": "Invalid identity in token"}), 500

        if nik_from_token != nik:
            return jsonify({"message": "Forbidden: cannot update other user's profile"}), 403

        ms = Masyarakat.query.get(nik)
        ktp = KTP.query.filter_by(nik=nik).first()
        kk = KartuKeluarga.query.filter_by(nik=nik).first()

        data = request.get_json(silent=True) or request.form.to_dict() or {}
        try:
            validated = profil_update_schema.load(data)
        except ValidationError as ve:
            return jsonify({"message": "Validation error", "errors": ve.messages}), 400

        # Update masyarakat fields
        if ms:
            if 'nomor_hp' in validated:
                ms.nomor_hp = validated.get('nomor_hp')
            if 'email' in validated:
                ms.email = validated.get('email')
        else:
            # create minimal masyarakat if missing is probably not desirable; return error
            return jsonify({"message": "Masyarakat not found"}), 404

        # Update or create KTP (unique per nik)
        if any(field in validated for field in ['tempat_lahir', 'tanggal_lahir', 'alamat']):
            if not ktp:
                ktp = KTP(nik=nik)
                db.session.add(ktp)
            if 'tempat_lahir' in validated:
                ktp.tempat_lahir = validated.get('tempat_lahir')
            if 'tanggal_lahir' in validated:
                ktp.tanggal_lahir = validated.get('tanggal_lahir')
            if 'alamat' in validated:
                ktp.alamat = validated.get('alamat')

        # Update or create Kartu Keluarga (take first)
        if 'no_kk' in validated:
            if not kk:
                kk = KartuKeluarga(nik=nik)
                db.session.add(kk)
            kk.no_kk = validated.get('no_kk')

        db.session.commit()

        # Refresh objects
        ms = Masyarakat.query.get(nik)
        ktp = KTP.query.filter_by(nik=nik).first()
        kk = KartuKeluarga.query.filter_by(nik=nik).first()

        resp = {
            "nik": nik,
            "nama": ms.nama if ms else None,
            "alamat": ktp.alamat if ktp and ktp.alamat else (kk.alamat if kk and kk.alamat else None),
            "no_kk": kk.no_kk if kk else None,
            "tempat_lahir": ktp.tempat_lahir if ktp else None,
            "tanggal_lahir": ktp.tanggal_lahir if ktp else None,
            "nomor_hp": ms.nomor_hp if ms else None,
            "email": ms.email if ms else None,
        }

        return jsonify({"message": "Profil berhasil diperbarui", "data": profil_schema.dump(resp)}), 200

    except IntegrityError as ie:
        db.session.rollback()
        return jsonify({"message": f"Integrity error: {str(ie.orig)}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Terjadi kesalahan server: {str(e)}"}), 500


def get_my_profile_controller():
    try:
        identity = get_jwt_identity()
        nik = int(identity)
    except Exception:
        return jsonify({"message": "Missing or invalid identity token"}), 401

    return get_profile_controller(nik)


def update_my_profile_controller():
    try:
        identity = get_jwt_identity()
        nik = int(identity)
    except Exception:
        return jsonify({"message": "Missing or invalid identity token"}), 401

    return update_profile_controller(nik)
