from extension import db


class KondisiEkonomi(db.Model):
	__tablename__ = "kondisi_ekonomi"

	id_kondisi_ekonomi = db.Column(db.Integer, primary_key=True, autoincrement=True)
	nik = db.Column(db.Integer, db.ForeignKey("masyarakat.nik"), nullable=False, unique=True)
	nominal_slip_gaji = db.Column(db.Integer)
	foto_slip_gaji = db.Column(db.String(255))
	daya_listrik_va = db.Column(db.Integer)
	foto_token_listrik = db.Column(db.String(255))
	status = db.Column(db.Enum("B", "T", "P", name="status_enum"), nullable=False)

	masyarakat = db.relationship("Masyarakat", back_populates="kondisi_ekonomi")

