from typing import List


class ActivityEnrichments(object):
    def __init__(self,
                 language: str = None,
                 entities: List[str] = None,
                 topics: List[str] = None,
                 sentiment: float = None) -> None:
        self.language = language
        self.entities = entities
        self.topics = topics
        self.sentiment = sentiment

    def __repr__(self):
        string = ""
        separator = ""
        for key, value in self.__dict__.items():
            if value is not None:
                string += f"{separator}{key} = {value}"
                separator = ", "
        return string
