from unittest import TestCase

from personas.enricher.activities.dandelion import DandelionAPI


class TestDandelionAPI(TestCase):
    def test_get_sentiment(self):
        token = "xxxxxxx"
        api = DandelionAPI(token)
        text = "Questo testo è neutrale"
        sentiment_score = api.get_sentiment(text)
        self.assertEqual(0.0, sentiment_score)

    def test_get_entities(self):
        token = "xxxxxxx"
        api = DandelionAPI(token)
        text = "An apple is better than an orange"
        entities = api.get_entities(text)
        self.assertEqual(len(entities), 2)

    def test_get_language(self):
        token = "xxxxxxx"
        api = DandelionAPI(token)
        text = "Questo è un tweet #thisistwitter"
        lang = api.get_language(text)
        self.assertEqual(lang["lang"], "it")