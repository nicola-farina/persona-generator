import requests
import os
from typing import Union

from PIL import Image
from m3inference import M3Inference, get_lang

from common.models.sources.twitter import TwitterDataSource


class CustomM3Inference(object):
    def __init__(self):
        self.__m3 = M3Inference(skip_logging=True)

    @staticmethod
    def __download_image(url: str) -> Union[str, None]:
        filename = "image." + url.split('.')[-1]
        img_folder = "m3_img"
        if not os.path.exists(img_folder):
            os.mkdir(img_folder)
        img_path = os.path.join(img_folder, filename)

        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                img = Image.open(response.raw).convert("RGB")
                img = img.resize((224, 224))
                img.save(img_path)
                return img_path
            else:
                return None
        except requests.exceptions.RequestException as e:
            print("Bad URL or could not connect.")
            return None

    def predict(self, data_source: TwitterDataSource) -> Union[dict, None]:
        # Get language from description
        lang = get_lang(data_source.description)
        # Download image
        img_path = self.__download_image(data_source.profile_image_url)
        if img_path is not None:
            # Prepare object for M3Inference
            m3_input = {
                "id": data_source.source_user_id,
                "name": data_source.name,
                "screen_name": data_source.username,
                "description": data_source.description,
                "lang": lang,
                "img_path": img_path
            }
            # Predict
            pred = self.__m3.infer([m3_input])[data_source.source_user_id]
            pred["org"]["human"] = pred["org"].pop("non-org")
            pred["org"]["brand"] = pred["org"].pop("is-org")
            # Remove image file
            os.remove(img_path)
            return pred
        else:
            print("Could not predict the image.")
            return None
