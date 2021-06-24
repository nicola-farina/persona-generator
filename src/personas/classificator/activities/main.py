import argparse

import paho.mqtt.client as mqtt
import json

from personas.classificator.activities.dandelion import DandelionAPI
from personas.models.activities.enrichments import ActivityEnrichments
from personas.models.activities.twitter import TwitterActivity
from personas.classificator.activities.secrets import DANDELION_TOKEN


def on_connect(client: mqtt.Client, userdata, flags, rc) -> None:
    print(f"Connected with result code {str(rc)}")
    client.subscribe("classificator/activities")


def on_message(client: mqtt.Client, userdata, msg) -> None:
    activity_dict = json.loads(msg.payload.decode("utf-8"))
    activity = TwitterActivity.from_dict(activity_dict)
    print(f"Received activity...")

    # Enrich activity
    activity.enriched_properties = get_enrichments(activity)

    # Send data to next queue
    print(activity)
    activity = json.dumps(activity.to_dict())
    client.publish("classificator/enriched_activities", activity)
    print("Done")


def get_enrichments(activity: TwitterActivity) -> ActivityEnrichments:
    # Setup Dandelion API
    dandelion = DandelionAPI(token=DANDELION_TOKEN)
    # Prepare the enrichments structure
    enrichments = ActivityEnrichments()

    # Enrich language
    if activity.language is not None:
        enrichments.language = activity.language
    elif activity.text is not None:
        pred_lang = dandelion.get_language(activity.text)
        enrichments.language = pred_lang["lang"]

    # Extract entities and topics
    if activity.text is not None:
        pred_entities = dandelion.get_entities(activity.text)
        entities = [entity["label"] for entity in pred_entities]
        enrichments.entities = entities

        topics = []
        for entity in pred_entities:
            topics.extend(entity["categories"])
        enrichments.topics = topics

    # Get sentiment
    if activity.text is not None:
        sentiment = dandelion.get_sentiment(activity.text)
        enrichments.sentiment = sentiment

    return enrichments


if __name__ == "__main__":
    # Setup argparser
    parser = argparse.ArgumentParser()
    parser.add_argument("--host-mqtt", required=True)
    parser.add_argument("--port-mqtt", required=True)
    args = parser.parse_args()
    host = args.host_mqtt
    port = int(args.port_mqtt)

    # Connect to MQTT client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(host=host, port=port)

    # Start the loop
    client.loop_forever()


