from flask import Blueprint, request, jsonify
from models import Category, User, db
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity
)

categories_blueprint = Blueprint('categories_blueprint', __name__)

@categories_blueprint.route('/')
@jwt_required
def get_categories():
    # get all categories

    categories=Category.query.all()
    serialized_categories=[c.to_dict() for c in categories]
    return jsonify({"categories": serialized_categories})

@categories_blueprint.route('/', methods=['POST'])
@jwt_required
def add_category():
    # add a category. requires user to be admin

    # check JWT identity and return unauthorized message if user not authorized
    token_user=get_jwt_identity()
    accessing_user = User.query.get_or_404(token_user)
    if accessing_user.is_admin==False:
        return {'message': 'unauthorized'}, 401

    # get data from request and create new category
    d=request.json
    name = d['name']
    description = d['description']
    new_category=Category(name=name, description=description)
    db.session.add(new_category)
    try: 
        # commit to db and return new category
        db.session.commit()
        return jsonify({"category": new_category.to_dict()}), 201
    except: 
        return {'message':'unable to add category'}, 500

@categories_blueprint.route('/<int:category_id>')
@jwt_required
def get_category(category_id):
    # get category by id
    category=Category.query.get_or_404(category_id, description = "category not")
    return jsonify({'category': category.to_dict()})

@categories_blueprint.route('/<int:category_id>', methods=['PATCH'])
@jwt_required
def update_category(category_id):
    # update a category. requires user to be admin

    # check JWT identity and return unauthorized message if user not authorized
    token_user=get_jwt_identity()
    accessing_user = User.query.get_or_404(token_user)
    if accessing_user.is_admin==False:
        return {'message': 'unauthorized'}, 401

    # get data form request and update the category
    d=request.json
    category=Category.query.get_or_404(category_id)
    for update in d:
        # don't update the id
        if update != 'id':
            setattr(category, update, d[update])
    db.session.add(category)
    try:
        # commit to the db and return updated category 
        db.session.commit()
        updated_category=Category.query.get_or_404(category_id, description = "category not found")
        return jsonify({'item': updated_category.to_dict()})
    except:
        return jsonify({'message': 'unable to edit category'}), 500

@categories_blueprint.route('/<int:category_id>', methods=['DELETE'])
@jwt_required
def delete_category(category_id):
    # delete a category. requires user to be an admin

    # check JWT identity and return unauthorized message if user not authorized
    token_user=get_jwt_identity()
    accessing_user = User.query.get_or_404(token_user)
    if accessing_user.is_admin==False:
        return {'message': 'unauthorized'}, 401

    # get category and delete
    category=Category.query.get_or_404(category_id, description = "category not found")
    db.session.delete(category)
    try:
        # commit to db and return success message
        db.session.commit()
        return jsonify({'message': 'category successfully deleted'})
    except:
        return jsonify({'message': 'unable to delete category'}), 500

