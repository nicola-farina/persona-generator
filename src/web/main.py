from web.api.app import create_app
from web.config import Config

if __name__ == "__main__":
    app = create_app(Config)
    app.run()