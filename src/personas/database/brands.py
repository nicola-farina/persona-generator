from typing import Union

from rejson import Path

from personas.database.abstract import Database
from personas.models.brand import Brand


class BrandsDatabase(Database):
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0) -> None:
        super().__init__(host, port, db)

    @staticmethod
    def __get_key(brand_id: str) -> str:
        return f"brand:{brand_id}"

    def save_brand(self, brand: Brand) -> None:
        if brand.brand_id is None:
            brand.brand_id = self._generate_id()
        key = self.__get_key(brand.brand_id)
        brand_dict = brand.to_dict()
        self._connection.jsonset(key, Path.rootPath(), brand_dict)

    def get_brand_by_id(self, brand_id: str) -> Union[Brand, None]:
        key = self.__get_key(brand_id)
        brand_dict = self._connection.jsonget(key, Path.rootPath())
        if brand_dict:
            brand = Brand.from_dict(brand_dict)
            return brand
        else:
            return None
