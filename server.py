from dotenv import load_dotenv
load_dotenv()  # WAJIB di paling atas sebelum import Config

from flask import Flask
from config import Config
from extension import db, migrate
from sqlalchemy import text
from utils.auth import init_jwt
from flask_cors import CORS


def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__)

    # Load config dari class Config (env sudah siap)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from extension import ma
    ma.init_app(app)

    init_jwt(app)
    CORS(app, resources={r"/*": {"origins": ["https://frontend-web-pelayanan-publik-sktm.vercel.app"]}}, supports_credentials=True)

    with app.app_context():
        import models
        from routes.authRoutes import auth_bp
        from routes.userRoutes import user_bp
        from routes.adminRoutes import admin_bp
        from routes.supabaseSignedRoutes import supabase_bp

        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(user_bp, url_prefix='/api/user')
        app.register_blueprint(admin_bp, url_prefix='/api/admin')
        app.register_blueprint(supabase_bp, url_prefix='/api')

        try:
            db.session.execute(text("SELECT 1 "))
            print("Database Connected")
        except Exception:
            print("Database Unconnected")

        try:
            from utils.supabase_client import test_connection
            if test_connection():
                print("Supabase Connected")
            else:
                print("Supabase Unconnected")
        except Exception:
            print("Supabase Unconnected")

    return app
