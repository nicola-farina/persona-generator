from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager

from personas.database.connection import DatabaseConnection

db_connection = DatabaseConnection()


# Application factory
def create_app(config_class: object) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)
    # Setup persistent DB connection
    db_connection.init(
        host=app.config.get("DB_HOST"),
        port=app.config.get("DB_PORT"),
        db=app.config.get("DB_NAME")
    )
    # Setup JWT
    jwt = JWTManager(app)
    # Setup API
    api = Api(prefix="/api/v1")
    from web.resources.tokens import Tokens
    api.add_resource(Tokens, "/tokens", endpoint="api.tokens")
    from web.resources.accounts import Accounts, AccountsID
    api.add_resource(Accounts, "/accounts", endpoint="api.accounts")
    api.add_resource(AccountsID, "/accounts/<string:account_id>", endpoint="api.account")
    from web.resources.brands import Brands, BrandsID
    api.add_resource(Brands, "/brands", endpoint="api.brands")
    api.add_resource(BrandsID, "/brands/<string:brand_id>", endpoint="api.brand")
    from web.resources.users import Users, UsersID
    api.add_resource(Users, "/users", endpoint="api.users")
    api.add_resource(UsersID, "/users/<string:user_id>", endpoint="api.user")
    api.init_app(app)

    return app

