from typing import NamedTuple, Optional, Tuple
from dao.database_factory import DatabaseFactory
from neo4j import ManagedTransaction, Record
from entity.Sector import Sector
from entity.Activity import Activity


class SectorRepository(NamedTuple):
    db: DatabaseFactory

    @staticmethod
    def create_query(tx: ManagedTransaction, entity: Sector):
        result = tx.run("CREATE (sector:Sector) "
                        "SET sector.name = $name "
                        "SET sector.reference = $reference "
                        "RETURN sector", vars(entity))
        return result.single()

    @staticmethod
    def bulk_create_query(tx: ManagedTransaction, entitis: list[Sector]):
        for entity in entitis:
            tx.run("MERGE (:Sector{name:$name})", vars(entity))

    @staticmethod
    def update_query(tx: ManagedTransaction, entity: Sector) -> Optional[Sector]:
        result = tx.run("MATCH (sector:Sector) "
                        "SET sector.name = $name "
                        "SET sector.description = $description "
                        "SET sector.reference = $reference "
                        "WHERE sector.id = $id "
                        "RETURN sector", **vars(entity))
        return result.single()

    @staticmethod
    def get_query(tx: ManagedTransaction, id: str) -> Optional[Sector]:
        result = tx.run("MATCH (sector:Sector) "
                        "WHERER id(sector) = $id "
                        "RETURN sector", id=id)
        return result.single()

    @staticmethod
    def get_all_query(tx: ManagedTransaction):
        result = tx.run("MATCH (sector:Sector) "
                        "RETURN sector")
        return result.data()

    @staticmethod
    def create_match_with_activity_query(tx: ManagedTransaction, activity: dict):
        tx.run("MATCH (sector:Sector) "
               "WHERE sector.name = $sector_name "
               "MATCH (activity:Activity) "
               "WHERE activity.name = $activity_name "
               "MERGE (sector)-[rel:MATCHES]->(activity)",
               sector_name=activity["sector"], activity_name=activity["name"])

    @staticmethod
    def delete_query(tx: ManagedTransaction, id: str) -> bool:
        result = tx.run("MATCH (sector:Sector) "
                        "WHERE id(sector) = $sector_id "
                        "DELETE sector",
                        sector_id=id)
        return result

    @staticmethod
    def delete_relationship_with_activity_query(tx: ManagedTransaction, entity: Sector, activity: Activity):
        result = tx.run("MATCH (sector:Sector) "
                        "WHERE id(sector) = $sector_id "
                        "MATCH (activity:Activity) "
                        "WHERE id(activity) = $activity_id "
                        "CREATE (sector)-[rel:MATCH]->(activity) "
                        "DELETE rel",
                        sector_id=entity.id, activity_id=activity.id)
        return result

    def create(self, entity: Sector):
        return self.db.execute_query(self.create_query, entity)

    def bulk_create(self, entities: list[Sector]):
        return self.db.execute_query(self.bulk_create_query, entities)

    def create_match_with_activity(self, entity: Sector, activity: Activity) -> Sector:
        return self.db.execute_query(self.create_match_with_activity_query, entity, activity)

    def update(self, entity: Sector) -> Tuple[bool, Optional[Sector]]:
        sector: Record = self.db.execute_query(self.update_query, entity)
        if sector:
            return (True, sector.data()["sector"])
        else:
            return (False, None)

    def get_by_id(self, id: str) -> Optional[Sector]:
        sector: Record = self.db.execute_query(self.get_query, id)
        if sector:
            return sector.data()
        else:
            return None

    def get_all(self) -> list[Sector]:
        return self.db.execute_query(self.get_all_query)

    def delete_by_id(self, id: str) -> bool:
        return self.db.execute_query(self.delete_query, id)

    def delete_relationship_with_activity(self, entity: Sector, activity: Activity) -> bool:
        return self.db.execute_query(self.delete_relationship_with_activity_query, entity, activity)
