from __future__ import annotations

from src.common.models.enrichments import Enrichments
from src.common.models.utils import generate_id


class Persona(object):
    def __init__(self,
                 brand_id: str,
                 persona_id: str = None,
                 name: str = None,
                 photo: str = None,
                 description: str = None,
                 attributes: Enrichments = None) -> None:
        self.persona_id = generate_id() if persona_id is None else persona_id
        self.brand_id = brand_id
        self.name = name
        self.photo = photo
        self.description = description
        self.attributes = attributes

    def to_dict(self) -> dict:
        return {
            "persona_id": self.persona_id,
            "brand_id": self.brand_id,
            "name": self.name,
            "photo": self.photo,
            "description": self.description,
            "attributes": self.attributes.to_dict()
        }

    @classmethod
    def from_dict(cls, dct: dict) -> Persona:
        allowed_fields = ("persona_id", "brand_id", "name", "photo", "description")
        allowed_attributes = {k: v for k, v in dct.items() if k in allowed_fields}
        attributes_dict = dct.get("attributes", None)
        if attributes_dict is not None:
            allowed_attributes["attributes"] = Enrichments.from_dict(attributes_dict)
        return cls(**allowed_attributes)

    def __repr__(self):
        string = ""
        separator = ""
        for key, value in self.__dict__.items():
            if value is not None:
                string += f"{separator}{key} = {value}"
                separator = ", "
        return string