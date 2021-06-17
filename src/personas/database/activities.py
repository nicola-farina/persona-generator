from typing import Union

from rejson import Path

from personas.database.abstract import Database
from personas.models.activities.abstract import Activity
from personas.models.activities.twitter import TwitterActivity


class ActivitiesDatabase(Database):
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0) -> None:
        super().__init__(host, port, db)

    @staticmethod
    def __get_key(activity_id: str) -> str:
        return f"activity:{activity_id}"

    def save_activity(self, activity: Activity) -> None:
        # Generate ID if first time save
        if activity.activity_id is None:
            activity.activity_id = self._generate_id()
        key = self.__get_key(activity.activity_id)
        activity_dict = activity.to_dict()
        self._connection.jsonset(key, Path.rootPath(), activity_dict)

    def get_activity_by_id(self, activity_id: str) -> Union[Activity, None]:
        key = self.__get_key(activity_id)
        activity_dict = self._connection.jsonget(key, Path.rootPath())
        if activity_dict:
            if activity_dict["source_name"] == "twitter":
                activity = TwitterActivity.from_dict(activity_dict)
            else:
                activity = None
            return activity
        else:
            return None
