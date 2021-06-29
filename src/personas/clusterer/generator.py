import json
import random
import requests

from personas.clusterer.secrets import NAME_API_KEY


class PersonaGenerator(object):
    def __init__(self):
        # Load dict of profile images
        with open("faces.json", "r") as infile:
            self.faces = json.load(infile)
        self.name_key = NAME_API_KEY

    def get_image(self, gender: str, age: str = None) -> str:
        if gender is None:
            gender = random.choice(["male", "female"])
        elif gender not in ["male", "female"]:
            raise ValueError("Unsupported gender")

        if age is None:
            age = "19-29"
        elif age not in ["<=18", "19-29", "30-39", ">=40"]:
            raise ValueError("Unsupported age")

        return random.choice(self.faces[gender][age])

    def get_name(self, gender: str, country_code: str = None) -> tuple:
        endpoint = "https://api.parser.name/?api_key=fe404672e5de865c092486a703efb8b6&endpoint=generate&country_code=DE"
        params = {
            "api_key": self.name_key,
            "endpoint": "generate",
            "gender": "f" if gender == "female" else "m",
        }
        if gender is None:
            params["gender"] = random.choice(["m", "f"])
        if country_code is not None:
            params["country_code"] = country_code
        response = requests.get(endpoint, params).json()
        if response["error"] != "null":
            return response["data"][0]["name"]["firstname"]["name"] + response["data"][0]["name"]["lastname"]["name"], \
                   response["data"][0]["name"]["lastname"]["country_code"]
