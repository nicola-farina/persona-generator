from typing import Union, List

from rejson import Path

from common.database.connection import DatabaseConnection
from common.models.activity import Activity, TwitterActivity


class ActivitiesDatabase(object):
    def __init__(self, connection: DatabaseConnection) -> None:
        self.connection = connection.connection

    @staticmethod
    def __get_key(activity_id: str) -> str:
        return f"activity:{activity_id}"

    def save_activity(self, activity: Activity) -> None:
        key = self.__get_key(activity.activity_id)
        source_dict = activity.to_dict()
        self.connection.jsonset(key, Path.rootPath(), source_dict)
        # Add it to the activities list of a data source
        self.connection.sadd(f"source:{activity.data_source_id}:activities", activity.activity_id)

    def get_activity_by_id(self, activity_id: str) -> Union[Activity, None]:
        key = self.__get_key(activity_id)
        activity_dict = self.connection.jsonget(key, Path.rootPath())
        if activity_dict:
            if activity_dict["source_name"] == "twitter":
                activity = TwitterActivity.from_dict(activity_dict)
            else:
                activity = None
            return activity
        else:
            return None

    def get_activities_of_data_source(self, data_source_id: str) -> List[Activity]:
        key = f"source:{data_source_id}:activities"
        activities_id = self.connection.smembers(key)
        activities = []
        for activity_id in activities_id:
            activities.append(self.get_activity_by_id(activity_id))
        return activities
