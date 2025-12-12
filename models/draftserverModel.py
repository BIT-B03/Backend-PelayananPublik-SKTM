from sqlalchemy.dialects.mysql import JSON as MySQLJSON
from extension import db


class DraftServer(db.Model):
    __tablename__ = "draft_server"

    id_draft_server = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nik = db.Column(db.Integer, db.ForeignKey("masyarakat.nik"), nullable=False)
    checksum = db.Column(db.String(255))
    serverVersion = db.Column(db.Integer)
    last_edit = db.Column(db.DateTime)
    status = db.Column(db.Enum("B", "T", "P", name="status_enum"), nullable=False)
    data_json = db.Column(MySQLJSON)

    masyarakat = db.relationship("Masyarakat", back_populates="draft_server")
