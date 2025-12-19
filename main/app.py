import os
from flask import Flask, session

app = Flask(
    __name__,
    static_folder='static')

app.secret_key = os.environ.get('SECRET_KEY', 'SECRET_KEY')

# setup configs
env = os.environ.get('FLASK_ENV', 'development')

app.config['ENV'] = env
app.config.from_pyfile(f'config/{env}.cfg')

# CSRF protection
from flask_wtf.csrf import CSRFProtect
csrf_protect = CSRFProtect(app)

# Database
from flask_sqlalchemy import SQLAlchemy
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.config['SECURITY_REGISTERABLE'] = True

from flask_sslify import SSLify
ssl = SSLify(app)
app.config['WTF_CSRF_ENABLED'] = False
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from flask_minify import Minify
minify = Minify(app=app, passive=True)