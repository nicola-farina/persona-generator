from os import getenv

from dotenv import load_dotenv

from personas.collector.twitter import TwitterCollector
from personas.common.user import Brand
from personas.common.database import Database

if __name__ == "__main__":
    # TWITTER
    # Get API keys
    load_dotenv()
    consumer_key = getenv("TWITTER_CONSUMER_KEY")
    consumer_secret = getenv("TWITTER_CONSUMER_SECRET")
    access_token = getenv("TWITTER_ACCESS_TOKEN")
    access_token_secret = getenv("TWITTER_ACCESS_TOKEN_SECRET")

    twitter = TwitterCollector(consumer_key, consumer_secret, access_token, access_token_secret)

    # Create brand
    uhopper_id = "223439979"
    uhopper = Brand(uhopper_id)

    # Get followers
    twitter.get_followers(uhopper)

    # Get the timeline of each follower
    for user in uhopper.followers:
        twitter.get_timeline(user)

    # Save everything in database
    db = Database()
    db.save_brand(uhopper)

