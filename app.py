from flask import Flask
from users.users import users_blueprint
from models import db, connect_db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///technology_advice'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "90283urhjoijodifj9834"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
app.register_blueprint(users_blueprint)

@app.route('/')
def index():
    return "in app.py"