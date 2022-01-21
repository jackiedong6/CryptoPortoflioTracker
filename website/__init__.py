from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from sqlalchemy import distinct, func
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db = SQLAlchemy()
DB_NAME = "database.db"

ENV = 'prod'

def create_app():
    app = Flask(__name__)
    if ENV == 'dev':
        app.config["SECRET_KEY"] = "hjshjhdjah kjshkjdhjs"
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    else:
         app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://tabpotcraugjre:0af33bb836951750c066cb2595c365520ad2632d50e6263ad72614847bcc09f7@ec2-3-227-15-75.compute-1.amazonaws.com:5432/d9fegdaepi9bn0"
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    from .models import User, Asset

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists("website/" + DB_NAME):
        db.create_all(app=app)
        print("Created Database!")
