from __future__ import annotations
from typing import List

from src.common.models.utils import generate_id
from src.common.models.enrichments import Enrichments


class User(object):
    def __init__(self,
                 brand_id: str,
                 data_sources: List[str],
                 user_id: str = None,
                 attributes: Enrichments = None
                 ) -> None:
        self.user_id = generate_id() if user_id is None else user_id
        self.brand_id = brand_id
        self.data_sources = data_sources
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
            allowed_attributes["attributes"] = Enrichments.from_dict(attributes_dict)
        return cls(**allowed_attributes)

    def __repr__(self):
        string = ""
        separator = ""
        for key, value in self.__dict__.items():
            if value is not None:
                string += f"{separator}{key} = {value}"
                separator = ", "
        return string
