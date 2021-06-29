import requests
import json
from typing import List


class Tapoi(object):
    def __init__(self):
        with open("category_map.json", mode="r") as infile:
            self.category_map = json.load(infile)

    @staticmethod
    def __call_api(entityMap: dict):
        url = "http://evaluator.tapoi.me:80/evaluation/model/fa4c3c4e-32f5-46af-aa31-dfc87b6d8680/"
        payload = {
            "entityMap": entityMap,
            "evaluation_type": "providedEntityMap",
            "norm_scale": 1,
            "power_factor": 1,
            "exponential_factor": 1,
            "include_matching_entries": False,
            "include_matching_entries_evaluation": False
        }
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers, json=payload).json()
        return response

    def get_interests(self, entity_map: dict) -> dict:
        response = self.__call_api(entity_map)
        interests = {}
        for interest in response["evaluation"]:
            interests[self.category_map[interest]] = response["evaluation"][interest]
        return interests
