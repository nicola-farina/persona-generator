from typing import Union

from rejson import Path

from personas.database.connection import DatabaseConnection
from personas.database.utils import generate_id
from personas.models.user import User


class UsersDatabase(object):
    def __init__(self, connection: DatabaseConnection) -> None:
        self.connection = connection.connection

    @staticmethod
    def __get_key(user_id: str) -> str:
        return f"user:{user_id}"

    def save_user(self, user: User) -> None:
        if user.user_id is None:
            user.user_id = generate_id()
        key = self.__get_key(user.user_id)
        user_dict = user.to_dict()
        self.connection.jsonset(key, Path.rootPath(), user_dict)
        # Add it to the users list
        self.connection.rpush("users", user.user_id)
        # Add it to the users list of a brand
        self.connection.rpush(f"brand:{user.brand_id}:users", user.user_id)
        # Keep track of the sources of this user
        for source_id in user.data_sources:
            self.connection.sadd(f"user:{user.user_id}:sources", source_id)

    def get_user_by_id(self, user_id: str) -> Union[User, None]:
        key = self.__get_key(user_id)
        user_dict = self.connection.jsonget(key, Path.rootPath())
        if user_dict:
            user = User.from_dict(user_dict)
            return user
        else:
            return None

    def delete_user_by_id(self, user_id: str, brand_id: str) -> None:
        key = self.__get_key(user_id)
        self.connection.delete(key)
        # Delete it from the users list
        self.connection.lrem("users", 1, user_id)
        # Delete it from the users list of a brand
        self.connection.lrem(f"brand:{brand_id}:users", 1, user_id)

    def get_users_of_brand(self, brand_id: str):
        key = f"brand:{brand_id}:users"
        users = []
        for user_id in self.connection.lrange(key, 0, -1):
            users.append(self.get_user_by_id(user_id))
        return users

    def get_all_users(self):
        users = []
        for user_id in self.connection.lrange("users", 0, -1):
            users.append(self.get_user_by_id(user_id))
        return users
