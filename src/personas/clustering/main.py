from typing import List
import os
import argparse

from dotenv import load_dotenv
import pandas as pd
import numpy as np
from sklearn.metrics import silhouette_score
from sklearn_extra.cluster._k_medoids import KMedoids

from common.database.connection import DatabaseConnection
from common.database.users import UsersDatabase
from common.database.sources import SourcesDatabase
from common.database.personas import PersonasDatabase
from common.models.persona import Persona
from common.models.enrichments import Enrichments
from src.personas.clustering.generator import PersonaGenerator


def distance_matrix(data: List[dict]) -> np.ndarray:
    size = len(data)
    matrix = np.empty([size, size])
    for i in range(0, size):
        for j in range(0, size):
            if i == j:
                matrix[i][j] = 0
            else:
                matrix[i][j] = compute_distance(data[i], data[j])
    return matrix


def compute_distance(user1: dict, user2: dict) -> float:
    distances = np.zeros(10)
    try:
        # Gender: categorical, simply add 1 if different
        distances[0] += user1["gender"] != user2["gender"]
        # Age: categorical, the more the difference, the more the distance
        if user1["age"] is None and user2["age"] is None:
            pass
        elif user1["age"] is None or user2["age"] is None:
            distances[1] += 1
        else:
            try:
                ages_map = {"<=18": 0, "19-29": 1, "30-39": 2, ">=40": 3}
                distances[1] += abs(ages_map[user1["age"]] - ages_map[user2["age"]]) / 3
            except KeyError:
                pass
        # Type: categorical
        distances[2] += user1["type_"] != user2["type_"]
        # Language: categorical
        distances[3] += user1["pref_language"] != user2["pref_language"]
        # Family status: categorical
        distances[4] += user1["family_status"] != user2["family_status"]
        # Children: categorical
        distances[5] += user1["has_children"] != user2["has_children"]
        # Personality: 4 letters, count how many are different (weighted double)
        if user1["personality"] is None and user2["personality"] is None:
            pass
        elif user1["personality"] is None or user2["personality"] is None:
            distances[6] += 1
        else:
            for i in range(0, 4):
                distances[6] += user1["personality"][i] != user2["personality"][i]
        # Interests: Jaccard distance (weighted double)
        sum = 0
        if user1["interests"] is None and user2["interests"] is None:
            pass
        elif user1["interests"] is None or user2["interests"] is None:
            distances[7] += 1
        else:
            for interest in user1["interests"]:
                sum += abs(user1["interests"][interest] - user2["interests"][interest])
            distances[7] += 3*(sum/len(user1["interests"]))
        # Channels: Jaccard distance
        user1_channels = set(user1["channels"]) if user1["channels"] is not None else set()
        user2_channels = set(user2["channels"]) if user2["channels"] is not None else set()
        if len(user1_channels) > 0 or len(user2_channels) > 0:
            distances[8] += 1 - len(user1_channels.intersection(user2_channels)) / len(user1_channels.union(user2_channels))
        # Attitude
        distances[9] += abs(user1["attitude"]-user2["attitude"]) / 2
        # Now compute average
        return np.mean(distances, axis=0)
    except KeyError:
        raise KeyError("Trying to cluster users on missing keys")


if __name__ == "__main__":
    load_dotenv()
    DB_URL = os.getenv("DB_URL")
    conn = DatabaseConnection(DB_URL)

    db_users = UsersDatabase(conn)
    db_sources = SourcesDatabase(conn)
    # Get brand from cli args
    parser = argparse.ArgumentParser()
    parser.add_argument("brand", help="The ID of the brand to generate personas for", type=str)
    brand_id = parser.parse_args().brand
    users = db_users.get_users_of_brand(brand_id)
    if not users:
        raise ValueError("ERROR: Brand not found")
    # Populate user attributes based on its data sources
    for user in users:
        sources = db_sources.get_sources_of_user(user.user_id)
        # In this demo, only Twitter is supported
        user.attributes = sources[0].attributes

    # Many attributes are tuple, where the second value is the confidence. Keep only the first value
    data = [user.attributes.to_dict() for user in users]
    for user in data:
        if user["gender"]:
            user["gender"] = user["gender"][0]
        if user["age"]:
            user["age"] = user["age"][0]
        if user["type_"]:
            user["type_"] = user["type_"][0]

    # Create dataframe
    df_users = pd.DataFrame(data)

    # Drop irrelevant columns
    df_users.drop("name", axis=1, inplace=True)

    # Precompute custom distance matrix
    dist_matrix = distance_matrix(data)

    # Try different number of clusters to find the best one
    scores = []
    max_clusters = 20
    for i in range(2, max_clusters):
        model = KMedoids(n_clusters=i, metric="precomputed", method="pam")
        labels = model.fit_predict(dist_matrix)
        scores.append(silhouette_score(dist_matrix, labels, metric="precomputed"))

    # Choose the number of clusters with max score
    n_cluster = np.argmax(scores) + 2
    model = KMedoids(n_clusters=n_cluster, metric="precomputed", method="pam")
    labels = model.fit_predict(dist_matrix)

    medoids = []
    # Print the medoids for each cluster
    for i, index in enumerate(model.medoid_indices_):
        medoids.append(df_users.iloc[[index]].to_dict(orient="records")[0])
        print(f"CLUSTER {i}:")
        print(medoids[i]["interests"])
        print("="*50)

    # Generate personas
    pg = PersonaGenerator()
    db_personas = PersonasDatabase(conn)
    for medoid in medoids:
        persona = Persona(brand_id=brand_id, attributes=Enrichments.from_dict(medoid))
        persona.name = pg.get_name(persona.attributes.gender)
        persona.photo = pg.get_image(persona.attributes.gender)
        db_personas.save_persona(persona)
        print(persona.to_dict())

