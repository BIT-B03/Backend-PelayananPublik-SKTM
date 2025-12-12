from extension import db


class HumanCapital(db.Model):
    __tablename__ = "human_capital"

    id_human_capital = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nik = db.Column(db.Integer, db.ForeignKey("masyarakat.nik"), nullable=False, unique=True)
    tingkat_pendidikan_kepala_keluarga = db.Column(db.String(50))
    anak_tidak_sekolah = db.Column(db.String(255))
    status = db.Column(db.Enum("B", "T", "P", name="status_enum"), nullable=False)

    masyarakat = db.relationship("Masyarakat", back_populates="human_capital")
