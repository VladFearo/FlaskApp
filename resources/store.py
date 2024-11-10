import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import abort, Blueprint
from schemas import StoreSchema
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from models import StoreModel
from db import db


blp = Blueprint("stores", __name__, description="Store operations")

@blp.route("/store/<string:store_id>")
class Store(MethodView):
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        try:
            return stores[store_id]
        except KeyError:
            abort(404, message="Store not found.")

    def delete(self, store_id):
        try:
            del stores[store_id]
            return {"message": "Store deleted."}
        except KeyError:
            abort(404, message="Store not found.")



@blp.route("/store")
class StoreList(MethodView):
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        return stores.values()

    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, store_data):
        store = StoreModel(**store_data)
        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(400, message="A store with the same name already exists.")
        except SQLAlchemyError:
            abort(500, message="An error occurred while adding the store to the database.")
        

        return store