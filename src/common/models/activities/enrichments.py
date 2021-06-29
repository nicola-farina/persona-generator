from __future__ import annotations
from typing import List


class ActivityEnrichments(object):
    def __init__(self,
                 language: str = None,
                 entities: List[str] = None,
                 sentiment: float = None) -> None:
        self.language = language
        self.entities = entities
        self.sentiment = sentiment

    def to_dict(self) -> dict:
        return {
            "language": self.language,
            "entities": self.entities,
            "sentiment": self.sentiment
        }

    @classmethod
    def from_dict(cls, dct: dict) -> ActivityEnrichments:
        allowed_fields = ("language", "entities", "sentiment")
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
