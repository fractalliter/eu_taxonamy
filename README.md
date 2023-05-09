# EU Taxonomy Navigator
Python Flask project with graphql and neo4j database, a graph representation of [EU Taxonomy Navigator](https://ec.europa.eu/sustainable-finance-taxonomy/home)

## How to run
You can run this application with [Python](https://www.python.org/downloads/) and deploy it as a whole software via [Docker](https://docs.docker.com/).

Python:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app run
```

## Deploy

You need to have [Docker](https://docs.docker.com/get-docker/) installed on your machine.
```bash
docker compose up -d
```

## Flow
1. Send a request to `/populate` endpoint to integrate data for EU Taxonamy objectives.
2. Go to `/graphql` url on your browser and execute queries.

## TODO
- [ ] Add unit and integration tests
- [ ] Introduce more environment variables
- [ ] Add documents
- [ ] Add CI
