from __future__ import annotations
from typing import List

from common.models.utils import generate_id


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


class Activity(object):
    def __init__(self,
                 source_activity_id: str,
                 source_name: str,
                 data_source_id: str,
                 activity_id: str = None,
                 enriched_properties: ActivityEnrichments = None
                 ) -> None:
        self.activity_id = generate_id() if activity_id is None else activity_id
        self.source_activity_id = source_activity_id
        self.source_name = source_name
        self.data_source_id = data_source_id
        self.enriched_properties = enriched_properties

    def to_dict(self) -> dict:
        return {
            "source_activity_id": self.source_activity_id,
            "source_name": self.source_name,
            "data_source_id": self.data_source_id,
            "activity_id": self.activity_id,
            "enriched_properties": None if self.enriched_properties is None else self.enriched_properties.to_dict()
        }

    def __repr__(self) -> str:
        string = ""
        separator = ""
        for key, value in self.__dict__.items():
            if value is not None:
                string += f"{separator}{key} = {value}"
                separator = ", "
        return string

    def __eq__(self, other: Activity):
        return self.activity_id == other.activity_id


class TwitterActivity(Activity):
    def __init__(self,
                 source_activity_id: str,
                 data_source_id: str,
                 activity_id: str = None,
                 enriched_properties: ActivityEnrichments = None,
                 text: str = None,
                 language: str = None,
                 media: List[str] = None,
                 hashtags: List[str] = None,
                 urls: List[str] = None,
                 likes: int = None,
                 shares: int = None,
                 ) -> None:
        super().__init__(source_activity_id, "twitter", data_source_id, activity_id, enriched_properties)
        self.text = text
        self.language = language
        self.media = media
        self.hashtags = hashtags
        self.urls = urls
        self.likes = likes
        self.shares = shares

    def to_dict(self) -> dict:
        dct = super().to_dict()
        dct_sub = {
            "text": self.text,
            "language": self.language,
            "media": self.media,
            "hashtags": self.hashtags,
            "urls": self.urls,
            "likes": self.likes,
            "shares": self.shares
        }
        return {**dct, **dct_sub}

    @classmethod
    def from_dict(cls, properties: dict) -> TwitterActivity:
        allowed_fields = ("source_activity_id", "data_source_id", "activity_id",
                          "text", "language", "media", "hashtags", "urls", "likes", "shares")
        allowed_attributes = {k: v for k, v in properties.items() if k in allowed_fields}
        enriched_properties_dict = properties.get("enriched_properties", None)
        if enriched_properties_dict is not None:
            allowed_attributes["enriched_properties"] = ActivityEnrichments.from_dict(enriched_properties_dict)
        return cls(**allowed_attributes)