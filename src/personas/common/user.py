from __future__ import annotations
import json
from typing import List

from personas.common.post import Post


class Brand(object):

    def __init__(self,
                 id_: str,
                 followers: List[User] = None) -> None:
        self.id_ = id_
        self.followers = followers


class User(object):

    def __init__(self,
                 id_: str,
                 name: str = None,
                 gender: str = None,
                 location: str = None,
                 profile_image_url: str = None,
                 biography: str = None,
                 user_type: str = None,
                 pref_language: str = None,
                 site: str = None,
                 followers_count: int = None,
                 following_count: int = None,
                 posts: List[Post] = None
                 ) -> None:
        self.id_ = id_
        self.name = name
        self.gender = gender
        self.location = location
        self.profile_image_url = profile_image_url
        self.biography = biography
        self.user_type = user_type
        self.pref_language = pref_language
        self.site = site
        self.followers_count = followers_count
        self.following_count = following_count
        self.posts = posts

    @classmethod
    def from_dict(cls, dct: dict) -> User:
        allowed_fields = ("id_", "name", "gender", "location", "profile_image_url", "biography", "user_type",
                          "pref_language", "site", "followers_count", "following_count", "posts")

        allowed_attributes = {k: v for k, v in dct.items() if k in allowed_fields}

        return cls(**allowed_attributes)
