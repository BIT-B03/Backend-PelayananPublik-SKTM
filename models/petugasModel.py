from extension import db
class Petugas(db.Model):
	__tablename__ = "petugas"
	nip = db.Column(db.Integer, primary_key=True)
	nik = db.Column(db.Integer, db.ForeignKey("masyarakat.nik"), nullable=False)
	password = db.Column(db.String(255))
	role = db.Column(db.String(10))
	masyarakat = db.relationship("Masyarakat", back_populates="petugas")

