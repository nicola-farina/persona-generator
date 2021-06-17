import argparse
import json

import paho.mqtt.client as mqtt

from personas.collector.twitter import TwitterCollector
from personas.collector.secrets import \
    TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET


def on_connect(client: mqtt.Client, userdata, flags, rc) -> None:
    print(f"Connected with result code {str(rc)}")
    client.subscribe("collector/twitter")


def on_message(client: mqtt.Client, userdata, msg) -> None:
    twitter_user_id = msg.payload.decode("utf-8")
    print(f"Received Twitter ID {twitter_user_id}...")

    # Collect data from twitter
    twitter = TwitterCollector(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET,
                               TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
    twitter_source = twitter.get_user(twitter_user_id)
    tweets = twitter.get_timeline(twitter_user_id, count=20)

    # Send data to next queue
    # First, the data source
    twitter_source = json.dumps(twitter_source.to_dict())
    client.publish("classificator/sources", twitter_source)
    # Then, activities one by one
    for tweet in tweets:
        tweet = json.dumps(tweet.to_dict())
        client.publish("classificator/activities", tweet)
    print("Done")


if __name__ == "__main__":
    # Setup argparser
    parser = argparse.ArgumentParser()
    parser.add_argument("--host_mqtt", required=True)
    parser.add_argument("--port_mqtt", required=True)
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
