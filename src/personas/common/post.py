from typing import List, Set


class Post(object):
    def __init__(self,
                 id_: str,
                 author_id: str = None,
                 text: str = None,
                 cleaned_text: str = None,
                 media: List[str] = None,
                 hashtags: List[str] = None,
                 urls: List[str] = None,
                 language: str = None,
                 likes: int = None,
                 shares: int = None,
                 comments_count: int = None,
                 entities: Set[str] = None,
                 topics: Set[str] = None,
                 sentiment: float = None):
        self.id_ = id_
        self.author_id = author_id
        self.text = text
        self.cleaned_text = cleaned_text
        self.media = media
        self.hashtags = hashtags
        self.urls = urls
        self.language = language
        self.likes = likes
        self.shares = shares
        self.comments_count = comments_count
        self.entities = entities
        self.topics = topics
        self.sentiment = sentiment

    @classmethod
    def from_dict(cls, dct: dict):
        allowed_fields = ("id_", "social_network", "author_id", "text", "cleaned_text", "media", "hashtags", "urls",
                          "language", "likes", "shares", "comments_count", "entities", "topics", "sentiment")

        allowed_attributes = {k: v for k, v in dct.items() if k in allowed_fields}

        return cls(**allowed_attributes)
