from typing import Union, List

from rejson import Path

from personas.database.connection import DatabaseConnection
from personas.database.utils import generate_id
from personas.models.brand import Brand


class BrandsDatabase(object):
    def __init__(self, connection: DatabaseConnection) -> None:
        self.connection = connection.connection

    @staticmethod
    def __get_key(brand_id: str) -> str:
        return f"brand:{brand_id}"

    def save_brand(self, brand: Brand) -> None:
        if brand.brand_id is None:
            brand.brand_id = generate_id()
        key = self.__get_key(brand.brand_id)
        brand_dict = brand.to_dict()
        self.connection.jsonset(key, Path.rootPath(), brand_dict)
        # Add it to the brands list
        self.connection.rpush("brands", brand.brand_id)
        # Add it to the brands list of an account
        self.connection.rpush(f"account:{brand.account_id}:brands", brand.brand_id)

    def get_brand_by_id(self, brand_id: str) -> Union[Brand, None]:
        key = self.__get_key(brand_id)
        brand_dict = self.connection.jsonget(key, Path.rootPath())
        if brand_dict:
            brand = Brand.from_dict(brand_dict)
            return brand
        else:
            return None

    def delete_brand_by_id(self, brand_id: str, account_id: str) -> None:
        key = self.__get_key(brand_id)
        self.connection.delete(key)
        # Delete it from the brands list
        self.connection.lrem("brands", 1, brand_id)
        # Delete it from the brands list of an account
        self.connection.lrem(f"account:{account_id}:brands", 1, brand_id)

    def get_brands_of_account(self, account_id: str, onlyID: bool = False) -> List[Brand]:
        key = f"account:{account_id}:brands"
        brands_id = self.connection.lrange(key, 0, -1)
        if onlyID:
            return brands_id
        else:
            brands = []
            for brand_id in brands_id:
                brands.append(self.get_brand_by_id(brand_id))
            return brands

    def get_all_brands(self) -> List[Brand]:
        brands = []
        for brand_id in self.connection.lrange("brands", 0, -1):
            brands.append(self.get_brand_by_id(brand_id))
        return brands
