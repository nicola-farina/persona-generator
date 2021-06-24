import os
from datetime import timedelta


class Config(object):
    SECRET_KEY = os.getenv("SECRET_KEY")
    PROPAGATE_EXCEPTIONS = True
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "6379")
    DB_NAME = os.getenv("DB_NAME", "0")
