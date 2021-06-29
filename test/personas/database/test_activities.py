from unittest import TestCase

from common.database.activities import ActivitiesDatabase
from common.models.activities.twitter import TwitterActivity


class TestActivitiesDatabase(TestCase):
    def test_save_activity(self):
        db = ActivitiesDatabase()
        activity = TwitterActivity("abc")
        db.save_activity(activity)

    def test_get_activity_by_id(self):
        # Save
        db = ActivitiesDatabase()
        activity = TwitterActivity("abc", activity_id="123")
        db.save_activity(activity)
        # Get
        query_activity = db.get_activity_by_id(activity.activity_id)
        self.assertEqual(activity, query_activity)
