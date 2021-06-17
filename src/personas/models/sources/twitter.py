from __future__ import annotations

from personas.models.sources.abstract import UserDataSource
from personas.models.attributes import Attributes


class TwitterDataSource(UserDataSource):
    def __init__(self,
                 source_user_id: str,
                 source_id: str = None,
                 username: str = None,
                 attributes: Attributes = None,
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
        allowed_fields = ("source_user_id", "source_id", "username", "attributes", "name",
                          "location", "profile_image_url", "description", "url", "followers_count", "following_count")
        allowed_attributes = {k: v for k, v in properties.items() if k in allowed_fields}
        return cls(**allowed_attributes)
