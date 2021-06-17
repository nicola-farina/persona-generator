from unittest import TestCase

from personas.database.sources import SourcesDatabase
from personas.models.sources.twitter import TwitterDataSource


class TestSourcesDatabase(TestCase):
    def test_save_source(self):
        db = SourcesDatabase()
        source = TwitterDataSource("abc")
        db.save_source(source)

    def test_get_source_by_id(self):
        # Save
        db = SourcesDatabase()
        source = TwitterDataSource("abc", source_id="123")
        db.save_source(source)
        # Get
        query_source = db.get_source_by_id(source.source_id)
        self.assertEqual(source, query_source)
