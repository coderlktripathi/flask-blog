from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

from awesomeblog.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
moment = Moment()
mail = Mail()
login_manager = LoginManager()
login_manager.login_view = "users.login"
login_manager.login_message_category = "info"


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    moment.init_app(app)

    from awesomeblog.users.routes import users
    from awesomeblog.posts.routes import posts
    from awesomeblog.main.routes import main
    from awesomeblog.messages.routes import msgs

    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(msgs)
    app.register_blueprint(main)

    return app
