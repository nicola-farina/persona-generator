import os

from dotenv import load_dotenv

from personas.common.database import Database
from personas.classificator.name.namsor import NameClassifier
from personas.classificator.timeline.analyzer import TimelineAnalyzer
from personas.classificator.utils.text_cleaner import remove_symbols, remove_emoji, remove_leading_trailing_spaces

if __name__ == "__main__":
    # Get secrets from environment
    load_dotenv()
    namsor_api_key = os.getenv("NAMSOR_API_KEY")

    # Get the followers of a given brand from the database
    db = Database()

    uhopper_id = "223439979"
    brand = db.get_brand(uhopper_id)

    followers = brand.followers
    print(followers[0].posts)

    # Classification
    name_classifier = NameClassifier(namsor_api_key)
    for user in followers:
        # Clean name
        user.name = remove_emoji(user.name)
        user.name = remove_symbols(user.name)
        user.name = remove_leading_trailing_spaces(user.name)
        # Get type
        user.type = name_classifier.predict_type(user.name)["predicted_type"]
        # Get gender
        if user.type == "anthroponym":
            user.gender = name_classifier.predict_gender(user.name)["predicted_gender"]

        # Get language
        user.pref_language = TimelineAnalyzer.get_preferred_language(user.posts)

    # Save enriched users to another database
    db = Database(db=1)
    db.save_brand_followers(brand)
