import paho.mqtt.client as mqtt


class QueueClient(mqtt.Client):
    def __init__(self, host: str, port: int):
        super(QueueClient, self).__init__()
        self.connect(host, port)
