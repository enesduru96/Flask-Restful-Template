from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
jwt = JWTManager()
api = Api()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__, template_folder="../templates")

    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config.from_object("app.config.Config")

    db.init_app(app)
    jwt.init_app(app)
    api.init_app(app)
    csrf.init_app(app)

    with app.app_context():
        from .models import User
        db.create_all()
        
        from .routes.auth import auth_bp
        from .routes.home import home_bp
        app.register_blueprint(auth_bp)
        app.register_blueprint(home_bp)

    return app