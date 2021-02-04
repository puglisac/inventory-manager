from flask import Blueprint, request, jsonify
from models import User, db, Item, Pull_List
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

@users_blueprint.route('/<email>')
@jwt_required
def get_user(email):
    token_user=get_jwt_identity()
    if email != token_user:
        return {'msg': 'unauthorized'}, 401
    u=User.query.get_or_404(email)
    return jsonify({"user": u.to_dict()})

@users_blueprint.route('/<email>', methods=['PATCH'])
@jwt_required
def update_user(email):
    token_user=get_jwt_identity()
    if email != token_user:
        return {'msg': 'unauthorized'}, 401
    d=request.json
    user=User.query.get_or_404(email)
    for update in d:
        if update != 'id':
            setattr(user, update, d[update])
    db.session.add(user)
    try: 
        db.session.commit()
        updated_user=User.query.get_or_404(email)
        return jsonify({'user': updated_user.to_dict()})
    except:
        return jsonify({'msg': 'unable to edit user'})

@users_blueprint.route('/<email>', methods=['DELETE'])
@jwt_required
def delete_user(email):
    user=User.query.get_or_404(email)
    db.session.delete(user)
    try:
        db.session.commit()
        return jsonify({'msg': 'user successfully deleted'})
    except:
        return jsonify({'msg': 'unable to delete user'})

@users_blueprint.route('/<email>/add_item', methods=["PATCH"])
@jwt_required
def add_item_to_user(email):
    user=User.query.get_or_404(email)
    token_user=get_jwt_identity()
    if email != token_user:
        return {'msg': 'unauthorized'}, 401
    item = Item.query.get_or_404(request.json['item_id'])
    user.pull_list.append(item)
    db.session.add(user)
    db.session.commit()
    updated_user = User.query.get_or_404(email)
    return jsonify({'user': updated_user.to_dict()})

@users_blueprint.route('/<email>/remove_item', methods=["DELETE"])
@jwt_required
def remove_item_from_user(email):
    user=User.query.get_or_404(email)
    token_user=get_jwt_identity()
    if email != token_user:
        return {'msg': 'unauthorized'}, 401
    item_to_remove = Pull_List.query.filter(Pull_List.user_id==email, Pull_List.item_id==request.json['item_id']).first_or_404()
    db.session.delete(item_to_remove)
    db.session.commit()
    updated_user = User.query.get_or_404(email)
    return jsonify({'user': updated_user.to_dict()})