from typing import List, Union

import tweepy

from personas.common.user import User, Brand
from personas.common.post import Post


class TwitterCollector(object):

    def __init__(self,
                 consumer_key: str,
                 consumer_secret: str,
                 access_token: str,
                 access_token_secret: str) -> None:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)

    @staticmethod
    def __parse_user(user) -> User:
        if user.default_profile_image:
            user.profile_image_url_https = None

        return User(
            id_=user.id_str,
            name=user.name,
            location=user.location,
            profile_image_url=user.profile_image_url_https,
            biography=user.description,
            site=user.url,
            followers_count=user.followers_count,
            following_count=user.friends_count
        )

    @staticmethod
    def __parse_tweet(tweet) -> Post:
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

        return Post(
            id_=tweet.id_str,
            author_id=tweet.user.id_str,
            text=tweet.text,
            media=media,
            hashtags=hashtags,
            urls=urls,
            language=tweet.lang,
            likes=tweet.favorite_count,
            shares=tweet.retweet_count,
        )

    def get_followers(self, user: Union[User, Brand]) -> None:
        print(f"Downloading followers of Twitter user {user.id_}...", end=" ")
        followers = self.api.followers(user_id=user.id_, skip_status=True, include_user_entities=False)
        print("Done")

        user.followers = []
        for follower in followers:
            user.followers.append(self.__parse_user(follower))

    def get_timeline(self, user: Union[User, Brand]) -> None:
        print(f"Downloading timeline of Twitter user {user.id_}...", end=" ")
        try:
            tweets = self.api.user_timeline(user_id=user.id_, trim_user=True)
            print("Done")

            user.posts = []
            for tweet in tweets:
                user.posts.append(self.__parse_tweet(tweet))
        except tweepy.error.TweepError:
            print("Failed. User has protected tweets")
