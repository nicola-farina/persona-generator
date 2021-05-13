from typing import List
import json

import redis

from personas.common.user import User, Brand
from personas.common.post import Post


class Database(object):

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0) -> None:
        self.__connection = redis.Redis(host, port, db, decode_responses=True)

    @staticmethod
    def __get_brand_key(brand: Brand = None, brand_id: str = None) -> str:
        if brand is None and brand_id is None:
            raise ValueError("Expected either brand or brand_id args")
        elif brand is None:
            id_ = brand_id
        else:
            id_ = brand.id_

        return f"brand:{id_}"

    @staticmethod
    def __get_user_key(user: User = None, user_id: str = None) -> str:
        if user is None and user_id is None:
            raise ValueError("Expected either user or user_id args")
        elif user is None:
            id_ = user_id
        else:
            id_ = user.id_

        return f"user:{id_}"

    @staticmethod
    def __get_post_key(post: Post = None, post_id: str = None) -> str:
        if post is None and post_id is None:
            raise ValueError("Expected either post or post_id args")
        elif post is None:
            id_ = post_id
        else:
            id_ = post.id_

        return f"post:{id_}"

    def save_brand(self, brand: Brand) -> None:
        key = self.__get_brand_key(brand=brand)

        # Save followers separately (Redis can't nest data types)
        if brand.followers:
            self.save_brand_followers(brand)
        if brand.centroids:
            self.save_brand_centroids(brand)

        # Save the hash of the other attributes
        attributes = brand.__dict__
        attributes.pop("followers", None)
        attributes.pop("centroids", None)
        self.__connection.hmset(key, attributes)

    def get_brand(self, brand_id: str) -> Brand:
        key = self.__get_brand_key(brand_id=brand_id)

        # Get the attributes and create brand
        attributes = self.__connection.hgetall(key)
        brand = Brand(attributes["id_"])

        # Get the followers list and populate it
        brand.followers = self.get_brand_followers(brand)
        brand.centroids = self.get_brand_centroids(brand)

        return brand

    def save_brand_followers(self, brand: Brand) -> None:
        brand_key = self.__get_brand_key(brand)
        followers_key = f"{brand_key}:followers"

        # Save users separately
        for follower in brand.followers:
            self.save_user(follower)

        # Save the ids only in a list (deleting the previous one)
        follower_ids = [follower.id_ for follower in brand.followers]
        self.__connection.delete(followers_key)
        self.__connection.rpush(followers_key, *follower_ids)

    def get_brand_followers(self, brand: Brand) -> List[User]:
        brand_key = self.__get_brand_key(brand)
        followers_key = f"{brand_key}:followers"

        follower_ids = self.__connection.lrange(followers_key, 0, -1)
        followers = []
        for follower_id in follower_ids:
            followers.append(self.get_user(user_id=follower_id))

        return followers

    def save_brand_centroids(self, brand: Brand) -> None:
        brand_key = self.__get_brand_key(brand)
        centroids_key = f"{brand_key}:centroids"

        self.__connection.delete(centroids_key)
        for centroid in brand.centroids:
            centroid_json = json.dumps(centroid)
            self.__connection.rpush(centroids_key, centroid_json)

    def get_brand_centroids(self, brand: Brand) -> List[dict]:
        brand_key = self.__get_brand_key(brand)
        centroids_key = f"{brand_key}:centroids"

        centroids_json = self.__connection.lrange(centroids_key, 0, -1)
        centroids = [json.loads(centroid) for centroid in centroids_json]

        return centroids

    def save_user(self, user: User) -> None:
        key = self.__get_user_key(user=user)

        # Save posts separately (Redis can't handle nested data types)
        if user.posts:
            self.save_user_posts(user)

        # Save the hash of the other attributes (only not "None" ones)
        attributes = {k: v for k, v in user.__dict__.items() if v is not None}
        attributes.pop("posts", None)
        self.__connection.hmset(key, attributes)

    def get_user(self, user_id: str) -> User:
        key = self.__get_user_key(user_id=user_id)

        # Get the attributes and create user
        attributes = self.__connection.hgetall(key)
        user = User.from_dict(attributes)

        # Get the posts list and populate it
        user.posts = self.get_user_posts(user)

        return user

    def save_user_posts(self, user: User) -> None:
        user_key = self.__get_user_key(user)
        posts_key = f"{user_key}:posts"

        # Save posts separately
        for post in user.posts:
            self.save_post(post)

        # Save the ids only in a list (deleting the previous one)
        post_ids = [post.id_ for post in user.posts]
        self.__connection.delete(posts_key)
        self.__connection.rpush(posts_key, *post_ids)

    def get_user_posts(self, user: User) -> List[Post]:
        user_key = self.__get_user_key(user)
        posts_key = f"{user_key}:posts"

        post_ids = self.__connection.lrange(posts_key, 0, -1)
        posts = []
        for post_id in post_ids:
            posts.append(self.get_post(post_id=post_id))

        return posts

    def save_post(self, post: Post) -> None:
        key = self.__get_post_key(post=post)

        # Save lists separately (Redis can't nest data types)
        list_fields = ["media", "hashtags", "urls"]
        set_fields = ["entities", "topics"]
        self.__save_post_lists(post, list_fields, set_fields)

        # Save the hash of the other attributes (not "None" attributes)
        attributes = {k: v for k, v in post.__dict__.items() if v is not None}
        for field in list_fields + set_fields:
            attributes.pop(field, None)

        self.__connection.hmset(key, attributes)

    def get_post(self, post_id: str) -> Post:
        key = self.__get_post_key(post_id=post_id)

        # Get attributes
        attributes = self.__connection.hgetall(key)
        post = Post.from_dict(attributes)

        # Populate required fields
        list_fields = ["media", "hashtags", "urls"]
        set_fields = ["entities", "topics"]
        fields_dict = self.__get_post_lists(post, list_fields, set_fields)
        for field, value in fields_dict.items():
            setattr(post, field, value)

        return post

    def get_user_persona(self, brand_id: str, user_id: str) -> dict:
        brand_key = self.__get_brand_key(brand_id=brand_id)
        user_key = self.__get_user_key(user_id=user_id)

        cluster_id = int(self.__connection.hget(user_key, "cluster"))
        personas = self.get_brand_centroids(Brand(brand_id))

        return personas[cluster_id]


    def __save_post_lists(self, post: Post, list_fields: list, set_fields: list) -> None:
        key = self.__get_post_key(post=post)

        for field in list_fields + set_fields:
            field_key = f"{key}:{field}"
            field_value = getattr(post, field)

            self.__connection.delete(field_key)
            if field_value:
                if field in list_fields:
                    self.__connection.rpush(field_key, *field_value)
                else:
                    self.__connection.sadd(field_key, *field_value)

    def __get_post_lists(self, post: Post, list_fields: list, set_fields: list) -> dict:
        key = self.__get_post_key(post=post)
        rtr = {}

        for field in list_fields + set_fields:
            field_key = f"{key}:{field}"

            if field in list_fields:
                rtr[field] = self.__connection.lrange(field_key, 0, -1)
            else:
                rtr[field] = self.__connection.smembers(field_key)

        return rtr
