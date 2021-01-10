from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql
from os import environ
from theangryshopper import config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.alchemy_configuration
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from theangryshopper import routes