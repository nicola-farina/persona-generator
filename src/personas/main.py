import argparse

import paho.mqtt.client as mqtt

if __name__ == "__main__":
    # Setup argparser
    parser = argparse.ArgumentParser()
    parser.add_argument("--host_mqtt", required=True)
    parser.add_argument("--port_mqtt", required=True)
    args = parser.parse_args()
    host = args.host_mqtt
    port = int(args.port_mqtt)

    # Connect to MQTT client
    client = mqtt.Client()
    client.connect(host=host, port=port)

    # Send payload to Twitter collector
    twitter_user_id = "307410719"
    client.publish("collector/twitter", "307410719")