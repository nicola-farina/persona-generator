import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config(object):
    PROPAGATE_EXCEPTIONS = True
    DB_URL = os.getenv("DB_URL")
    QUEUE_HOST = os.getenv("QUEUE_HOST")
    QUEUE_PORT = os.getenv("QUEUE_PORT")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
