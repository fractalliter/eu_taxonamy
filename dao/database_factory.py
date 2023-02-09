from neo4j import GraphDatabase


class DatabaseFactory:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def execute_query(self, query, params):
        with self.driver.session() as session:
            return session.execute_write(query, params)

    def close(self):
        self.driver.close()


db = DatabaseFactory("bolt://localhost:7687", "neo4j", "9VXuvxKAWuV9RTW")
