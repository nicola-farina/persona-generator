from typing import Union

from rejson import Path

from src.common.database.connection import DatabaseConnection
from src.common.models.persona import Persona


class PersonasDatabase(object):
    def __init__(self, connection: DatabaseConnection) -> None:
        self.connection = connection.connection

    @staticmethod
    def __get_key(persona_id: str) -> str:
        return f"persona:{persona_id}"

    def save_persona(self, persona: Persona) -> None:
        key = self.__get_key(persona.persona_id)
        persona_dict = persona.to_dict()
        self.connection.jsonset(key, Path.rootPath(), persona_dict)
        # Add it to the personas list
        self.connection.sadd("personas", persona.persona_id)
        # Add it to the personas list of a brand
        self.connection.sadd(f"brand:{persona.brand_id}:personas", persona.persona_id)

    def get_persona_by_id(self, persona_id: str) -> Union[Persona, None]:
        key = self.__get_key(persona_id)
        persona_dict = self.connection.jsonget(key, Path.rootPath())
        if persona_dict:
            persona = Persona.from_dict(persona_dict)
            return persona
        else:
            return None

    def delete_persona_by_id(self, persona_id: str, brand_id: str) -> None:
        key = self.__get_key(persona_id)
        self.connection.delete(key)
        # Delete it from the personas list
        self.connection.srem("personas", persona_id)
        # Delete it from the personas list of a brand
        self.connection.srem(f"brand:{brand_id}:personas", persona_id)

    def get_personas_of_brand(self, brand_id: str):
        key = f"brand:{brand_id}:personas"
        personas = []
        for persona_id in self.connection.smembers(key):
            personas.append(self.get_persona_by_id(persona_id))
        return personas

    def get_all_personas(self):
        personas = []
        for persona_id in self.connection.smembers("personas"):
            personas.append(self.get_persona_by_id(persona_id))
        return personas
