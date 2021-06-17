from typing import List


class Attributes(object):
    def __init__(self,
                 name: str = None,
                 gender: str = None,
                 age: int = None,
                 type_: str = None,
                 location: str = None,
                 pref_language: str = None,
                 family_status: str = None,
                 has_children: bool = None,
                 job: str = None,
                 income: int = None,
                 personality: str = None,
                 interests: List[str] = None,
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
        self.times_of_activity = times_of_activity
        self.channels = channels

    def __repr__(self):
        string = ""
        separator = ""
        for key, value in self.__dict__.items():
            if value is not None:
                string += f"{separator}{key} = {value}"
                separator = ", "
        return string
