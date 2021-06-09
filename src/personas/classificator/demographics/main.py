import pprint as pp

from personas.models.sources.twitter import TwitterDataSource
from personas.models.attributes import Attributes
from personas.classificator.demographics.m3 import CustomM3Inference
from personas.classificator.demographics.namsor import NamsorAPI
from personas.classificator.demographics.secrets import NAMSOR_API_KEY
from personas.classificator.utils.text_cleaner import clean_text


def __get_max_tuple_from_dict(dct: dict) -> tuple:
    max_key = max(dct, key=dct.get)
    return max_key, dct[max_key]


if __name__ == "__main__":

    data_source = TwitterDataSource(
        source_user_id="abc", name="Daniele Miorandi", username="DanieleMiorandi",
        profile_image_url="https://pbs.twimg.com/profile_images/1202550189652877313/QfRPlfqU_400x400.jpg",
        description="innovator, outdoor sports addicted, in love with food and arts. ceo @uhopper- tweets on "
                    "innovation, AI, startups and science")

    enriched_attributes = Attributes()

    if data_source.name:
        enriched_attributes.name = clean_text(data_source.name)

    # If a profile picture and other data is available, try to predict demographics from it
    if data_source.profile_image_url and data_source.description and data_source.username and data_source.name:
        m3 = CustomM3Inference()
        pred = m3.predict(data_source)
        enriched_attributes.age = __get_max_tuple_from_dict(pred["age"])
        enriched_attributes.gender = __get_max_tuple_from_dict(pred["gender"])
        enriched_attributes.type_ = __get_max_tuple_from_dict(pred["org"])

    # Else, only predict by name
    elif data_source.name:
        namsor = NamsorAPI(key=NAMSOR_API_KEY)
        # Predict type (human vs brand)
        enriched_attributes.type_ = namsor.predict_type(enriched_attributes.name)
        # Predict gender
        enriched_attributes.gender = namsor.predict_gender(enriched_attributes.name)

    data_source.attributes = enriched_attributes
    pp.pprint(data_source.attributes)