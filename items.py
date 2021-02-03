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

    db.session.commit()
    return jsonify({"item": item.to_dict()})
    # except: 
    #     return {'msg':'unable to add item'}