import json
import os

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

from common.database.connection import DatabaseConnection
from common.database.activities import ActivitiesDatabase
from personas.enrichment.activities.dandelion import DandelionAPI
from common.models.activity import ActivityEnrichments, TwitterActivity


def on_connect(client: mqtt.Client, userdata, flags, rc) -> None:
    print(f"Connected with result code {str(rc)}")
    client.subscribe(topic="enricher/activities", qos=1)


def on_message(client: mqtt.Client, userdata, msg) -> None:
    activity_dict = json.loads(msg.payload.decode("utf-8"))
    activity = TwitterActivity.from_dict(activity_dict)
    print(f"Received activity '{activity.text[:20]}', enriching...")
    # Enrich activity
    activity.enriched_properties = get_enrichments(activity)
    # Save activity in DB
    db_activities = ActivitiesDatabase(db_connection)
    db_activities.save_activity(activity)
    # Finished
    print("Done")


def get_enrichments(activity: TwitterActivity) -> ActivityEnrichments:
    # Setup Dandelion API
    dandelion = DandelionAPI(token=DANDELION_TOKEN)
    # Prepare the enrichments structure
    enrichments = ActivityEnrichments()

    # If the language is already present, use it, otherwise enrich it
    if activity.language is not None:
        enrichments.language = activity.language
    elif activity.text is not None:
        # Enrich language
        pred_lang = dandelion.get_language(activity.text)
        enrichments.language = pred_lang["lang"]

    # Proceed with next enrichments
    if activity.text is not None:
        # Extract entities
        entities = dandelion.get_entities(activity.text)
        enrichments.entities = entities
        # Extract sentiment
        sentiment = dandelion.get_sentiment(activity.text)
        enrichments.sentiment = sentiment

    return enrichments


if __name__ == "__main__":
    # Load needed parameters from environment
    load_dotenv()
    # Queue
    QUEUE_HOST = os.getenv("QUEUE_HOST")
    QUEUE_PORT = os.getenv("QUEUE_PORT")
    # DB
    DB_URL = os.getenv("DB_URL")
    # Dandelion API
    DANDELION_TOKEN = os.getenv("DANDELION_TOKEN")
    if QUEUE_HOST is None or QUEUE_PORT is None:
        raise Exception("ERROR: Setup queue host and port in environment variables")
    if DB_URL is None:
        raise Exception("ERROR: Setup DB url in environment variables")
    if DANDELION_TOKEN is None:
        raise Exception("ERROR: Setup Dandelion API token in environment variables")
    # Connect to MQTT client
    client = mqtt.Client(client_id="activities", clean_session=False)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(host=QUEUE_HOST, port=int(QUEUE_PORT))
    # Prepare DB connection
    db_connection = DatabaseConnection(DB_URL)
    # Start the loop
    client.loop_forever()


