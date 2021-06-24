from typing import List

import tweepy

from personas.models.sources.twitter import TwitterDataSource
from personas.models.activities.twitter import TwitterActivity


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
    def __parse_tweet(tweet) -> TwitterActivity:
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
            author_id=tweet.user.id_str,
            text=tweet.text,
            language=tweet.lang,
            media=media,
            hashtags=hashtags,
            urls=urls,
            likes=tweet.favorite_count,
            shares=tweet.retweet_count
        )

    def get_profile_info(self, data_source: TwitterDataSource) -> TwitterDataSource:
        print(f"Downloading profile data of Twitter user {data_source.source_user_id}...", end=" ")
        try:
            user_data = self.api.get_user(user_id=data_source.source_user_id)
            print("Done")
            return self.__parse_user(data_source, user_data)
        except tweepy.error.TweepError as ex:
            print("Failed:", ex.response.text)

    def get_timeline(self, user_id, count: int = 200) -> List[TwitterActivity]:
        print(f"Downloading {count} tweets of Twitter user {user_id}...", end=" ")
        try:
            tweets = []
            count_per_page = count if count < 200 else 200
            for tweet in tweepy.Cursor(self.api.user_timeline, user_id=user_id, trim_user=True,
                                       count=count_per_page).items(count):
                tweets.append(self.__parse_tweet(tweet))
            print("Done")
            return tweets
        except tweepy.error.TweepError as ex:
            print("Failed:", ex.response.text)
