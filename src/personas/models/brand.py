from __future__ import annotations


class Brand(object):
    def __init__(self,
                 name: str,
                 brand_id: str = None) -> None:
        self.name = name
        self.brand_id = brand_id

    def to_dict(self) -> dict:
        return {
            "brand_id": self.brand_id,
            "name": self.name
        }

    @classmethod
    def from_dict(cls, properties: dict) -> Brand:
        allowed_fields = ("brand_id", "name")
        allowed_attributes = {k: v for k, v in properties.items() if k in allowed_fields}
        return cls(**allowed_attributes)

    def __repr__(self):
        string = f"ID: {self.brand_id}; NAME: {self.name}"
        return string

    def __eq__(self, other: Brand):
        return self.brand_id == other.brand_id
