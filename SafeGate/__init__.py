from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app= Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///studentUser.db'
app.config['SECRET_KEY']='08cdf60452563aa74bbc4943'
db=SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
from SafeGate import routes
from SafeGate import models





