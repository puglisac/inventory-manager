from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
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
        return {"msg":"invalid login"}, 500

@users_blueprint.route('/signup', methods=['POST'])
@jwt_required
def signup():
    token_user=get_jwt_identity()
    accessing_user = User.query.get_or_404(token_user)
    if accessing_user.is_admin==False:
        return {'msg': 'unauthorized'}, 401
    d=request.json

    email=d['email']
    password=d['password']
    first_name=d['first_name']
    last_name=d['last_name']

    new_user = User.signup(email, password, first_name, last_name)
    db.session.add(new_user)
    try:
        db.session.commit()
        access_token = create_access_token(identity=request.json['email'])
        return jsonify(access_token=access_token), 201
    except IntegrityError:
        return {"msg":"email already in use"}, 500

@users_blueprint.route('/<email>')
@jwt_required
def get_user(email):
    token_user=get_jwt_identity()
    accessing_user = User.query.get_or_404(token_user)
    if email != accessing_user.email or accessing_user.is_admin==False:
        return {'msg': 'unauthorized'}, 401
    u=User.query.get_or_404(email, description="user not found")
    return jsonify({"user": u.to_dict()})

@users_blueprint.route('/<email>', methods=['PATCH'])
@jwt_required
def update_user(email):
    token_user=get_jwt_identity()
    accessing_user = User.query.get_or_404(token_user)
    if email != accessing_user.email or accessing_user.is_admin==False:
        return {'msg': 'unauthorized'}, 401
    d=request.json
    user=User.query.get_or_404(email, description="user not found")
    for update in d:
        if update != 'id':
            setattr(user, update, d[update])
    db.session.add(user)
    try: 
        db.session.commit()
        updated_user=User.query.get_or_404(email)
        return jsonify({'user': updated_user.to_dict()})
    except:
        return jsonify({'msg': 'unable to edit user'}), 500

@users_blueprint.route('/<email>', methods=['DELETE'])
@jwt_required
def delete_user(email):
    token_user=get_jwt_identity()
    accessing_user = User.query.get_or_404(token_user)
    if email != accessing_user.email or accessing_user.is_admin==False:
        return {'msg': 'unauthorized'}, 401
    user=User.query.get_or_404(email, description="user not found")
    db.session.delete(user)
    try:
        db.session.commit()
        return jsonify({'msg': 'user successfully deleted'})
    except:
        return jsonify({'msg': 'unable to delete user'}), 500

@users_blueprint.route('/<email>/add_item', methods=["PATCH"])
@jwt_required
def add_item_to_user(email):
    user=User.query.get_or_404(email, description="user not found")
    token_user=get_jwt_identity()
    if email != token_user:
        return {'msg': 'unauthorized'}, 401
    item = Item.query.get_or_404(request.json['item_id'])
    user.pull_list.append(item)
    db.session.add(user)
    try: 
        db.session.commit()
        updated_user = User.query.get_or_404(email)
        return jsonify({'user': updated_user.to_dict()})
    except: 
        return {'msg': 'unable to add item'}, 500

@users_blueprint.route('/<email>/remove_item', methods=["DELETE"])
@jwt_required
def remove_item_from_user(email):
    token_user=get_jwt_identity()
    if email != token_user:
        return {'msg': 'unauthorized'}, 401
    item_to_remove = Pull_List.query.filter(Pull_List.user_id==email, Pull_List.item_id==request.json['item_id']).first_or_404(description="item not found in pull_list")
    db.session.delete(item_to_remove) 
    try:
        db.session.commit()
        updated_user = User.query.get_or_404(email)
        return jsonify({'user': updated_user.to_dict()})
    except: 
        return {'msg':'unable to remove item'}, 500