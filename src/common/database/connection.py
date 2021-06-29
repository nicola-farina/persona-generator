from rejson import Client


class DatabaseConnection(object):
    def __init__(self, url: str = None) -> None:
        self.connection = None
        if url is not None:
            self.init(url)

    def init(self, url: str) -> None:
        self.connection = Client.from_url(url=url, decode_responses=True)

    def close(self):
        try:
            self.connection.close()
        except:
            # Already closed
            pass
