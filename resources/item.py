import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import abort, Blueprint
from db import items


blp = Blueprint("items", __name__, description="Item operations")

@blp.route("/item/<string:item_id>")
class Item(MethodView):
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
    
    def put(self, item_id):
        item_data = request.get_json()
        if "price" not in item_data or "name" not in item_data:
            abort(400, message="Missing required fields (name or price).")
        try:
            item = items[item_id]
            item |= item_data # merge dictionaries to update item
            
            return item
        except KeyError:
            abort(404, message="Item not found.")
        

@blp.route("/item")
class ItemList(MethodView):
    def get(self):
        return {"items": list(items.values())}

    def post(self):
        item_data = request.get_json()
        if(
            "name" not in item_data or
            "price" not in item_data or
            "store_id" not in item_data
        ):
            abort(400, message="Missing required fields (name price or store id).")
        for item in items.values():
            if(
            item_data["name"] == item["name"]
            and item_data["store_id"] == item["store_id"]
            ):
                abort(400, message="Item already exists.")

        item_id = uuid.uuid4().hex
        item = { **item_data, "id": item_id }
        items[item_id] = item
        return item, 201