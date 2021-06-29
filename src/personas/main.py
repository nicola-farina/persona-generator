import os
import json

from dotenv import load_dotenv
import paho.mqtt.client as mqtt

from src.common.database.connection import DatabaseConnection
from src.common.database.users import UsersDatabase
from src.common.database.sources import SourcesDatabase

load_dotenv()


def on_connect(client: mqtt.Client, userdata, flags, rc) -> None:
    print(f"Connected with result code {str(rc)}")
    db_users = UsersDatabase(conn)
    users = db_users.get_users_of_brand("a39544eca6e14da3bae9c95418df0861")

    db_sources = SourcesDatabase(conn)
    sources = [db_sources.get_sources_of_user(user.user_id)[0] for user in users]
    for source in sources:
        queue.publish(topic="enricher/sources", payload=json.dumps(source.to_dict()), qos=1)


DB_URL = os.getenv("DB_URL")
conn = DatabaseConnection(url=DB_URL)

QUEUE_HOST = os.getenv("QUEUE_HOST")
QUEUE_PORT = os.getenv("QUEUE_PORT")
queue = mqtt.Client()
queue.on_connect = on_connect
queue.connect(QUEUE_HOST, int(QUEUE_PORT))
queue.loop_forever()
