import argparse
import json

import paho.mqtt.client as mqtt

from personas.models.sources.twitter import TwitterDataSource
from personas.collector.twitter import TwitterCollector
from personas.collector.secrets import \
    TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET


def on_connect(client: mqtt.Client, userdata, flags, rc) -> None:
    print(f"Connected with result code {str(rc)}")
    client.subscribe("collector/twitter")


def on_message(client: mqtt.Client, userdata, msg) -> None:
    data_source_dict = json.loads(msg.payload.decode("utf-8"))
    data_source = TwitterDataSource.from_dict(data_source_dict)
    print(f"Received Twitter ID {data_source.source_user_id}...")

    # Collect data from twitter
    twitter = TwitterCollector(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET,
                               TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
    data_source = twitter.get_profile_info(data_source)
    tweets = twitter.get_timeline(data_source.source_user_id, count=20)

    # Send data to next queue
    # First, the data source
    data_source = json.dumps(data_source.to_dict())
    client.publish("classificator/sources", data_source)
    # Then, activities one by one
    if tweets:
        for tweet in tweets:
            tweet = json.dumps(tweet.to_dict())
            client.publish("classificator/activities", tweet)
    print("Done")


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
