import argparse

from personas.collector.twitter import TwitterCollector
from personas.collector.secrets import \
    TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET

if __name__ == "__main__":
    # Setup argparser
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source", required=True)
    parser.add_argument("-u", "--user_id", required=True)
    args = parser.parse_args()

    # Get the user IDs from command line
    source_name: str = args.source
    user_id: str = args.user_id

    if source_name.lower() == "twitter":
        # Get API keys
        twitter = TwitterCollector(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET,
                                   TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)

        # Get profile info and activities
        print("=" * 80)
        twitter_source = twitter.get_user(user_id)
        tweets = twitter.get_timeline(user_id, count=20)

        # Print them
        print()
        print(twitter_source)
        print(f"Retrieved {len(tweets)} activities")
        print(tweets[0])
        print("=" * 80)
