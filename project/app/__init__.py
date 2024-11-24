from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import os

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__, static_folder="media")
    app.config.from_object("config.Config")

    # Ensure the upload folder exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)

    # Register routes
    from app.routes import auth_routes, profile_routes, upload_routes
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(profile_routes.bp)
    app.register_blueprint(upload_routes.bp)

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    return app

