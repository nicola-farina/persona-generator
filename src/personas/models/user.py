from __future__ import annotations
from typing import List

from personas.models.attributes import Attributes


class User(object):
    def __init__(self,
                 brand_id: str,
                 data_sources: List[str],
                 user_id: str = None,
                 attributes: Attributes = None
                 ) -> None:
        self.brand_id = brand_id
        self.data_sources = data_sources
        self.user_id = user_id
        self.attributes = attributes

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "brand_id": self.brand_id,
            "data_sources": self.data_sources,
            "attributes": None if self.attributes is None else self.attributes.to_dict()
        }

    @classmethod
    def from_dict(cls, dct: dict) -> User:
        allowed_fields = ("user_id", "brand_id", "data_sources")
        allowed_attributes = {k: v for k, v in dct.items() if k in allowed_fields}
        attributes_dict = dct.get("attributes", None)
        if attributes_dict is not None:
            allowed_attributes["attributes"] = Attributes.from_dict(attributes_dict)
        return cls(**allowed_attributes)

    def __repr__(self):
        string = ""
        separator = ""
        for key, value in self.__dict__.items():
            if value is not None:
                string += f"{separator}{key} = {value}"
                separator = ", "
        return string
