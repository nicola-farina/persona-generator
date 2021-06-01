from urllib.parse import quote
import requests


class GenderClassifier(object):
    def __init__(self, key: str):
        self.key = key

    def __call_namsor_api(self, name: str) -> dict:
        endpoint = "https://v2.namsor.com/NamSorAPIv2/api2/json/genderFull/"
        url = endpoint + quote(name)
        headers = {"X-API-KEY": self.key}
        response = requests.get(url, headers=headers)
        return response.json()

    def predict_gender_by_name(self, name: str) -> str:
        print(f"Predicting gender for {name}...", end=" ")
        response = self.__call_namsor_api(name)
        gender = response["likelyGender"]
        confidence = round(response["probabilityCalibrated"], 2)
        print(gender)
        return gender

    def predict_gender_by_photo(self, photo_url: str) -> str:
        pass
