import os
from flask import Flask
from app.models import db, User
from app.routes.auth import auth_bp
from app.routes.admin import admin_bp
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv


load_dotenv()

def create_app():
    app=Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS") == "True"
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    login_manager = LoginManager()
    login_manager.init_app(app)

    login_manager.login_view = "auth_bp.login"  # route name
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))



    db.init_app(app)
    with app.app_context():
        db.create_all()
        User.make_admin()
    
    return app