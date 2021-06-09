from personas.classificator.activities.dandelion import DandelionAPI
from personas.models.activities.twitter import TwitterActivity
from personas.models.activities.enrichments import ActivityEnrichments
from personas.classificator.activities.secrets import DANDELION_TOKEN

if __name__ == "__main__":
    # Activity to analyze
    activity = TwitterActivity(activity_id="abc", text="I'm a computer scientist and I love programming!")
    # Setup Dandelion API
    dandelion = DandelionAPI(token=DANDELION_TOKEN)
    # Prepare the enrichments structure
    enrichments = ActivityEnrichments()

    # Enrich language
    if activity.language is not None:
        enrichments.language = activity.language
    else:
        pred_lang = dandelion.get_language(activity.text)
        enrichments.language = pred_lang["lang"]

    # Extract entities and topics
    pred_entities = dandelion.get_entities(activity.text)
    entities = [entity["label"] for entity in pred_entities]
    enrichments.entities = set(entities)

    topics = []
    for entity in pred_entities:
        topics.extend(entity["categories"])
    enrichments.topics = set(topics)

    # Get sentiment
    sentiment = dandelion.get_sentiment(activity.text)
    enrichments.sentiment = sentiment

    # Put everything in the activity
    activity.enriched_properties = enrichments
    print(activity.enriched_properties)


