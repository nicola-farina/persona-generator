from rejson import Client


class DatabaseConnection(object):
    def __init__(self) -> None:
        self.connection = None

    def init(self, host: str, port: int, db: int) -> None:
        self.connection = Client(host=host, port=port, db=db, decode_responses=True)

    def close(self):
        try:
            self.connection.close()
        except:
            # Already closed
            pass
