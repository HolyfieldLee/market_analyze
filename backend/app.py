"""
from flask import Flask
from .config import Config
from .extensions import db, migrate, bcrypt, jwt, cors
from .blueprints.auth import auth_bp
from .blueprints.recs import recs_bp
from .blueprints.api import api_bp
import os

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # Ensure instance directory exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass
    print(">>> SQLALCHEMY_DATABASE_URI =", app.config["SQLALCHEMY_DATABASE_URI"])

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # Blueprints
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(recs_bp, url_prefix="/api/recs")

    # Create tables on first run (for quick start)
    with app.app_context():
        from . import models  # noqa: F401
        db.create_all()

    return app
"""
# backend/app.py
from flask import Flask
from .config import Config
from .extensions import db, migrate, bcrypt, jwt, cors
from .blueprints.auth import auth_bp
from .blueprints.recs import recs_bp
from .blueprints.api import api_bp
import os

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # instance 디렉토리 보장
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # 확장 초기화
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={
        r"/api/*": {"origins": "*"}  # 필요시 iOS 도메인/포트로 제한
    })

    # 블루프린트 등록 (모두 /api/v1로 네임스페이스)
    app.register_blueprint(api_bp,  url_prefix="/api/v1")
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(recs_bp, url_prefix="/api/v1/recs")

    return app

