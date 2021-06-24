from typing import Union, List

from rejson import Path

from personas.database.connection import DatabaseConnection
from personas.models.sources.abstract import UserDataSource
from personas.models.sources.twitter import TwitterDataSource
from personas.database.utils import generate_id


class SourcesDatabase(object):
    def __init__(self, connection: DatabaseConnection) -> None:
        self.connection = connection.connection

    @staticmethod
    def __get_key(source_id: str) -> str:
        return f"source:{source_id}"

    def save_source(self, source: UserDataSource) -> str:
        if source.source_id is None:
            source.source_id = generate_id()
        key = self.__get_key(source.source_id)
        source_dict = source.to_dict()
        self.connection.jsonset(key, Path.rootPath(), source_dict)
        # Add it to the source list
        self.connection.rpush("sources", source.source_id)
        return source.source_id

    def get_source_by_id(self, source_id: str) -> Union[UserDataSource, None]:
        key = self.__get_key(source_id)
        source_dict = self.connection.jsonget(key, Path.rootPath())
        if source_dict:
            if source_dict["source_name"] == "twitter":
                source = TwitterDataSource.from_dict(source_dict)
                return source
            else:
                raise ValueError
        else:
            return None

    def get_sources_of_user(self, user_id: str) -> List[UserDataSource]:
        key = f"user:{user_id}:sources"
        sources_id = self.connection.smembers(key)
        sources = []
        for source_id in sources_id:
            sources.append(self.get_source_by_id(source_id))
        return sources
