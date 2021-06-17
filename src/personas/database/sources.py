from typing import Union

from rejson import Path

from personas.database.abstract import Database
from personas.models.sources.abstract import UserDataSource
from personas.models.sources.twitter import TwitterDataSource


class SourcesDatabase(Database):
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0) -> None:
        super().__init__(host, port, db)

    @staticmethod
    def __get_key(source_id: str) -> str:
        return f"source:{source_id}"

    def save_source(self, source: UserDataSource) -> None:
        # Generate ID if first time save
        if source.source_id is None:
            source.source_id = self._generate_id()
        key = self.__get_key(source.source_id)
        source_dict = source.to_dict()
        self._connection.jsonset(key, Path.rootPath(), source_dict)

    def get_source_by_id(self, source_id: str) -> Union[UserDataSource, None]:
        key = self.__get_key(source_id)
        source_dict = self._connection.jsonget(key, Path.rootPath())
        if source_dict:
            if source_dict["source_name"] == "twitter":
                source = TwitterDataSource.from_dict(source_dict)
            else:
                source = None
            return source
        else:
            return None
