from unittest import TestCase

import fakeredis

from personas.database.brands import BrandsDatabase
from personas.models.brand import Brand


class TestBrandsDatabase(TestCase):

    def test_save_brand(self):
        db = BrandsDatabase()
        brand = Brand("Test")
        db.save_brand(brand)

    def test_get_brand_by_id(self):
        # Save
        db = BrandsDatabase()
        brand = Brand(name="Test", brand_id="123")
        db.save_brand(brand)
        # Get
        query_brand = db.get_brand_by_id(brand.brand_id)
        self.assertEqual(brand, query_brand)
