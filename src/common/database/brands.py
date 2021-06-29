from typing import Union, List

from rejson import Path

from src.common.database.connection import DatabaseConnection
from src.common.models.brand import Brand


class BrandsDatabase(object):
    def __init__(self, connection: DatabaseConnection) -> None:
        self.connection = connection.connection

    @staticmethod
    def __get_key(brand_id: str) -> str:
        return f"brand:{brand_id}"

    def save_brand(self, brand: Brand) -> None:
        key = self.__get_key(brand.brand_id)
        brand_dict = brand.to_dict()
        self.connection.jsonset(key, Path.rootPath(), brand_dict)
        # Add it to the brands list
        self.connection.sadd("brands", brand.brand_id)
        # Add it to the brands list of an account
        self.connection.sadd(f"account:{brand.account_id}:brands", brand.brand_id)

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
        self.connection.srem("brands", brand_id)
        # Delete it from the brands list of an account
        self.connection.srem(f"account:{account_id}:brands", brand_id)

    def get_brands_of_account(self, account_id: str, onlyID: bool = False) -> List[Brand]:
        key = f"account:{account_id}:brands"
        brands_id = self.connection.smembers(key)
        if onlyID:
            return brands_id
        else:
            brands = []
            for brand_id in brands_id:
                brands.append(self.get_brand_by_id(brand_id))
            return brands

    def get_all_brands(self) -> List[Brand]:
        brands = []
        for brand_id in self.connection.smembers("brands"):
            brands.append(self.get_brand_by_id(brand_id))
        return brands
