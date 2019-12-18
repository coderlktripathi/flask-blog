from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager

app = Flask(__name__)

# app configs
app.config['SECRET_KEY'] = 'f61d941196bb0df7acc2537843547d3045a3e64683dc9a45a8ea98440f71d108'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'

# create SQLAlchemy class instance as db
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

from blog import routes