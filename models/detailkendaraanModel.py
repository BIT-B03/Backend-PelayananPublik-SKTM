from sqlalchemy.dialects.mysql import YEAR as MySQLYEAR
from extension import db


class DetailKendaraan(db.Model):
    __tablename__ = "detail_kendaraan"

    id_detail_kendaraan = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_aset_non_financial = db.Column(db.Integer, db.ForeignKey("aset_non_financial.id_aset_non_financial"), nullable=False)
    jenis_kendaraan = db.Column(db.String(100))
    tipe_kendaraan = db.Column(db.String(100))
    tahun_pembuatan = db.Column(MySQLYEAR)
    status = db.Column(db.Enum("B", "T", "P", name="status_enum"), nullable=False)

    aset_non_financial = db.relationship("AsetNonFinancial", back_populates="detail_kendaraan")