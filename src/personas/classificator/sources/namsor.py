from urllib.parse import quote
import requests

class NamsorAPI(object):

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

    def predict_gender(self, name: str) -> tuple:
        print(f"Predicting gender for {name}...", end=" ")
        response = self.__call_api(name, "gender")
        gender = response["likelyGender"]
        confidence = round(response["probabilityCalibrated"], 2)
        print(gender)
        return gender, confidence

    def predict_type(self, name: str) -> tuple:
        print(f"Predicting type for {name}...", end=" ")
        response = self.__call_api(name, "type")
        name_type = "human" if response["commonType"] == "anthroponym" else "brand"
        score = response["score"]
        print(name_type)
        return name_type, score
