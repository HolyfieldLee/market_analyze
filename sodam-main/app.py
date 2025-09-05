import os
from dotenv import load_dotenv
from flask import Flask
from config import Config
from extensions import init_extensions
from routes.core import core_bp
from routes.api import api_bp

load_dotenv()

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    
    app.config.from_object(Config)
    init_extensions(app)

    app.register_blueprint(core_bp)
    app.register_blueprint(api_bp)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
