from typing import List

from personas.models.activities.abstract import Activity
from personas.models.activities.enrichments import ActivityEnrichments


class TwitterActivity(Activity):
    def __init__(self,
                 activity_id: str,
                 author_id: str = None,
                 enriched_properties: ActivityEnrichments = None,
                 text: str = None,
                 language: str = None,
                 media: List[str] = None,
                 hashtags: List[str] = None,
                 urls: List[str] = None,
                 likes: int = None,
                 shares: int = None,
                 ) -> None:
        super().__init__(activity_id, "Twitter", author_id, enriched_properties)
        self.text = text
        self.language = language
        self.media = media
        self.hashtags = hashtags
        self.urls = urls
        self.likes = likes
        self.shares = shares
