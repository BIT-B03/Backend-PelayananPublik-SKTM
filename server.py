from flask import Flask
from config import Config
from extension import db, migrate
from sqlalchemy import text
from dotenv import load_dotenv


def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    # Load environment variables from .env
    load_dotenv()
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        import models  
        try:
            db.session.execute(text("SELECT 1 "))
            print("Database Connected")
        except Exception as e:
            print("Database Unconnected")
    return app
if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=5000, debug=True)
