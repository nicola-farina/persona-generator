from flask import request, url_for
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from web.utils import abort_if_not_authorized
from web.api.app import db_connection
from src.common.models.brand import Brand
from src.common.database.brands import BrandsDatabase


def brand_to_api_repr(brand: Brand) -> dict:
    return {
       "brand_id": brand.brand_id,
       "name": brand.name,
       "_links": {
           "self": url_for("api.brand", brand_id=brand.brand_id)
       }
    }


class Brands(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        try:
            # Create brand
            name = data["name"]
            brand = Brand(name=name, account_id=get_jwt_identity())
            # Save it in DB
            db = BrandsDatabase(connection=db_connection)
            db.save_brand(brand)
            # Return a response
            return brand_to_api_repr(brand), 201
        except KeyError:
            return {"message": "Error, some keys are missing"}, 400

    @jwt_required()
    def get(self):
        args = request.args
        account_id = args.get("account_id")
        db = BrandsDatabase(db_connection)
        if account_id:
            abort_if_not_authorized(account_id)
            brands = db.get_brands_of_account(account_id)
            brands = [brand_to_api_repr(brand) for brand in brands]
            return brands, 200
        else:
            brands = db.get_all_brands()
            brands = [brand_to_api_repr(brand) for brand in brands]
            return brands, 200


class BrandsID(Resource):
    @jwt_required()
    def get(self, brand_id):
        # Check in DB
        db = BrandsDatabase(connection=db_connection)
        brand = db.get_brand_by_id(brand_id)

        if brand is None:
            return {"message": "Error, brand not found"}, 404

        abort_if_not_authorized(brand.account_id)
        return brand_to_api_repr(brand), 201

    @jwt_required()
    def delete(self, brand_id):
        # Check in DB
        db = BrandsDatabase(connection=db_connection)
        brand = db.get_brand_by_id(brand_id)

        if brand is None:
            return {"message": "Error, brand not found"}, 404

        abort_if_not_authorized(brand.account_id)
        # Delete from DB
        db.delete_brand_by_id(brand_id, brand.account_id)

        return {}, 204
