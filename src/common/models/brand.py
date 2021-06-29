from __future__ import annotations

from src.common.models.utils import generate_id


class Brand(object):
    def __init__(self,
                 name: str,
                 account_id: str,
                 brand_id: str = None) -> None:
        self.brand_id = generate_id() if brand_id is None else brand_id
        self.name = name
        self.account_id = account_id

    def to_dict(self) -> dict:
        return {
            "brand_id": self.brand_id,
            "account_id": self.account_id,
            "name": self.name
        }

    @classmethod
    def from_dict(cls, properties: dict) -> Brand:
        allowed_fields = ("brand_id", "name", "account_id")
        allowed_attributes = {k: v for k, v in properties.items() if k in allowed_fields}
        return cls(**allowed_attributes)

    def __repr__(self):
        string = f"ID: {self.brand_id}; NAME: {self.name}"
        return string

    def __eq__(self, other: Brand):
        return self.brand_id == other.brand_id
