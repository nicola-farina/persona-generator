import json
import random

import names


class PersonaGenerator(object):
    def __init__(self):
        # Load dict of profile images
        with open("faces.json", "r") as infile:
            self.faces = json.load(infile)

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

    def get_name(self, gender: str) -> tuple:
        if gender is None:
            gender = random.choice(["male", "female"])
        return names.get_full_name(gender=gender)
