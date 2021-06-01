from personas.models.sources.abstract import UserDataSource
from personas.models.attributes import Attributes


class TwitterDataSource(UserDataSource):
    def __init__(self,
                 source_user_id: str,
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
        super().__init__("Twitter", source_user_id, username, attributes)
        self.name = name
        self.location = location
        self.profile_image_url = profile_image_url
        self.description = description
        self.url = url
        self.followers_count = followers_count
        self.following_count = following_count
