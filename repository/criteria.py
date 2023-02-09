from typing import NamedTuple, Optional, Tuple
from dao.database_factory import DatabaseFactory
from neo4j import ManagedTransaction, Record
from entity.Criteria import Criteria
from entity.Objective import Objective


class CriteriaRepository(NamedTuple):
    db: DatabaseFactory

    @staticmethod
    def create_query(tx: ManagedTransaction, entity: Criteria):
        result = tx.run("CREATE (criteria:Criteria) "
                        "SET criteria.description = $description "
                        "RETURN criteria", **vars(entity))
        return result.single()

    @staticmethod
    def bulk_create_query(tx: ManagedTransaction, descriptions: list[str]):
        for description in descriptions:
            tx.run("MERGE (:Criteria{description:$description})",
                   description=description)

    @staticmethod
    def update_query(tx: ManagedTransaction, entity: Criteria) -> Optional[Criteria]:
        result = tx.run("MATCH (criteria:Criteria) "
                        "SET criteria.description = $description "
                        "WHERE criteria.id = $id "
                        "RETURN criteria", **vars(entity))
        return result.single()

    @staticmethod
    def _get_query(tx: ManagedTransaction, id: str) -> Optional[Criteria]:
        result = tx.run("MATCH (criteria:Criteria) "
                        "WHERER id(criteria) = $id "
                        "RETURN criteria", id=id)
        return result.single()

    @staticmethod
    def _get_all_query(tx: ManagedTransaction):
        result = tx.run("MATCH (criteria:Criteria) "
                        "RETURN criteria")
        return result.data()

    @staticmethod
    def _create_match_with_objective_query(tx: ManagedTransaction, entity: Criteria, objective: Objective):
        result = tx.run("MATCH (criteria:Criteria) "
                        "WHERE id(criteria) = $criteria_id "
                        "MATCH (objective:Objective) "
                        "WHERE id(objective) = $objective_id "
                        "CREATE (criteria)-[rel:MATCH]->(objective) "
                        "RETURN criteria, rel, objective",
                        criteria_id=entity.id, objective_id=objective.id)
        return result

    @staticmethod
    def _create_contribution_match_with_objective_query(tx: ManagedTransaction, entity: Criteria, objective: Objective, match: dict):
        result = tx.run("MATCH (criteria:Criteria) "
                        "WHERE id(criteria) = $criteria_id "
                        "MATCH (objective:Objective) "
                        "WHERE id(objective) = $objective_id "
                        "CREATE (criteria)-[rel:MATCH{contribution_type:$contribution_type,description:$description}]->(objective) "
                        "RETURN criteria, rel, objective",
                        criteria_id=entity.id, objective_id=objective.id, **match)
        return result

    @staticmethod
    def _delete_query(tx: ManagedTransaction, id: str) -> bool:
        result = tx.run("MATCH (criteria:Criteria) "
                        "WHERE id(criteria) = $criteria_id "
                        "DELETE criteria",
                        criteria_id=id)
        return result

    @staticmethod
    def _delete_relationship_with_objective_query(tx: ManagedTransaction, entity: Criteria, objective: Objective):
        result = tx.run("MATCH (criteria:Criteria) "
                        "WHERE id(criteria) = $criteria_id "
                        "MATCH (objective:Objective) "
                        "WHERE id(objective) = $objective_id "
                        "CREATE (criteria)-[rel:MATCH]->(objective) "
                        "DELETE rel",
                        criteria_id=entity.id, objective_id=objective.id)
        return result

    def create(self, entity: Criteria):
        return self.db.execute_query(self.create_query, entity)

    def create_match_with_objective(self, entity: Criteria, objective: Objective) -> Criteria:
        return self.db.execute_query(self._create_match_with_objective_query, entity, objective)

    def create_contribution_match_with_objective(self, entity: Criteria, objective: Objective) -> Criteria:
        return self.db.execute_query(self._create_contribution_match_with_objective_query, entity, objective)

    def update(self, entity: Criteria) -> Tuple[bool, Optional[Criteria]]:
        criteria: Record = self.db.execute_query(self.update_query, entity)
        if criteria:
            return (True, criteria.data()["criteria"])
        else:
            return (False, None)

    def get_by_id(self, id: str) -> Optional[Criteria]:
        criteria: Record = self.db.execute_query(self._get_query, id)
        if criteria:
            return criteria.data()
        else:
            return None

    def get_all(self) -> list[Criteria]:
        return self.db.execute_query(self._get_all_query)

    def delete_by_id(self, id: str) -> bool:
        return self.db.execute_query(self._delete_query, id)

    def delete_relationship_with_objective(self, entity: Criteria, objective: Objective) -> bool:
        return self.db.execute_query(self._delete_relationship_with_objective_query, entity, objective)
