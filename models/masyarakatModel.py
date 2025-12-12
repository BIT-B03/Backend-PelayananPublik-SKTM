from extension import db


class Masyarakat(db.Model):
	__tablename__ = "masyarakat"

	nik = db.Column(db.Integer, primary_key=True, nullable=False)
	nama = db.Column(db.String(255))
	jenis_kelamin = db.Column(db.Enum('L', 'P', name='jenis_kelamin_enum'), nullable=False)
	email = db.Column(db.String(255))
	nomor_hp = db.Column(db.String(15))
	password = db.Column(db.String(255))

	ktp = db.relationship("KTP", uselist=False, back_populates="masyarakat", cascade="all, delete-orphan")
	human_capital = db.relationship(
		"HumanCapital", uselist=False, back_populates="masyarakat", cascade="all, delete-orphan"
	)
	kondisi_rumah = db.relationship(
		"KondisiRumah", uselist=False, back_populates="masyarakat", cascade="all, delete-orphan"
	)
	kondisi_ekonomi = db.relationship(
		"KondisiEkonomi", uselist=False, back_populates="masyarakat", cascade="all, delete-orphan"
	)
	aset_non_financial = db.relationship(
		"AsetNonFinancial", uselist=False, back_populates="masyarakat", cascade="all, delete-orphan"
	)
	kartu_keluarga = db.relationship(
		"KartuKeluarga", back_populates="masyarakat", cascade="all, delete-orphan"
	)
	petugas = db.relationship("Petugas", back_populates="masyarakat", cascade="all, delete-orphan")
	draft_server = db.relationship(
		"DraftServer", back_populates="masyarakat", cascade="all, delete-orphan"
	)

