import argparse
import json

import paho.mqtt.client as mqtt

from personas.models.sources.twitter import TwitterDataSource
from personas.models.attributes import Attributes
from personas.classificator.sources.m3 import CustomM3Inference
from personas.classificator.sources.namsor import NamsorAPI
from personas.classificator.sources.secrets import NAMSOR_API_KEY
from personas.classificator.utils.text_cleaner import clean_text

from personas.database.connection import DatabaseConnection
from personas.database.sources import SourcesDatabase


def on_connect(client: mqtt.Client, userdata, flags, rc) -> None:
    print(f"Connected with result code {str(rc)}")
    client.subscribe("classificator/sources")


def on_message(client: mqtt.Client, userdata, msg) -> None:
    data_source_dict = json.loads(msg.payload.decode("utf-8"))
    data_source = TwitterDataSource.from_dict(data_source_dict)
    print(f"Received data source of user {data_source.username}...")

    # Enrich data source
    data_source.attributes = get_enrichments(data_source)
    print("Enriched properties:", data_source.attributes)

    # Save data
    conn = DatabaseConnection()
    conn.init("localhost", 6379, 0)
    db = SourcesDatabase(conn)
    db.save_source(data_source)


def get_max_tuple_from_dict(dct: dict) -> tuple:
    max_key = max(dct, key=dct.get)
    return max_key, dct[max_key]


def get_enrichments(data_source: TwitterDataSource) -> Attributes:
    enriched_attributes = Attributes()

    if data_source.name:
        enriched_attributes.name = clean_text(data_source.name)

    # If a profile picture and other data is available, try to predict demographics from it
    if data_source.profile_image_url and data_source.description and data_source.username and data_source.name:
        m3 = CustomM3Inference()
        pred = m3.predict(data_source)
        enriched_attributes.age = get_max_tuple_from_dict(pred["age"])
        enriched_attributes.gender = get_max_tuple_from_dict(pred["gender"])
        enriched_attributes.type_ = get_max_tuple_from_dict(pred["org"])

    # Else, only predict by name
    elif data_source.name:
        namsor = NamsorAPI(key=NAMSOR_API_KEY)
        # Predict type (human vs brand)
        enriched_attributes.type_ = namsor.predict_type(enriched_attributes.name)
        # Predict gender
        enriched_attributes.gender = namsor.predict_gender(enriched_attributes.name)

    return enriched_attributes


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
