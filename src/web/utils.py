from flask_jwt_extended import get_jwt_identity
from flask_restful import abort


def abort_if_not_authorized(account_id: str):
    current_account = get_jwt_identity()
    if current_account != account_id:
        abort(403, message="Error, unauthorized")
