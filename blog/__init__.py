from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask_mail import Mail
from flask_migrate import Migrate

from flask_login import LoginManager

app = Flask(__name__)

# app configs
app.config[
    "SECRET_KEY"
] = "f61d941196bb0df7acc2537843547d3045a3e64683dc9a45a8ea98440f71d108"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
app.config["MAIL_SERVER"] = "smtp.googlemail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "gyanp7987@gmail.com"
app.config["MAIL_PASSWORD"] = ""

# create SQLAlchemy class instance as db
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
moment = Moment(app)
mail = Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

from blog import routes
