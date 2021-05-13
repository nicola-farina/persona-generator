import pandas as pd
import numpy as np
from kmodes.kmodes import KModes
from kneed import KneeLocator
from sklearn.preprocessing import StandardScaler, LabelEncoder

from personas.common.database import Database

if __name__ == "__main__":
    db = Database(db=1)

    uhopper_id = "223439979"
    brand = db.get_brand(uhopper_id)

    users = brand.followers

    # Create users dataframe
    users_dict = [user.__dict__ for user in users]
    df_users = pd.DataFrame(users_dict)

    # List of relevant columns
    cols_to_drop = ["id_", "name", "location", "profile_image_url", "biography", "site", "followers_count",
                    "following_count", "posts", "type_", "cluster"]
    cols_to_cluster = [col for col in df_users.columns if col not in cols_to_drop]

    # Drop rows with brand type
    df_users = df_users[df_users["type_"] != "brand-name"]

    # Drop rows which contain "NaN" values
    df_users.fillna(value=np.nan, inplace=True)
    df_users.dropna(inplace=True, subset=cols_to_cluster)

    # PREPARE DATAFRAME FOR CLUSTERING
    df_cluster = df_users.copy(deep=True)

    # Replace posts with the number of posts
    df_cluster["posts"] = [len(posts) for posts in df_cluster["posts"]]

    # Categorize users into active and popular
    df_cluster["active"] = [1 if posts >= 100 else 0 for posts in df_cluster["posts"]]
    df_cluster["popular"] = [1 if int(followers) >= 100 else 0 for followers in df_cluster["followers_count"]]

    # Drop irrelevant columns for clustering
    df_cluster.drop(cols_to_drop, axis=1, inplace=True)

    # Label-encode categorical columns
    gender_encoder = LabelEncoder()
    df_cluster["gender"] = gender_encoder.fit_transform(df_cluster["gender"])

    lang_encoder = LabelEncoder()
    df_cluster["pref_language"] = lang_encoder.fit_transform(df_cluster["pref_language"])

    # Find optimal number of clusters (KModes)
    costs = []
    kmax = 15

    for k in range(1, kmax + 1):
        kmodes = KModes(n_clusters=k, init="Cao")
        kmodes.fit(df_cluster)
        costs.append(kmodes.cost_)

    kn = KneeLocator(range(1, kmax + 1), costs, curve="convex", direction="decreasing")
    number_clusters = kn.knee

    # Perform clustering
    kmodes = KModes(n_clusters=number_clusters, init="Cao")
    clusters = kmodes.fit_predict(df_cluster)
    centroids = kmodes.cluster_centroids_

    # Save decoded centroids in brand
    centroids_df = pd.DataFrame(kmodes.cluster_centroids_, columns=df_cluster.columns)
    centroids_df["gender"] = gender_encoder.inverse_transform(centroids_df["gender"])
    centroids_df["pref_language"] = lang_encoder.inverse_transform(centroids_df["pref_language"])
    centroids_df["cluster"] = centroids_df.index
    brand.centroids = centroids_df.to_dict("records")

    # Add cluster attribute to original dataframe
    df_users["cluster"] = clusters

    # Add cluster attribute to the followers
    i, j = 0, 0
    while j < len(df_users):
        follower = brand.followers[i]
        clustered = df_users.iloc[j]
        if follower.id_ == clustered.id_:
            follower.cluster = int(clustered.cluster)
            j += 1
        i += 1

    # Save users with their cluster in DB
    db = Database(db=2)
    db.save_brand(brand)
