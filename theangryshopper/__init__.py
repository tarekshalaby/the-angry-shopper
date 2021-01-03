from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from theangryshopper.db_config import alchemy_configuration 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = alchemy_configuration
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from theangryshopper import routes