from typing import List

import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


def convert_wikipedia_pageids_to_english_urls(lang: str, pageids: List[str]) -> List[str]:
    if lang not in DandelionAPI.SUPPORTED_LANGUAGES or len(pageids) == 0:
        return []
    # Use the endpoint of the right language
    endpoint = f"https://{lang}.wikipedia.org/w/api.php"
    # Prepare a "|" separated list of titles to convert
    arg_pageids = ""
    for pageid in pageids:
        arg_pageids = arg_pageids + str(pageid) + "|"
    arg_pageids = arg_pageids[:-1]
    # Prepare args
    args = {
        "action": "query",
        "format": "json",
        "prop": "langlinks",
        "pageids": arg_pageids,
        "llprop": "url",
        "lllang": "en",
    }
    # Send request
    s = requests.Session()
    retries = Retry(total=5, backoff_factor=0.1)
    s.mount("https://", HTTPAdapter(max_retries=retries))
    try:
        response = s.get(endpoint, params=args)
    except requests.exceptions.ConnectionError:
        print("Cannot reach Wikipedia API for conversion")
        return []

    # Check response
    if response.status_code == 200:
        response = response.json()
        urls = []
        for page in response["query"]["pages"].values():
            try:
                urls.append(page["langlinks"][0]["url"])
            except KeyError:
                continue
        return urls
    else:
        return []


class DandelionAPI(object):

    SUPPORTED_LANGUAGES = [
        "de", "en", "es", "fr", "it", "ot", "ru", "af", "sq", "ar",
        "bn", "bg", "hr", "cs", "da", "nl", "et", "fi", "gu", "he",
        "hi", "hu", "id", "ja", "kn", "ko", "lv", "lt", "mk", "ml",
        "mr", "el", "ne", "no", "pa", "fa", "pl", "ro", "sk", "sl",
        "sw", "sv", "tl", "ta", "te", "th", "tr", "uk", "ur", "vi"
    ]

    __endpoints = {
        "language": "https://api.dandelion.eu/datatxt/li/v1",
        "sentiment": "https://api.dandelion.eu/datatxt/sent/v1",
        "entities": "https://api.dandelion.eu/datatxt/nex/v1"
    }

    def __init__(self,
                 token: str):
        self.token = token

    def __call_api(self, endpoint: str, text: str, extra_params: dict = None) -> requests.Response:
        url = self.__endpoints[endpoint]
        params = {
            "token": self.token,
            "text": text
        }
        if extra_params is not None:
            params.update(extra_params)
        response = requests.get(url, params=params)
        return response

    def get_language(self, text: str):
        extra_params = {
            "clean": True
        }
        print(f"    Predicting language...", end=" ")
        response = self.__call_api("language", text, extra_params=extra_params)
        if response.status_code == 200:
            response = response.json()
            language = response["detectedLangs"][0]["lang"]
            print("Done")
            return language
        else:
            return "und"

    def get_sentiment(self, text: str):
        print(f"    Predicting sentiment...", end=" ")
        response = self.__call_api("sentiment", text)
        if response.status_code == 200:
            response = response.json()
            sentiment_score = response["sentiment"]["score"]
            print("Done")
            return sentiment_score
        else:
            return 0.

    def get_entities(self, text: str):
        extra_params = {
            "social.hashtag": True,
            "social.mention": True,
            "include": "categories"
        }
        print(f"    Extracting entities...", end=" ")
        response = self.__call_api("entities", text, extra_params=extra_params)
        if response.status_code == 200:
            response = response.json()
            lang = response["lang"]
            # Parse entities
            if lang != "en":
                # Convert wikipedia pages to english
                pageids = [entity["id"] for entity in response["annotations"]]
                entities = convert_wikipedia_pageids_to_english_urls(lang, pageids)
            else:
                entities = [entity["uri"] for entity in response["annotations"]]
            print("Done")
            return entities
        else:
            print("Couldn't extract")
            return []
