import json
import os

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

from common.database.connection import DatabaseConnection
from common.database.sources import SourcesDatabase
from common.database.activities import ActivitiesDatabase
from common.models.enrichments import Enrichments
from common.models.data_source import TwitterDataSource
from personas.enrichment.sources.m3_wrapper import CustomM3Inference
from personas.enrichment.sources.namsor import NamsorAPI
from personas.enrichment.sources.tapoi import Tapoi
from personas.enrichment.utils.text_cleaner import clean_text


def on_connect(client: mqtt.Client, userdata, flags, rc) -> None:
    print(f"Connected with result code {str(rc)}")
    client.subscribe(topic="enricher/sources", qos=1)


def on_message(client: mqtt.Client, userdata, msg) -> None:
    data_source_dict = json.loads(msg.payload.decode("utf-8"))
    if data_source_dict["source_name"] == "twitter":
        data_source = TwitterDataSource.from_dict(data_source_dict)
    else:
        raise ValueError("ERROR: Received not supported data source")
    print(f"Received data source {data_source.source_id}...", end=" ")
    # Enrich data source
    data_source.attributes = get_enrichments(data_source)
    # Save data
    db_sources = SourcesDatabase(db_connection)
    db_sources.save_source(data_source)
    # Finished
    print(data_source.attributes)


def get_enrichments(data_source: TwitterDataSource) -> Enrichments:
    enriched_attributes = Enrichments()

    if data_source.name:
        enriched_attributes.name = clean_text(data_source.name)

    # If a profile picture and other data is available, try to predict demographics from it
    if data_source.profile_image_url and data_source.description and data_source.username and data_source.name:
        m3 = CustomM3Inference()
        pred = m3.predict(data_source)
        if pred is not None:
            enriched_attributes.age = get_max_tuple_from_dict(pred["age"])
            enriched_attributes.gender = get_max_tuple_from_dict(pred["gender"])
            enriched_attributes.type_ = get_max_tuple_from_dict(pred["org"])
        else:
            namsor = NamsorAPI(key=NAMSOR_TOKEN)
            # Predict type (human vs brand)
            enriched_attributes.type_ = namsor.predict_type(enriched_attributes.name)
            # Predict gender
            enriched_attributes.gender = namsor.predict_gender(enriched_attributes.name)
    # Else, only predict using name
    elif data_source.name:
        namsor = NamsorAPI(key=NAMSOR_TOKEN)
        # Predict type (human vs brand)
        enriched_attributes.type_ = namsor.predict_type(enriched_attributes.name)
        # Predict gender
        enriched_attributes.gender = namsor.predict_gender(enriched_attributes.name)

    # Now collect all activities from DB to enrich further
    db_activities = ActivitiesDatabase(db_connection)
    activities = db_activities.get_activities_of_data_source(data_source.source_id)
    language_map, avg_sentiment, entity_map = {}, {}, {}
    for activity in activities:
        if activity.enriched_properties is not None:
            # Count each language
            lang = activity.enriched_properties.language
            language_map[lang] = language_map.get(lang, 0) + 1
            # Average sentiment score
            avg_sentiment["avg"] = (
                ((avg_sentiment.get("avg", 0) * avg_sentiment.get("count", 0)) +
                activity.enriched_properties.sentiment) / (avg_sentiment.get("count", 0) + 1)
            )
            avg_sentiment["count"] = avg_sentiment.get("count", 0) + 1
            # Dictionary of entities
            for entity in activity.enriched_properties.entities:
                entity_map[entity] = entity_map.get(entity, 0) + 1
    if language_map:
        enriched_attributes.pref_language = get_max_tuple_from_dict(language_map)[0]
    if avg_sentiment:
        enriched_attributes.attitude = avg_sentiment["avg"]
    if entity_map:
        tapoi = Tapoi()
        enriched_attributes.interests = tapoi.get_interests(entity_map)

    return enriched_attributes


def get_max_tuple_from_dict(dct: dict) -> tuple:
    max_key = max(dct, key=dct.get)
    return max_key, dct[max_key]


if __name__ == "__main__":
    # Load needed parameters from environment
    load_dotenv()
    # Queue
    QUEUE_HOST = os.getenv("QUEUE_HOST")
    QUEUE_PORT = os.getenv("QUEUE_PORT")
    # DB
    DB_URL = os.getenv("DB_URL")
    # Dandelion API
    NAMSOR_TOKEN = os.getenv("NAMSOR_TOKEN")
    if QUEUE_HOST is None or QUEUE_PORT is None:
        raise Exception("ERROR: Setup queue host and port in environment variables")
    if DB_URL is None:
        raise Exception("ERROR: Setup DB url in environment variables")
    if NAMSOR_TOKEN is None:
        raise Exception("ERROR: Setup Namsor API token in environment variables")
    # Connect to MQTT client
    client = mqtt.Client(client_id="sources", clean_session=False)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(host=QUEUE_HOST, port=int(QUEUE_PORT))
    # Prepare DB connection
    db_connection = DatabaseConnection(DB_URL)
    # Start the loop
    client.loop_forever()
