from __future__ import annotations

from src.common.models.utils import generate_id
from src.common.models.enrichments import Enrichments


class DataSource(object):
    def __init__(self,
                 source_name: str,
                 source_user_id: str,
                 source_id: str = None,
                 username: str = None,
                 attributes: Enrichments = None):
        self.source_id = generate_id() if source_id is None else source_id
        self.source_name = source_name
        self.source_user_id = source_user_id
        self.username = username
        self.attributes = attributes

    def to_dict(self):
        return {
            "source_name": self.source_name,
            "source_user_id": self.source_user_id,
            "source_id": self.source_id,
            "username": self.username,
            "attributes": None if self.attributes is None else self.attributes.to_dict()
        }

    def __repr__(self):
        string = ""
        separator = ""
        for key, value in self.__dict__.items():
            if value is not None:
                string += f"{separator}{key} = {value}"
                separator = ", "
        return string

    def __eq__(self, other: DataSource):
        return self.source_id == other.source_id


class TwitterDataSource(DataSource):
    def __init__(self,
                 source_user_id: str,
                 source_id: str = None,
                 username: str = None,
                 attributes: Enrichments = None,
                 name: str = None,
                 location: str = None,
                 profile_image_url: str = None,
                 description: str = None,
                 url: str = None,
                 followers_count: int = None,
                 following_count: int = None
                 ):
        super().__init__("twitter", source_user_id, source_id, username, attributes)
        self.name = name
        self.location = location
        self.profile_image_url = profile_image_url
        self.description = description
        self.url = url
        self.followers_count = followers_count
        self.following_count = following_count

    def to_dict(self) -> dict:
        dct = super().to_dict()
        dct_sub = {
            "name": self.name,
            "location": self.location,
            "profile_image_url": self.profile_image_url,
            "description": self.description,
            "url": self.url,
            "followers_count": self.followers_count,
            "following_count": self.following_count
        }
        return {**dct, **dct_sub}

    @classmethod
    def from_dict(cls, properties: dict) -> TwitterDataSource:
        allowed_fields = ("source_user_id", "source_id", "username", "name",
                          "location", "profile_image_url", "description", "url", "followers_count", "following_count")
        allowed_attributes = {k: v for k, v in properties.items() if k in allowed_fields}
        attributes_dict = properties.get("attributes", None)
        if attributes_dict is not None:
            allowed_attributes["attributes"] = Enrichments.from_dict(attributes_dict)
        return cls(**allowed_attributes)
