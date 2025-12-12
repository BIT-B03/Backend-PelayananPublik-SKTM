from extension import db


class KondisiRumah(db.Model):
	__tablename__ = "kondisi_rumah"

	id_kondisi_rumah = db.Column(db.Integer, primary_key=True, autoincrement=True)
	nik = db.Column(db.Integer, db.ForeignKey("masyarakat.nik"), nullable=False, unique=True)
	foto_depan_rumah = db.Column(db.String(255))
	foto_atap = db.Column(db.String(255))
	foto_lantai = db.Column(db.String(255))
	foto_kamar_mandi = db.Column(db.String(255))
	status = db.Column(db.Enum("B", "T", "P", name="status_enum"), nullable=False)

	masyarakat = db.relationship("Masyarakat", back_populates="kondisi_rumah")

