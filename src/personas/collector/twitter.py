from typing import List
import json
import os

import tweepy
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

from common.database.connection import DatabaseConnection
from common.database.sources import SourcesDatabase
from common.database.activities import ActivitiesDatabase
from common.models.sources.twitter import TwitterDataSource
from common.models.activities.twitter import TwitterActivity


class TwitterCollector(object):
    def __init__(self,
                 consumer_key: str,
                 consumer_secret: str,
                 access_token: str,
                 access_token_secret: str) -> None:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    @staticmethod
    def __parse_user(data_source, user_data) -> TwitterDataSource:
        if user_data.default_profile_image:
            user_data.profile_image_url_https = None
        else:
            # Remove "_normal" to have full size image
            user_data.profile_image_url_https = user_data.profile_image_url_https.replace("_normal", "")

        data_source.source_user_id = user_data.id_str
        data_source.username = user_data.screen_name
        data_source.name = user_data.name
        data_source.location = user_data.location
        data_source.profile_image_url = user_data.profile_image_url_https
        data_source.description = user_data.description
        data_source.url = user_data.url
        data_source.followers_count = user_data.followers_count
        data_source.following_count = user_data.friends_count

        return data_source

    @staticmethod
    def __parse_tweet(data_source, tweet) -> TwitterActivity:
        media = tweet.entities.get("media")
        if media is None:
            media = []
        else:
            media = [media["media_url"] for media in media]

        hashtags = tweet.entities.get("hashtags")
        if hashtags is None:
            hashtags = []
        else:
            hashtags = [hashtag["text"] for hashtag in hashtags]

        urls = tweet.entities.get("urls")
        if urls is None:
            urls = []
        else:
            urls = [url["url"] for url in urls]

        return TwitterActivity(
            source_activity_id=tweet.id_str,
            data_source_id=data_source.source_id,
            text=tweet.text,
            language=tweet.lang,
            media=media,
            hashtags=hashtags,
            urls=urls,
            likes=tweet.favorite_count,
            shares=tweet.retweet_count
        )

    def get_profile_info(self, data_source: TwitterDataSource) -> TwitterDataSource:
        print(f"    Downloading profile data...", end=" ")
        try:
            user_data = self.api.get_user(user_id=data_source.source_user_id)
            print("Done")
            return self.__parse_user(data_source, user_data)
        except tweepy.error.TweepError as ex:
            print("Failed:", ex.response.text)

    def get_timeline(self, data_source: TwitterDataSource, count: int = 200) -> List[TwitterActivity]:
        print(f"    Downloading {count} tweets...", end=" ")
        try:
            tweets = []
            count_per_page = count if count < 200 else 200
            for tweet in tweepy.Cursor(self.api.user_timeline, user_id=data_source.source_user_id, trim_user=True,
                                       count=count_per_page).items(count):
                tweets.append(self.__parse_tweet(data_source, tweet))
            print("Done")
            return tweets
        except tweepy.error.TweepError as ex:
            print("Failed:", ex.response.text)
            return []


def on_connect(client: mqtt.Client, userdata, flags, rc) -> None:
    print(f"Connected with result code {str(rc)}")
    client.subscribe("collector/twitter", qos=2)


def on_message(client: mqtt.Client, userdata, msg) -> None:
    data_source_dict = json.loads(msg.payload.decode("utf-8"))
    data_source = TwitterDataSource.from_dict(data_source_dict)
    print(f"Received Twitter ID {data_source.source_user_id}...")
    # Collect data from twitter
    data_source, tweets = collect_data(data_source)
    # Save the data on DB
    db_sources = SourcesDatabase(db_connection)
    db_activities = ActivitiesDatabase(db_connection)
    db_sources.save_source(data_source)
    for tweet in tweets:
        db_activities.save_activity(tweet)
    # Send data to next queue
    data_source = json.dumps(data_source.to_dict())
    client.publish(topic="enricher/sources", payload=data_source, qos=1)
    for tweet in tweets:
        tweet = json.dumps(tweet.to_dict())
        client.publish(topic="enricher/activities", payload=tweet, qos=1)
    print("Done")


def collect_data(data_source: TwitterDataSource) -> (TwitterDataSource,TwitterActivity):
    twitter = TwitterCollector(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET,
                               TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
    data_source = twitter.get_profile_info(data_source)
    tweets = twitter.get_timeline(data_source, count=5)
    return data_source, tweets


if __name__ == "__main__":
    # Load needed parameters from environment
    load_dotenv()
    # Queue
    QUEUE_HOST = os.getenv("QUEUE_HOST")
    QUEUE_PORT = os.getenv("QUEUE_PORT")
    # DB
    DB_URL = os.getenv("DB_URL")
    # Twitter API
    TWITTER_CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
    TWITTER_CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")
    TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
    TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    if QUEUE_HOST is None or QUEUE_PORT is None:
        raise Exception("ERROR: Setup queue host and port in environment variables")
    if DB_URL is None:
        raise Exception("ERROR: Setup DB url in environment variables")
    if (TWITTER_CONSUMER_KEY is None or TWITTER_CONSUMER_SECRET is None or
            TWITTER_ACCESS_TOKEN is None or TWITTER_ACCESS_TOKEN_SECRET is None):
        raise Exception("ERROR: Setup Twitter API keys in environment variables")
    # Connect to MQTT client
    client = mqtt.Client(client_id="collector")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(host=QUEUE_HOST, port=int(QUEUE_PORT))
    # Prepare DB connection
    db_connection = DatabaseConnection(DB_URL)
    # Start the loop
    client.loop_forever()
