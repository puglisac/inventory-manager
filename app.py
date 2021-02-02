from flask import Flask
from users.users import users_blueprint
from models import db, connect_db
from flask_jwt_extended import JWTManager

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///technology_advice'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "kiujytrfd56"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['JWT_SECRET_KEY'] = 'asdfgtey56wy4etrafds'
jwt = JWTManager(app)

connect_db(app)
app.register_blueprint(users_blueprint, url_prefix="/users")

@app.route('/')
def index():
    return "in app.py"