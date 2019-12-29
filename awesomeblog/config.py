import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'f61d941196bb0df7acc2537843547d3045a3e64683dc9a45a8ea98440f71d108'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'awesomeblog.db')
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'gyanp7987@gmail.com'
    MAIL_PASSWORD = ''
    ELASTICSEARCH_URL = 'http://localhost:9200'
    POSTS_PER_PAGE = 5