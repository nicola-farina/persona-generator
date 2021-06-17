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
    def __parse_user(data) -> TwitterDataSource:
        if data.default_profile_image:
            data.profile_image_url_https = None

        return TwitterDataSource(
            source_user_id=data.id_str,
            username=data.screen_name,
            attributes=None,
            name=data.name,
            location=data.location,
            profile_image_url=data.profile_image_url_https,
            description=data.description,
            url=data.url,
            followers_count=data.followers_count,
            following_count=data.friends_count
        )

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

    def get_user(self, user_id: str) -> TwitterDataSource:
        print(f"Downloading profile data of Twitter user {user_id}...", end=" ")
        try:
            user_data = self.api.get_user(user_id=user_id)
            print("Done")
            return self.__parse_user(user_data)
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
