from flask import Flask
from users import users_blueprint
from items import items_blueprint
from categories import categories_blueprint
from models import db, connect_db
from flask_jwt_extended import JWTManager, create_access_token
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
jwt = JWTManager(app)

connect_db(app)
app.register_blueprint(users_blueprint, url_prefix="/users")
app.register_blueprint(items_blueprint, url_prefix="/items")
app.register_blueprint(categories_blueprint, url_prefix="/categories")

db.create_all()

@app.route('/')
def index():
    return "in app.py"