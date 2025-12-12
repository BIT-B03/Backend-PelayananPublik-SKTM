import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL","mysql+pymysql://420812_pelayanan:PelayananPublik_123@mysql-ramadhanreal.alwaysdata.net:3306/ramadhanreal_pelayananpublik",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
