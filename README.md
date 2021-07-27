# persona-generator
Python package to automatically generate marketing personas from social media data of a fanbase. The code is messy and the project is incomplete: the main focus is the design of the system, this is only a very rough prototype.

## How to use
- After cloning the repository, install the required packages found in the requirements file.
- Configure all the needed variables in the .env file.
- Run a Redis DB with RedisJSON module installed: 

  `docker run -d -p 6379:6379 --name redis-rejson redislabs/rejson:latest`
- Run the web service (`src/web/main.py`), the Twitter collector (`src/personas/collection/twitter.py`), the activity enricher (`src/personas/enrichment/activities/main.py`) and the data source enricher (`src/personas/enrichment/sources/main.py`).
- Use API to create an account, create a brand, and add users to a brand. When a user is added, it is automatically sent to collection and enrichment. The API docs are found here: [API Documentation](https://app.swaggerhub.com/apis-docs/nicola-farina/personagenerator/1.0.0#/)

- When users are enriched, run the clustering and generation module to generate the personas for the brand (`src/personas/clustering/main.py`). You have to pass the brand id as a command line argument.
