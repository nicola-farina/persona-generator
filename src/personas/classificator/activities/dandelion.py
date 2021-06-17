import requests


class DandelionAPI(object):

    __endpoints = {
        "language": "https://api.dandelion.eu/datatxt/li/v1",
        "sentiment": "https://api.dandelion.eu/datatxt/sent/v1",
        "entities": "https://api.dandelion.eu/datatxt/nex/v1"
    }

    def __init__(self,
                 token: str):
        self.token = token

    def __call_api(self, endpoint: str, text: str, extra_params: dict = None) -> dict:
        url = self.__endpoints[endpoint]
        params = {
            "token": self.token,
            "text": text
        }
        if extra_params is not None:
            params.update(extra_params)
        response = requests.get(url, params=params)
        return response.json()

    def get_language(self, text: str):
        extra_params = {
            "clean": True
        }
        print(f"Predicting language for '{text}'...", end=" ")
        response = self.__call_api("language", text, extra_params=extra_params)
        # Parse entities
        language = {
            "lang": response["detectedLangs"][0]["lang"],
            "confidence": response["detectedLangs"][0]["confidence"]
        }
        print("Done")
        return language

    def get_sentiment(self, text: str):
        print(f"Predicting sentiment for '{text}'...", end=" ")
        response = self.__call_api("sentiment", text)
        sentiment_score = response["sentiment"]["score"]
        print(sentiment_score)
        return sentiment_score

    def get_entities(self, text: str):
        extra_params = {
            "social.hashtag": True,
            "social.mention": True,
            "include": "categories"
        }
        print(f"Extracting entities for '{text}'...", end=" ")
        response = self.__call_api("entities", text, extra_params=extra_params)
        # Parse entities
        entities = [{
            "label": entity["label"],
            "confidence": entity["confidence"],
            "uri": entity["uri"],
            "categories": entity["categories"] if "categories" in entity else []
        } for entity in response["annotations"]]
        print("Done")
        return entities

