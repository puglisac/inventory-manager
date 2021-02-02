from flask import Blueprint, request, jsonify
from app import jwt
from models import User
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity
)

users_blueprint = Blueprint('users_blueprint', __name__)

@users_blueprint.route('/login', methods=['POST'])
def index():
    try:
        if User.authenticate(request.json.email, request.json.password):
            access_token = create_access_token(identity=request.json.email)
            return jsonify(access_token=access_token), 200
    except:
        return {"msg":"invalid login"}