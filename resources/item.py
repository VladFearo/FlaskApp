import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import abort, Blueprint
from sqlalchemy.exc import SQLAlchemyError

from db import db
from schemas import ItemSchema, ItemUpdateSchema
from models import ItemModel


blp = Blueprint("items", __name__, description="Item operations")

@blp.route("/item/<string:item_id>")
class Item(MethodView):
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        try:
            return items[item_id]
        except KeyError:
            abort(404, message="Item not found.")

    def delete(self, item_id):
        try:
            del items[item_id]
            return {"message": "Item deleted."}
        except KeyError:
            abort(404, message="Item not found.")
    
    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemSchema)
    def put(self,item_data, item_id):
        try:
            item = items[item_id]
            item |= item_data # merge dictionaries to update item
            
            return item
        except KeyError:
            abort(404, message="Item not found.")
        

@blp.route("/item")
class ItemList(MethodView):
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        return items.values()

    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, item_data):
        item = ItemModel(**item_data)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while adding the item to the database.")
        

        return item