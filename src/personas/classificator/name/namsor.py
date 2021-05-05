from urllib.parse import quote
import requests


class NameClassifier(object):

    __endpoints = {
        "gender": "https://v2.namsor.com/NamSorAPIv2/api2/json/genderFull/",
        "type": "https://v2.namsor.com/NamSorAPIv2/api2/json/nameType/"
    }

    def __init__(self, key: str):
        self.key = key

    def __call_api(self, name: str, endpoint: str) -> dict:
        url = self.__endpoints[endpoint] + quote(name)
        headers = {"X-API-KEY": self.key}
        response = requests.get(url, headers=headers)
        return response.json()

    def predict_gender(self, name: str) -> dict:
        print(f"Predicting gender for {name}...", end=" ")

        response = self.__call_api(name, "gender")

        gender = response["likelyGender"]
        confidence = round(response["probabilityCalibrated"], 2)

        print(gender)
        return {
            "predicted_gender": gender,
            "confidence": confidence
        }

    def predict_type(self, name: str) -> dict:
        print(f"Predicting type for {name}...", end=" ")

        response = self.__call_api(name, "type")

        name_type = response["commonType"]
        score = response["score"]

        print(name_type)
        return {
            "predicted_type": name_type,
            "score": score
        }
