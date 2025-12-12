from extension import db


class KTP(db.Model):
    __tablename__ = "ktp"

    id_ktp = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nik = db.Column(db.Integer, db.ForeignKey("masyarakat.nik"), nullable=False, unique=True)
    tempat_lahir = db.Column(db.String(255))
    tanggal_lahir = db.Column(db.Date)
    alamat = db.Column(db.Text)
    foto_ktp = db.Column(db.String(255))
    foto_surat_pengantar_rt_rw = db.Column(db.String(255))
    status = db.Column(db.Enum("B", "T", "P", name="status_enum"), nullable=False)

    masyarakat = db.relationship("Masyarakat", back_populates="ktp")
