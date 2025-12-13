from flask import Flask
from config import Config
from extension import db, migrate
from sqlalchemy import text
from dotenv import load_dotenv
from utils.auth import init_jwt


def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    # Load environment variables from .env
    load_dotenv()
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    from extension import ma
    ma.init_app(app)
    init_jwt(app)

    with app.app_context():
        import models  
        from routes.authRoutes import auth_bp
        app.register_blueprint(auth_bp)
        try:
            db.session.execute(text("SELECT 1 "))
            print("Database Connected")
        except Exception as e:
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
if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=5000, debug=True)
