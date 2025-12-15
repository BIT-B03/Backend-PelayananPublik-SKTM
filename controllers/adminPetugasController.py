from flask import jsonify, request
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from extension import db
from models.petugasModel import Petugas
from models.masyarakatModel import Masyarakat
from schema.adminPetugasSchema import create_petugas_schema, petugas_schema
from marshmallow import ValidationError


def create_petugas_controller(payload: dict):
    try:
        if request.method != 'POST':
            return jsonify({"message": "Method Not Allowed"}), 405

        # validate payload
        try:
            validated = create_petugas_schema.load(payload or {})
        except ValidationError as ve:
            return jsonify({"message": "Validation error", "errors": ve.messages}), 400

        nik = validated.get('nik')
        password = validated.get('password')
        role = validated.get('role')

        # Pastikan masyarakat exist
        ms = Masyarakat.query.get(nik)
        if not ms:
            return jsonify({"message": "masyarakat not found for provided nik"}), 404

        # Cek apakah sudah ada petugas untuk nik ini
        existing = Petugas.query.filter_by(nik=nik).first()
        if existing:
            return jsonify({"message": "petugas already exists for this nik"}), 409

        # Jika tidak ada password diberikan, buat password default (contoh: 6 digit terakhir nomor_hp atau nik)
        if not password:
            raw = (ms.nomor_hp or str(ms.nik))
            password = raw[-6:]

        hashed = generate_password_hash(password)

        new = Petugas(nik=nik, password=hashed, role=role or 'petugas')
        db.session.add(new)
        db.session.commit()

        result = petugas_schema.dump(new)
        return jsonify({"message": "petugas created", "data": result}), 201

    except IntegrityError as ie:
        db.session.rollback()
        return jsonify({"message": f"Integrity error: {str(ie.orig)}"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Server error: {str(e)}"}), 500
