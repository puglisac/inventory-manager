from flask import Blueprint

users_blueprint = Blueprint('users_blueprint', __name__, url_prefix="/users")

@users_blueprint.route('/')
def index():
    return "This is in the users"