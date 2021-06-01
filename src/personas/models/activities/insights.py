from typing import Set


class ActivityInsights(object):
    def __init__(self,
                 language: str = None,
                 entities: Set[str] = None,
                 topics: Set[str] = None,
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