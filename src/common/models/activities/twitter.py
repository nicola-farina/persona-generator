from __future__ import annotations
from typing import List

from common.models.activities.general import Activity
from common.models.activities.enrichments import ActivityEnrichments


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
