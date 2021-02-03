from flask import Blueprint, request, jsonify
from models import User
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity
)

users_blueprint = Blueprint('users_blueprint', __name__)

@users_blueprint.route('/login', methods=['POST'])
def login():
    try:
        if User.authenticate(request.json['email'], request.json['password']):
            access_token = create_access_token(identity=request.json['email'])
            return jsonify(access_token=access_token)
    except:
        return {"msg":"invalid login"}

@users_blueprint.route('/signup', methods=['POST'])
def signup():
    d=request.json

    email=d['email']
    password=d['password']
    first_name=d['first_name']
    last_name=d['last_name']

    try:
        User.signup(email, password, first_name, last_name)
        access_token = create_access_token(identity=request.json['email'])
        return jsonify(access_token=access_token)
    except:
        return {"msg":"invalid signup"}

@users_blueprint.route('/')
@jwt_required
def get_user():
    email=get_jwt_identity()
    u=User.query.get_or_404(email)
    # need to get password out of user when returning
    return jsonify({"user": u.to_dict(rules=('-password'))})