from __future__ import annotations

from personas.models.attributes import Attributes


class UserDataSource(object):
    def __init__(self,
                 source_name: str,
                 source_user_id: str,
                 source_id: str = None,
                 username: str = None,
                 attributes: Attributes = None):
        self.source_name = source_name
        self.source_user_id = source_user_id
        self.source_id = source_id
        self.username = username
        self.attributes = attributes

    def to_dict(self):
        return {
            "source_name": self.source_name,
            "source_user_id": self.source_user_id,
            "source_id": self.source_id,
            "username": self.username,
            "attributes": None if self.attributes is None else self.attributes
        }

    def __repr__(self):
        string = ""
        separator = ""
        for key, value in self.__dict__.items():
            if value is not None:
                string += f"{separator}{key} = {value}"
                separator = ", "
        return string

    def __eq__(self, other: UserDataSource):
        return self.source_id == other.source_id
