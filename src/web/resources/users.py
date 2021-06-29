import json

from flask import request, url_for
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
import paho.mqtt.client as mqtt

from web.common.utils import abort_if_not_authorized
from web.api.app import db_connection
from src.common.models.user import User
from src.common.models.sources.twitter import TwitterDataSource
from src.common.database.users import UsersDatabase
from src.common.database.brands import BrandsDatabase
from src.common.database.sources import SourcesDatabase


def user_to_api_repr(user: User, attributes: bool = False) -> dict:
    dct = {
       "user_id": user.user_id,
       "data_sources": user.data_sources
    }
    if attributes:
        dct["attributes"] = None if user.attributes is None else user.attributes.__dict__
    dct["_links"] = {
       "self": url_for("api.user", user_id=user.user_id)
    }
    return dct


def check_if_current_user_owns_brand(brand_id: str) -> bool:
    db_brands = BrandsDatabase(db_connection)
    current_account_brands = db_brands.get_brands_of_account(get_jwt_identity(), onlyID=True)
    return brand_id in current_account_brands


class Users(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        try:
            brand_id = data["brand_id"]
            raw_data_sources = data["data_sources"]
            for raw_data_source in raw_data_sources:
                if raw_data_source["source_name"] != "twitter":
                    raise ValueError
            # Save data sources
            db_sources = SourcesDatabase(db_connection)
            data_sources = []
            for raw_data_source in raw_data_sources:
                if raw_data_source["source_name"] == "twitter":
                    data_source = TwitterDataSource(source_user_id=raw_data_source["source_user_id"])
                    data_sources.append(data_source)
                    # Save the empty data source in the DB
                    db_sources.save_source(data_source)
            # Save user
            db_users = UsersDatabase(db_connection)
            data_sources_ids = [ds.source_id for ds in data_sources]
            user = User(brand_id=brand_id, data_sources=data_sources_ids)
            db_users.save_user(user)
            # Send the data sources for collection
            queue = mqtt.Client()
            queue.connect("localhost")
            for data_source in data_sources:
                topic = f"collector/{data_source.source_name}"
                queue.publish(topic, json.dumps(data_source.to_dict()))
            # Return a response
            return user_to_api_repr(user), 201
        except KeyError:
            return {"message": "Error, some keys are missing"}, 400
        except ValueError:
            return {"message": "Error, one or more data sources not supported."}, 400

    @jwt_required()
    def get(self):
        args = request.args
        brand_id = args.get("brand_id")
        include_attributes = args.get("include_attributes", False)
        db = UsersDatabase(db_connection)
        if brand_id is not None:
            # Check if the currently logged account owns this brand
            if not check_if_current_user_owns_brand(brand_id):
                abort_if_not_authorized(brand_id)
            users = db.get_users_of_brand(brand_id)
            users = [user_to_api_repr(user, include_attributes) for user in users]
            return users, 200
        else:
            users = db.get_all_users()
            users = [user_to_api_repr(user, include_attributes) for user in users]
            return users, 200


class UsersID(Resource):
    @jwt_required()
    def get(self, user_id):
        # Check in DB
        db = UsersDatabase(connection=db_connection)
        user = db.get_user_by_id(user_id)

        if user is None:
            return {"message": "Error, user not found"}, 404

        if not check_if_current_user_owns_brand(user.brand_id):
            abort_if_not_authorized(user.brand_id)

        include_attributes = request.args.get("include_attributes", False)
        return user_to_api_repr(user, include_attributes), 201

    @jwt_required()
    def delete(self, user_id):
        # Check in DB
        db = UsersDatabase(connection=db_connection)
        user = db.get_user_by_id(user_id)

        if user is None:
            return {"message": "Error, user not found"}, 404

        if not check_if_current_user_owns_brand(user.brand_id):
            abort_if_not_authorized(user.brand_id)
        # Delete from DB
        db.delete_user_by_id(user_id, user.brand_id)

        return {}, 204
