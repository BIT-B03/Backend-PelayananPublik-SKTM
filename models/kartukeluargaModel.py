from sqlalchemy import Enum as SAEnum
from extension import db


class KartuKeluarga(db.Model):
    __tablename__ = "kartu_keluarga"

    id_kk = db.Column(db.Integer, primary_key=True, autoincrement=True)
    no_kk = db.Column(db.Integer)
    nama_kepala_keluarga = db.Column(db.String(255))
    alamat = db.Column(db.Text)
    foto_kk = db.Column(db.String(255))
    status = db.Column(SAEnum("P", "T", "B", name="kartu_keluarga_status_enum"), nullable=True)
    nik = db.Column(db.Integer, db.ForeignKey("masyarakat.nik"), nullable=False)

    masyarakat = db.relationship("Masyarakat", back_populates="kartu_keluarga")
