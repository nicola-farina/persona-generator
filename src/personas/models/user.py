from __future__ import annotations
from typing import List
from typing import NamedTuple


class User(object):

    def __init__(self,
                 id_: str,
                 data_sources: List[NamedTuple] = None
                 ) -> None:
        self.id_ = id_
        self.data_sources = data_sources

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
