from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from models import User, db, Item
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity
)



users_blueprint = Blueprint('users_blueprint', __name__)

@users_blueprint.route('/login', methods=['POST'])
def login():
    # login a user
    try:
        if User.authenticate(request.json['email'], request.json['password']):
            access_token = create_access_token(identity=request.json['email'])
            return jsonify(access_token=access_token)
        else:
            return {"message":"invalid email or password"}, 401
    except:
        return {"message":"invalid login"}, 500

@users_blueprint.route('/signup', methods=['POST'])
@jwt_required
def signup():
    # signup a user requires user to be admin
    
    # check JWT identity is same as email or user is an admin
    token_user=get_jwt_identity()
    accessing_user = User.query.filter_by(email=token_user).first_or_404(description = "user not found")

    # # return unauthorized message if user not authorized
    if accessing_user.is_admin==False:
        return {'message': 'unauthorized'}, 401

    d=request.json

    email=d['email']
    password=d['password']
    first_name=d['first_name']
    last_name=d['last_name']
    is_admin=d['is_admin']
    # create new user and add for commit
    new_user = User.signup(email, password, first_name, last_name, is_admin)
    db.session.add(new_user)
    try:
        # commit new user and return JWT
        db.session.commit()
        new_user=User.query.filter_by(email=email).first_or_404(description="user not found")
        return jsonify({"user": new_user.to_dict()}), 201
    except IntegrityError:
        return {"message":"email already in use"}, 500

@users_blueprint.route('/')
@jwt_required
def get_all_users():
    # get all users

    # check JWT identity is same as email
    token_user=get_jwt_identity()
    accessing_user = User.query.filter_by(email=token_user).first_or_404(description = "user not found")
    if accessing_user.is_admin==False:
        return {'message': 'unauthorized'}, 401
    # get user and return json
    users=User.query.order_by('email').all()
    serialized_users=[u.to_dict() for u in users]
    return jsonify({"users": serialized_users})

@users_blueprint.route('/<email>')
@jwt_required
def get_user(email):
    # get a user by email

    # check JWT identity is same as email or user is an admin
    token_user=get_jwt_identity()
    accessing_user = User.query.filter_by(email=token_user).first_or_404(description = "user not found")
    if email != accessing_user.email and accessing_user.is_admin==False:
        return {'message': 'unauthorized'}, 401
    # get user and return json
    u=User.query.filter_by(email=email).first_or_404(description = "user not found")
    return jsonify({"user": u.to_dict()})

@users_blueprint.route('/<email>', methods=['PATCH'])
@jwt_required
def update_user(email):
    # update a user

    # check JWT identity is same as email or user is an admin
    token_user=get_jwt_identity()
    accessing_user = User.query.filter_by(email=token_user).first_or_404(description = "user not found")

    # return unauthorized message if user not authorized
    if email != accessing_user.email and accessing_user.is_admin==False:
        return {'message': 'unauthorized'}, 401

    # get data from request.json and update user
    d=request.json
    user=User.query.filter_by(email=email).first_or_404(description = "user not found")
    for update in d:
        # don't update id and only update is_admin if accessing_user is admin
        if update != 'id' and update != 'password':
            if update == 'is_admin' and accessing_user.is_admin:
                setattr(user, update, d[update])
            else:
                setattr(user, update, d[update])
            
    db.session.add(user)

    try: 
        # commit to database and return updated user
        db.session.commit()
        updated_user=User.query.get_or_404(user.id, description = "user not found")
        return jsonify({'user': updated_user.to_dict()})
    except IntegrityError:
        return jsonify({'message': 'Email already in use'}), 500
    except:  
        return jsonify({'message': 'unable to edit user'}), 500

@users_blueprint.route('/<email>/change_password', methods=['PATCH'])
@jwt_required
def changePassword(email):
    # check JWT identity is same as email or user is an admin
    token_user=get_jwt_identity()
    accessing_user = User.query.filter_by(email=token_user).first_or_404(description = "user not found")

    # return unauthorized message if user not authorized
    if email != accessing_user.email:
        return {'message': 'unauthorized'}, 401
    existing_password=request.json['existing_password']
    new_password=request.json['new_password']
    if User.authenticate(email, existing_password):
        accessing_user.changePassword(new_password)
        db.session.add(accessing_user)
        try:
            db.session.commit()
            updated_user=User.query.get_or_404(accessing_user.id, description = "user not found")
            return jsonify({'user': updated_user.to_dict()})
        except:
            return jsonify({'message': 'unable to change password'}), 500
    else:
        return jsonify({'message': 'incorrect password'}), 400



@users_blueprint.route('/<email>', methods=['DELETE'])
@jwt_required
def delete_user(email):
    # delete a user

    # check JWT identity is same as email or user is an admin
    token_user=get_jwt_identity()
    accessing_user = User.query.filter_by(email=token_user).first_or_404(description = "user not found")

    # return unauthorized message if user not authorized
    if email != accessing_user.email and accessing_user.is_admin==False:
        return {'message': 'unauthorized'}, 401
    
    # find and delete user
    user=User.query.filter_by(email=email).first_or_404(description = "user not found")
    db.session.delete(user)
    try:
        # commit and return success message
        db.session.commit()
        return jsonify({'message': 'user successfully deleted'})
    except:
        return jsonify({'message': 'unable to delete user'}), 500

@users_blueprint.route('/<email>/add_item', methods=["PATCH"])
@jwt_required
def add_item_to_user(email):
    # add an item to a user's pull list

    # check JWT identity is same as email
    user=User.query.filter_by(email=email).first_or_404(description = "user not found")
    token_user=get_jwt_identity()

    # return unauthorized message if user not authorized
    if email != token_user:
        return {'message': 'unauthorized'}, 401

    # get item and append to pull list
    item = Item.query.get_or_404(request.json['item_id'], description="item not found")
   
    user.pull_list.append(item)
    db.session.add(user)
    try: 
        # commit to db and return updated user
        db.session.commit()
        updated_user = User.query.filter_by(email=email).first_or_404(description = "user not found")
        return jsonify({'user': updated_user.to_dict()})
    except: 
        return {'message': 'unable to add item'}, 500

@users_blueprint.route('/<email>/remove_item', methods=["PATCH"])
@jwt_required
def remove_item_from_user(email):
    # remove item from user's pull list. requires requestor to be admin

 # check JWT identity is same as email or user is an admin
    token_user=get_jwt_identity()
    accessing_user = User.query.filter_by(email=token_user).first_or_404(description = "user not found")

    # return unauthorized message if user not authorized
    if accessing_user.is_admin==False:
        return {'message': 'unauthorized'}, 401
    if request.json['item_id']=="all":
        user=User.query.filter_by(email=email).first_or_404(description = "user not found")
        user.pull_list=[]
        db.session.add(user)
    # get item and delete from session
    else:
        item_to_remove = Item.query.get_or_404(request.json['item_id'],description="item not found in pull_list")
        item_to_remove.user_id=None
        db.session.add(item_to_remove) 
    try:
        # commit to db and return updated user
        db.session.commit()
        updated_user = User.query.filter_by(email=email).first_or_404(description = "user not found")
        return jsonify({'user': updated_user.to_dict()})
    except: 
        return {'message':'unable to remove item'}, 500