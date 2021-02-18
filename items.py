from flask import Blueprint, request, jsonify
from sqlalchemy import func
from models import Category, Item, Item_Category, User, db
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity
)

items_blueprint = Blueprint('items_blueprint', __name__)

@items_blueprint.route('/')
@jwt_required
def get_items():
    # get all items. can accept array of category_ids in query string to filter by categories
    if request.args:
        category_arr = request.args['category_id'].split(",")
        items = Item.query.join(Item.categories).filter(
            Item.categories.any(Category.id.in_(category_arr))
            ).group_by(Item.id).having(
            func.count(Category.name) >= len(category_arr))
    else: 
        items=Item.query.all()
    serialized_items=[i.to_dict() for i in items]
    return jsonify({"items": serialized_items})

@items_blueprint.route('/', methods=['POST'])
@jwt_required
def add_item():
    # add item. requires user to be an admin

    # check JWT identity and return unauthorized message if user not authorized
    token_user=get_jwt_identity()
    accessing_user = User.query.filter_by(email=token_user).first_or_404()
    if accessing_user.is_admin==False:
        return {'message': 'unauthorized'}, 401

    # get data from request and create new item
    d=request.json
    name = d['name']
    location = d['location']
    description = d['description']
    quantity = d['quantity']
    image_path = d['image_path']
    category_ids = d['categories']
    
    # add category ids to item
    categories_arr=[]
    for id in category_ids:
        category = Category.query.get_or_404(id, description="category not found")
        categories_arr.append(category)
    
    item=Item(name=name, 
                location=location, 
                description=description, 
                quantity=quantity, 
                image_path=image_path,
                categories=categories_arr)

    db.session.add(item)
    try: 
        # commit to db and return new item
        db.session.commit()
        return jsonify({"item": item.to_dict()}), 201
    except: 
        return {'message':'unable to add item'}, 500

@items_blueprint.route('/<int:item_id>')
@jwt_required
def get_item(item_id):
    # get item by id
    item=Item.query.get_or_404(item_id, description="item not found")
    return jsonify({'item': item.to_dict()})

@items_blueprint.route('/<int:item_id>', methods=['PATCH'])
@jwt_required
def update_item(item_id):
    # update an item. requires user to be an admin

    # check JWT identity and return unauthorized message if user not authorized
    token_user=get_jwt_identity()
    accessing_user = User.query.filter_by(email=token_user).first_or_404()
    if accessing_user.is_admin==False:
        return {'message': 'unauthorized'}, 401

    # get data from request and update item
    d=request.json
    item=Item.query.get_or_404(item_id, description = "item not found")
    for update in d:
        # don't update id
        if update != 'id' and update != 'categories':
            setattr(item, update, d[update])

    # update category ids
    if(request.json['categories']):
        category_ids = request.json['categories']
        categories_arr=[]
        for id in category_ids:
            category = Category.query.get_or_404(id, description="category not found")
            categories_arr.append(category)
            
        item.categories=categories_arr
    
    db.session.add(item)
    try: 
        # commit to db and return updated item
        db.session.commit()
        updated_item=Item.query.get_or_404(item_id)
        return jsonify({'item': updated_item.to_dict()})
    except:
        return jsonify({'message': 'unable to edit item'}), 500

@items_blueprint.route('/<int:item_id>', methods=['DELETE'])
@jwt_required
def delete_item(item_id):
    # delete an item. requires user to be admin

    # check JWT identity and return unauthorized message if user not authorized
    token_user=get_jwt_identity()
    accessing_user = User.query.filter_by(email=token_user).first_or_404()
    if accessing_user.is_admin==False:
        return {'message': 'unauthorized'}, 401

    # get item and delete
    item=Item.query.get_or_404(item_id)
    db.session.delete(item)
    try:
        # commit to db and return success message
        db.session.commit()
        return jsonify({'message': 'item successfully deleted'})
    except:
        return jsonify({'message': 'unable to delete item'}), 500

@items_blueprint.route('/<int:item_id>/add_category', methods=["PATCH"])
@jwt_required
def add_category_to_item(item_id):
    # adds category tag to item. requires user to be admin
    

    # check JWT identity and return unauthorized message if user not authorized
    token_user=get_jwt_identity()
    accessing_user = User.query.filter_by(email=token_user).first_or_404()
    if accessing_user.is_admin==False:
        return {'message': 'unauthorized'}, 401

    # get item and categories and set array of categories to items.categories
    item=Item.query.get_or_404(item_id, description="item not found")
    

    category_to_add = Category.query.get_or_404(request.json['category_id'], description="category not found")

    item.categories.append(category_to_add)
    db.session.add(item)
    try: 
        # commit to db and return item
        db.session.commit()
        updated_item = Item.query.get_or_404(item_id)
        return jsonify({'item': updated_item.to_dict()})
    except: 
        return {'message': 'unable to add item'}, 500

@items_blueprint.route('/<int:item_id>/remove_category', methods=["DELETE"])
@jwt_required
def remove_category_from_item(item_id):
    # remove category tag from item. requires user to be an admin

    # check JWT identity and return unauthorized message if user not authorized
    token_user=get_jwt_identity()
    accessing_user = User.query.filter_by(email=token_user).first_or_404()
    if accessing_user.is_admin==False:
        return {'message': 'unauthorized'}, 401

    # remove relationship
    category_to_remove = Item_Category.query.filter(Item_Category.item_id==item_id, Item_Category.category_id==request.json['category_id']).first_or_404(description="category not assigned to item")
    db.session.delete(category_to_remove) 
    try:
        # commit to db and return item
        db.session.commit()
        updated_item = Item.query.get_or_404(item_id)
        return jsonify({'item': updated_item.to_dict()})
    except: 
        return {'message':'unable to remove category'}, 500