from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from elasticsearch import Elasticsearch

from awesomeblog.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
moment = Moment()
mail = Mail()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    moment.init_app(app)

    app.elasticsearch = (
        Elasticsearch([app.config['ELASTICSEARCH_URL']])
        if app.config.get('ELASTICSEARCH_URL')
        else None
    )

    from awesomeblog.users.routes import users
    from awesomeblog.posts.routes import posts
    from awesomeblog.main.routes import main
    from awesomeblog.messages.routes import msgs
    from awesomeblog.errors.handlers import errors

    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(msgs)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app

from awesomeblog import models