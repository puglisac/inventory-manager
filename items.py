from flask import Blueprint, request, jsonify
from models import Category, Item, Item_Category, db
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity
)

items_blueprint = Blueprint('items_blueprint', __name__)

@items_blueprint.route('/')
@jwt_required
def get_items():
    items=Item.query.all()
    serialized_items=[i.to_dict() for i in items]
    return jsonify({"items": serialized_items})

@items_blueprint.route('/', methods=['POST'])
@jwt_required
def add_item():
    d=request.json
    name = d['name']
    location = d['location']
    description = d['description']
    quantity = d['quantity']
    image_path = d['image_path']
    item=Item(name=name, location=location, description=description, quantity=quantity, image_path=image_path)
    db.session.add(item)
    try: 
        db.session.commit()
        return jsonify({"item": item.to_dict()}), 201
    except: 
        return {'msg':'unable to add item'}, 500

@items_blueprint.route('/<int:item_id>')
@jwt_required
def get_item(item_id):
    item=Item.query.get_or_404(item_id)
    return jsonify({'item': item.to_dict()})

@items_blueprint.route('/<int:item_id>', methods=['PATCH'])
@jwt_required
def update_item(item_id):
    d=request.json
    item=Item.query.get_or_404(item_id)
    for update in d:
        if update != 'id':
            setattr(item, update, d[update])
    db.session.add(item)
    try: 
        db.session.commit()
        updated_item=Item.query.get_or_404(item_id)
        return jsonify({'item': updated_item.to_dict()})
    except:
        return jsonify({'msg': 'unable to edit item'}), 500

@items_blueprint.route('/<int:item_id>', methods=['DELETE'])
@jwt_required
def delete_item(item_id):
    item=Item.query.get_or_404(item_id)
    db.session.delete(item)
    try:
        db.session.commit()
        return jsonify({'msg': 'item successfully deleted'})
    except:
        return jsonify({'msg': 'unable to delete item'}), 500

@items_blueprint.route('/<int:item_id>/add_category', methods=["PATCH"])
@jwt_required
def add_item_to_user(item_id):
    item=Item.query.get_or_404(item_id, description="item not found")
    category = Category.query.get_or_404(request.json['item_id'], description="category not found")
    item.categories.append(category)
    db.session.add(item)
    try: 
        db.session.commit()
        updated_item = Item.query.get_or_404(item_id)
        return jsonify({'item': updated_item.to_dict()})
    except: 
        return {'msg': 'unable to add item'}, 500

@items_blueprint.route('/<int:item_id>/remove_category', methods=["DELETE"])
@jwt_required
def remove_item_from_user(item_id):
    category_to_remove = Item_Category.query.filter(Item_Category.item_id==item_id, Item_Category.category_id==request.json['category_id']).first_or_404(description="category not assigned to item")
    db.session.delete(category_to_remove) 
    try:
        db.session.commit()
        updated_item = Item.query.get_or_404(item_id)
        return jsonify({'item': updated_item.to_dict()})
    except: 
        return {'msg':'unable to remove category'}, 500