from neo4j import GraphDatabase

class Neo4jDriver:
    def __init__(self):
        self.uri = "bolt://127.0.0.1:7687"
        self.user = "neo4j"
        self.password = "Neo4j@0407"
        self.database = "vectorKG"
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password), database=self.database)

    def get_session(self):
        return self.driver.session()

driver = Neo4jDriver()