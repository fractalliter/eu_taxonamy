from typing import NamedTuple, Optional
from dao.database_factory import DatabaseFactory
from neo4j import ManagedTransaction, Record
from entity.Activity import Activity
from entity.Objective import Objective


class ActivityRepository(NamedTuple):
    db: DatabaseFactory

    @staticmethod
    def _create_query(tx: ManagedTransaction, entity: Activity):
        result = tx.run("CREATE (activity:Activity) "
                        "SET activity.name = $name "
                        "SET activity.description = $description "
                        "SET activity.reference = $reference "
                        "RETURN activity", **vars(entity))
        return result.single()

    @staticmethod
    def _update_query(tx: ManagedTransaction, entity: Activity) -> Optional[Activity]:
        result = tx.run("MATCH (activity:Activity) "
                        "SET activity.name = $name "
                        "SET activity.description = $description "
                        "SET activity.reference = $reference "
                        "WHERE activity.id = $id "
                        "RETURN activity", **vars(entity))
        return result.single()

    @staticmethod
    def _get_query(tx: ManagedTransaction, id: str) -> Optional[Activity]:
        result = tx.run("MATCH (activity:Activity) "
                        "WHERER id(activity) = $id "
                        "RETURN activity", id=id)
        return result.single()

    @staticmethod
    def _get_all_query(tx: ManagedTransaction):
        result = tx.run("MATCH (activity:Activity) "
                        "RETURN activity")
        return result.data()

    @staticmethod
    def _create_match_with_objective_query(tx: ManagedTransaction, entity: Activity, objective: Objective):
        result = tx.run("MATCH (activity:Activity) "
                        "WHERE id(activity) = $activity_id "
                        "MATCH (objective:Objective) "
                        "WHERE id(objective) = $objective_id "
                        "CREATE (activity)-[rel:MATCH]->(objective) "
                        "RETURN activity, rel, objective",
                        activity_id=entity.id, objective_id=objective.id)
        return result

    @staticmethod
    def _create_contribution_match_with_objective_query(tx: ManagedTransaction, entity: Activity, objective: Objective, match: dict):
        result = tx.run("MATCH (activity:Activity) "
                        "WHERE id(activity) = $activity_id "
                        "MATCH (objective:Objective) "
                        "WHERE id(objective) = $objective_id "
                        "CREATE (activity)-[rel:MATCH{contribution_type:$contribution_type,description:$description}]->(objective) "
                        "RETURN activity, rel, objective",
                        activity_id=entity.id, objective_id=objective.id, **match)
        return result

    @staticmethod
    def _delete_query(tx: ManagedTransaction, id: str) -> bool:
        result = tx.run("MATCH (activity:Activity) "
                        "WHERE id(activity) = $activity_id "
                        "DELETE activity",
                        activity_id=id)
        return result

    @staticmethod
    def _delete_relationship_with_objective_query(tx: ManagedTransaction, entity: Activity, objective: Objective):
        result = tx.run("MATCH (activity:Activity) "
                        "WHERE id(activity) = $activity_id "
                        "MATCH (objective:Objective) "
                        "WHERE id(objective) = $objective_id "
                        "CREATE (activity)-[rel:MATCH]->(objective) "
                        "DELETE rel",
                        activity_id=entity.id, objective_id=objective.id)
        return result

    def create(self, entity: Activity):
        return self.db.execute_query(self._create_query, entity)

    def create_match_with_objective(self, entity: Activity, objective: Objective) -> Activity:
        return self.db.execute_query(self._create_match_with_objective_query, entity, objective)

    def create_contribution_match_with_objective(self, entity: Activity, objective: Objective) -> Activity:
        return self.db.execute_query(self._create_contribution_match_with_objective_query, entity, objective)

    def update(self, entity: Activity) -> tuple(bool, Optional[Activity]):
        activity: Record = self.db.execute_query(self._update_query, entity)
        if activity:
            return (True, activity.data()["activity"])
        else:
            return (False, None)

    def get_by_id(self, id: str) -> Optional[Activity]:
        activity: Record = self.db.execute_query(self._get_query, id)
        if activity:
            return activity.data()
        else:
            return None

    def get_all(self) -> list[Activity]:
        return self.db.execute_query(self._get_all_query)

    def delete_by_id(self, id: str) -> bool:
        return self.db.execute_query(self._delete_query, id)

    def delete_relationship_with_objective(self, entity: Activity, objective: Objective) -> bool:
        return self.db.execute_query(self._delete_relationship_with_objective_query, entity, objective)
