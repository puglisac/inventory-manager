from flask import Blueprint, request, jsonify
from models import Item, db
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
        return jsonify({"item": item.to_dict()})
    except: 
        return {'msg':'unable to add item'}

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
    db.session.commit()
    updated_item=Item.query.get_or_404(item_id)
    return jsonify({'item': updated_item.to_dict()})

# @items_blueprint.route('/<int:item_id>', methods=['PATCH'])
# @jwt_required
# def update_item(item_id):
#     d=request.json
#     item=Item.query.get_or_404(item_id)
#     for update in d:
#         if update != 'id':
#             setattr(item, update, d[update])
#     db.session.add(item)
#     db.session.commit()
#     updated_item=Item.query.get_or_404(item_id)
#     return jsonify({'item': updated_item.to_dict()})