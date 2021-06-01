from unittest import TestCase

from personas.models.sources.twitter import TwitterDataSource


class TestUserDataSource(TestCase):
    def test_repr(self):
        ds = TwitterDataSource(source_user_id="1", username="test")
        ds_repr = ds.__repr__()
        self.assertEqual(ds_repr, "source_name = Twitter, source_user_id = 1, username = test")
