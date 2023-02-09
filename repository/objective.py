from typing import NamedTuple, Optional, Tuple
from dao.database_factory import DatabaseFactory
from neo4j import ManagedTransaction, Record
from entity.Criteria import Criteria
from entity.Objective import Objective


class ObjectiveRepository(NamedTuple):
    db: DatabaseFactory

    @staticmethod
    def _create_query(tx: ManagedTransaction, entity: Objective):
        result = tx.run("CREATE (objective:Objective) "
                        "SET objective.name = $name "
                        "SET objective.description = $description "
                        "SET objective.reference = $reference "
                        "RETURN objective", **vars(entity))
        return result.single()

    @staticmethod
    def bulk_create_query(tx: ManagedTransaction, entitis: list[Objective]):
        for entity in entitis:
            tx.run(
                "MERGE (:Objective{name:$name,long_name:$long_name, key:$key})", vars(entity))

    @staticmethod
    def _update_query(tx: ManagedTransaction, entity: Objective) -> Optional[Objective]:
        result = tx.run("MATCH (objective:Objective) "
                        "SET objective.name = $name "
                        "SET objective.description = $description "
                        "SET objective.reference = $reference "
                        "WHERE objective.id = $id "
                        "RETURN objective", **vars(entity))
        return result.single()

    @staticmethod
    def _get_query(tx: ManagedTransaction, id: str) -> Optional[Objective]:
        result = tx.run("MATCH (objective:Objective) "
                        "WHERER id(objective) = $id "
                        "RETURN objective", id=id)
        return result.single()

    @staticmethod
    def _get_all_query(tx: ManagedTransaction):
        result = tx.run("MATCH (objective:Objective) "
                        "RETURN objective")
        return result.data()

    @staticmethod
    def create_dnsh_objective_query(tx: ManagedTransaction, objective: str, dnsh_objective: str):
        tx.run("MATCH (objective:Objective) "
               "WHERE objective.key = $objective_key "
               "MATCH (dnsh_objective:Objective) "
               "WHERE dnsh_objective.key = $dnsh_objective_key "
               "MERGE (objective)-[rel:DNSH]->(dnsh_objective)",
               objective_key=objective, dnsh_objective_key=dnsh_objective)

    @staticmethod
    def create_sc_criteria_query(tx: ManagedTransaction, objective: str, criteria: str):
        tx.run("MATCH (objective:Objective) "
               "WHERE objective.key = $objective_key "
               "MATCH (criteria:Criteria) "
               "WHERE criteria.description = $criteria_description "
               "MERGE (objective)-[rel:SC_CRITERIA]->(criteria)",
               objective_key=objective, criteria_description=criteria)

    @staticmethod
    def create_dnsh_match_with_criteria_query(tx: ManagedTransaction, objective: str, criteria: Criteria):
        tx.run("MATCH (objective:Objective) "
               "WHERE objective.key = $objective_key "
               "MATCH (criteria:Criteria) "
               "WHERE criteria.description = $criteria_description "
               "MERGE (objective)-[rel:DNSH_MATCHES]->(criteria)",
               objective_key=objective, criteria_description=criteria)

    @staticmethod
    def _delete_query(tx: ManagedTransaction, id: str) -> bool:
        result = tx.run("MATCH (objective:Objective) "
                        "WHERE id(objective) = $objective_id "
                        "DELETE objective",
                        objective_id=id)
        return result

    @staticmethod
    def _delete_relationship_with_criteria_query(tx: ManagedTransaction, objective: str, criteria: Criteria):
        result = tx.run("MATCH (objective:Objective) "
                        "WHERE objective.name = $objective_name "
                        "MATCH (criteria:Criteria) "
                        "WHERE id(criteria) = $criteria_id "
                        "CREATE (objective)-[rel:MATCH]->(objective) "
                        "DELETE rel",
                        objective_name=objective, criteria_id=criteria.id)
        return result

    def create(self, entity: Objective):
        return self.db.execute_query(self._create_query, entity)

    def bulk_create(self, entities: list[Objective]):
        return self.db.execute_query(self.bulk_create_query, entities)

    def update(self, entity: Objective) -> Tuple[bool, Optional[Objective]]:
        objective: Record = self.db.execute_query(self._update_query, entity)
        if objective:
            return (True, objective.data()["objective"])
        else:
            return (False, None)

    def get_by_id(self, id: str) -> Optional[Objective]:
        objective: Record = self.db.execute_query(self._get_query, id)
        if objective:
            return objective.data()
        else:
            return None

    def get_all(self) -> list[Objective]:
        return self.db.execute_query(self._get_all_query)

    def delete_by_id(self, id: str) -> bool:
        return self.db.execute_query(self._delete_query, id)

    def delete_relationship_with_objective(self, entity: Objective, objective: Objective) -> bool:
        return self.db.execute_query(self._delete_relationship_with_criteria_query, entity, objective)
