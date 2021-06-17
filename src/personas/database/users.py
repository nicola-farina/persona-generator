from typing import Union

from personas.database.abstract import Database
from personas.models.user import User


class UsersDatabase(Database):
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, test=False) -> None:
        super().__init__(host, port, db, test)

    @staticmethod
    def __get_key(user_id: str) -> str:
        return f"user:{user_id}"
