from server import create_app
from flask_cors import CORS

application = create_app()
CORS(application, resources={r"/*": {"origins": ["https://frontend-web-pelayanan-publik-sktm.vercel.app"]}}, supports_credentials=True)