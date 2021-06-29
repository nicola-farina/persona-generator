from unittest import TestCase

from common.database.connection import Database


class TestDatabase(TestCase):

    def test_connection(self):
        try:
            db = Database()
        except:
            self.fail("NAH")


    def test_save(self):
        self.fail()
