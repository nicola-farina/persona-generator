from __future__ import annotations

from personas.models.activities.enrichments import ActivityEnrichments


class Activity(object):

    def __init__(self,
                 source_activity_id: str,
                 source_name: str,
                 activity_id: str = None,
                 author_id: str = None,
                 enriched_properties: ActivityEnrichments = None
                 ) -> None:
        self.source_activity_id = source_activity_id
        self.source_name = source_name
        self.activity_id = activity_id
        self.author_id = author_id
        self.enriched_properties = enriched_properties

    def to_dict(self) -> dict:
        return {
            "source_activity_id": self.source_activity_id,
            "source_name": self.source_name,
            "activity_id": self.activity_id,
            "author_id": self.author_id,
            "enriched_properties": None if self.enriched_properties is None else self.enriched_properties.__dict__
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
