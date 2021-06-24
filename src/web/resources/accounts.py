from flask import request, url_for
from flask_restful import Resource
from flask_jwt_extended import jwt_required
import bcrypt

from web.common.utils import abort_if_not_authorized
from web.api.app import db_connection
from src.personas.models.account import Account
from src.personas.database.accounts import AccountsDatabase


def account_to_api_repr(account: Account) -> dict:
    return {
        "account_id": account.account_id,
        "email": account.email,
        "name": account.name,
        "_links": {
            "self": url_for("api.account", account_id=account.account_id)
        }
    }


class Accounts(Resource):
    def post(self):
        data = request.get_json()
        try:
            email = data["email"]
            name = data["name"]
            password = data["password"]
            # Check if email already present
            db = AccountsDatabase(connection=db_connection)
            email_check = db.get_account_by_email(email)
            if email_check is not None:
                return {"message": "Error, email already taken"}, 409
            # Create account
            hashed_psw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            account = Account(email, name, hashed_psw=hashed_psw)
            # Save it in DB
            db.save_account(account)
            # Return a response
            return account_to_api_repr(account), 201
        except KeyError:
            return {"message": "Error, some keys are missing"}, 400

    @jwt_required()
    def get(self):
        db = AccountsDatabase(db_connection)
        accounts = db.get_all_accounts()
        accounts = [account_to_api_repr(account) for account in accounts]
        return accounts, 200


class AccountsID(Resource):
    @jwt_required()
    def get(self, account_id):
        abort_if_not_authorized(account_id)
        # Check in DB
        db = AccountsDatabase(connection=db_connection)
        account = db.get_account_by_id(account_id)
        if account is None:
            return {"message": "Error, account not found"}, 404

        return account_to_api_repr(account), 200

    @jwt_required()
    def delete(self, account_id):
        abort_if_not_authorized(account_id)
        # Check in DB
        db = AccountsDatabase(connection=db_connection)
        account = db.get_account_by_id(account_id)

        if account is None:
            return {"message": "Error, account not found"}, 404

        # Delete from DB
        db.delete_account_by_id(account_id)

        return {}, 204
