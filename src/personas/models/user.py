from __future__ import annotations
from typing import List, Type

from personas.models.sources.abstract import UserDataSource


class User(object):
    def __init__(self,
                 user_id: str,
                 brand_id: str,
                 data_sources: List[Type[UserDataSource]]
                 ) -> None:
        #TODO
        pass

    @classmethod
    def from_dict(cls, dct: dict) -> User:
        allowed_fields = ("id_", "name", "gender", "location", "profile_image_url", "biography", "type_",
                          "pref_language", "site", "followers_count", "following_count", "posts", "cluster")

        allowed_attributes = {k: v for k, v in dct.items() if k in allowed_fields}

        return cls(**allowed_attributes)

    def __repr__(self):
        string = ""
        separator = ""
        for key, value in self.__dict__.items():
            if value is not None:
                string += f"{separator}{key} = {value}"
                separator = ", "
        return string
