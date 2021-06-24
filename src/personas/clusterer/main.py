from typing import List


import pandas as pd
import numpy as np
from sklearn.metrics import silhouette_score
from sklearn_extra.cluster._k_medoids import KMedoids
import matplotlib.pyplot as plt

from personas.database.connection import DatabaseConnection
from personas.database.users import UsersDatabase
from personas.database.sources import SourcesDatabase


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
    distances = np.zeros(9)
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
        # Job: TODO
        # Personality: 4 letters, count how many are different (weighted double)
        if user1["personality"] is None and user2["personality"] is None:
            pass
        elif user1["personality"] is None or user2["personality"] is None:
            distances[6] += 1
        else:
            for i in range(0, 4):
                distances[6] += user1["personality"][i] != user2["personality"][i]
        # Interests: Jaccard distance (weighted double)
        user1_interests = set(user1["interests"]) if user1["interests"] is not None else set()
        user2_interests = set(user2["interests"]) if user2["interests"] is not None else set()
        if len(user1_interests) > 0 or len(user2_interests) > 0:
            distances[7] += 2*(1 - len(user1_interests.intersection(user2_interests)) / len(user1_interests.union(user2_interests)))
        # Channels: Jaccard distance
        user1_channels = set(user1["channels"]) if user1["channels"] is not None else set()
        user2_channels = set(user2["channels"]) if user2["channels"] is not None else set()
        if len(user1_channels) > 0 or len(user2_channels) > 0:
            distances[8] += 1 - len(user1_channels.intersection(user2_channels)) / len(user1_channels.union(user2_channels))
        # Now compute average
        return np.mean(distances, axis=0)
    except KeyError:
        raise KeyError("Trying to cluster users on missing keys")


if __name__ == "__main__":
    conn = DatabaseConnection()
    conn.init("localhost", 6379, 0)

    db_users = UsersDatabase(conn)
    db_sources = SourcesDatabase(conn)
    # Get users of a brand
    users = db_users.get_users_of_brand("3fa0099b1dc648e7b1f7d21e2ef906e8")
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
    print(df_users)

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

    # Plot silhuette score
    plt.plot(range(2, max_clusters), scores)
    plt.xlabel("Number of clusters")
    plt.ylabel("Avg Silhuette Score (more is better)")
    plt.xticks(range(2, max_clusters))
    plt.show()

    # Choose the number of clusters with max score
    n_cluster = np.argmax(scores)+2
    model = KMedoids(n_clusters=n_cluster, metric="precomputed", method="pam")
    labels = model.fit_predict(dist_matrix)

    medoids = []
    # Print the medoids for each cluster
    for i, index in enumerate(model.medoid_indices_):
        medoids.append(df_users.iloc[[index]])
        print(f"CLUSTER {i}:")
        print(medoids[i])
        print("="*50)

    # Generate personas
