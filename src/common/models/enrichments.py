from __future__ import annotations

from typing import List


class Enrichments(object):
    def __init__(self,
                 name: str = None,
                 gender: str = None,
                 age: str = None,
                 type_: str = None,
                 location: str = None,
                 pref_language: str = None,
                 family_status: str = None,
                 has_children: bool = None,
                 job: str = None,
                 income: int = None,
                 personality: str = None,
                 interests: dict = None,
                 attitude: float = None,
                 times_of_activity: dict = None,
                 channels: List[str] = None):
        self.name = name
        self.gender = gender
        self.age = age
        self.type_ = type_
        self.location = location
        self.pref_language = pref_language
        self.family_status = family_status
        self.has_children = has_children
        self.job = job
        self.income = income
        self.personality = personality
        self.interests = interests
        self.attitude = attitude
        self.times_of_activity = times_of_activity
        self.channels = channels

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "gender": self.gender,
            "age": self.age,
            "type_": self.type_,
            "location": self.location,
            "pref_language": self.pref_language,
            "family_status": self.family_status,
            "has_children": self.has_children,
            "job": self.job,
            "income": self.income,
            "personality": self.personality,
            "interests": self.interests,
            "attitude": self.attitude,
            "times_of_activity": self.times_of_activity,
            "channels": self.channels
        }

    @classmethod
    def from_dict(cls, dct: dict) -> Enrichments:
        allowed_fields = ("name", "gender", "age", "type_", "location", "pref_language", "family_status",
                          "has_children", "job", "income", "personality", "interests", "attitude",
                          "times_of_activity", "channels")
        allowed_attributes = {k: v for k, v in dct.items() if k in allowed_fields}
        return cls(**allowed_attributes)

    def __repr__(self):
        string = ""
        separator = ""
        for key, value in self.__dict__.items():
            if value is not None:
                string += f"{separator}{key} = {value}"
                separator = ", "
        return string
