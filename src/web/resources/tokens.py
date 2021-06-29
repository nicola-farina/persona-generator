from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token
import bcrypt

from web.api.app import db_connection
from src.common.database.accounts import AccountsDatabase


class Tokens(Resource):
    def post(self):
        data = request.get_json()
        try:
            email = data["email"]
            password = data["password"]
            # Get account from DB
            db = AccountsDatabase(db_connection)
            account = db.get_account_by_email(email)

            if account is None:
                return {"message": "Error, email or password not right."}, 401

            # Check the password
            psw_check = bcrypt.checkpw(password.encode("utf-8"), account.hashed_psw)
            if psw_check:
                return {
                    "access_token": create_access_token(identity=account.account_id)
                }, 200
            else:
                return {"message": "Error, email or password not right."}, 401
        except KeyError:
            return {"message": "Error, some keys are missing"}, 400
