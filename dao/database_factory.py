from neo4j import GraphDatabase
from os import getenv


class DatabaseFactory:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def execute_query(self, query, params):
        with self.driver.session() as session:
            return session.execute_write(query, params)

    def close(self):
        self.driver.close()


db = DatabaseFactory(
    f'bolt://{getenv("DB_URL") or "localhost"}:7687',
    getenv("DB_USERNAME") or "neo4j",
    getenv("DB_PASSWORD") or "9VXuvxKAWuV9RTW"
)
