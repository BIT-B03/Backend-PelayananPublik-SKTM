from extension import db


class AsetNonFinancial(db.Model):
	__tablename__ = "aset_non_financial"

	id_aset_non_financial = db.Column(db.Integer, primary_key=True, autoincrement=True)
	nik = db.Column(db.Integer, db.ForeignKey("masyarakat.nik"), nullable=False, unique=True)
	total_kendaraan = db.Column(db.Integer)
	masyarakat = db.relationship("Masyarakat", back_populates="aset_non_financial")
	detail_kendaraan = db.relationship(
		"DetailKendaraan", back_populates="aset_non_financial", cascade="all, delete-orphan"
	)
	status = db.Column(db.Enum("B", "T", "P", name="status_enum"), nullable=False)

