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
    categories=Category.query.all()
    serialized_categories=[c.to_dict() for c in categories]
    return jsonify({"categories": serialized_categories})

@categories_blueprint.route('/', methods=['POST'])
@jwt_required
def add_category():
    token_user=get_jwt_identity()
    accessing_user = User.query.get_or_404(token_user)
    if accessing_user.is_admin==False:
        return {'msg': 'unauthorized'}, 401

    d=request.json
    name = d['name']
    description = d['description']
    new_category=Category(name=name, description=description)
    db.session.add(new_category)
    try: 
        db.session.commit()
        return jsonify({"category": new_category.to_dict()}), 201
    except: 
        return {'msg':'unable to add category'}, 500

@categories_blueprint.route('/<int:category_id>')
@jwt_required
def get_category(category_id):
    category=Category.query.get_or_404(category_id)
    return jsonify({'category': category.to_dict()})

@categories_blueprint.route('/<int:category_id>', methods=['PATCH'])
@jwt_required
def update_category(category_id):

    token_user=get_jwt_identity()
    accessing_user = User.query.get_or_404(token_user)
    if accessing_user.is_admin==False:
        return {'msg': 'unauthorized'}, 401

    d=request.json
    category=Category.query.get_or_404(category_id)
    for update in d:
        if update != 'id':
            setattr(category, update, d[update])
    db.session.add(category)
    try: 
        db.session.commit()
        updated_category=Category.query.get_or_404(category_id)
        return jsonify({'item': updated_category.to_dict()})
    except:
        return jsonify({'msg': 'unable to edit category'}), 500

@categories_blueprint.route('/<int:category_id>', methods=['DELETE'])
@jwt_required
def delete_category(category_id):

    token_user=get_jwt_identity()
    accessing_user = User.query.get_or_404(token_user)
    if accessing_user.is_admin==False:
        return {'msg': 'unauthorized'}, 401

    category=Category.query.get_or_404(category_id)
    db.session.delete(category)
    try:
        db.session.commit()
        return jsonify({'msg': 'category successfully deleted'})
    except:
        return jsonify({'msg': 'unable to delete category'}), 500

