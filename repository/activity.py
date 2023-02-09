from typing import NamedTuple, Optional, Tuple
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
                        "RETURN id(activity) as id, activity.name as name, "
                        "activity.description as description, "
                        "activity.reference as reference", vars(entity))
        return result.single()

    @staticmethod
    def bulk_create_query(tx: ManagedTransaction, entitis: list[Activity]):
        for entity in entitis:
            tx.run(
                "MERGE (:Activity{name:$name, description:$description,reference:$reference})",
                vars(entity)
            )

    @staticmethod
    def _update_query(tx: ManagedTransaction, entity: Activity) -> Optional[Activity]:
        result = tx.run("MATCH (activity:Activity) "
                        "SET activity.name = $name "
                        "SET activity.description = $description "
                        "SET activity.reference = $reference "
                        "WHERE activity.id = $id "
                        "RETURN id(activity) as id, activity.name as name, "
                        "activity.description as description, "
                        "activity.reference as reference", vars(entity))
        return result.single()

    @staticmethod
    def _get_query(tx: ManagedTransaction, id: str) -> Optional[Activity]:
        result = tx.run("MATCH (activity:Activity) "
                        "WHERER id(activity) = $id "
                        "RETURN id(activity) as id, activity.name as name, "
                        "activity.description as description, "
                        "activity.reference as reference", id=id)
        return result.single()

    @staticmethod
    def _get_all_query(tx: ManagedTransaction, params):
        result = tx.run("MATCH (activity:Activity) "
                        "RETURN id(activity) as id, activity.name as name, "
                        "activity.description as description, "
                        "activity.reference as reference", params)
        return result.data()

    @staticmethod
    def _main_objectives_all_by_id_query(tx: ManagedTransaction, params):
        result = tx.run("MATCH(a:Activity)-[matches:MATCHES]->(o:Objective)"
                        "RETURN a as activity, o as objective, "
                        "matches.contribution_type as activityContributionType, "
                        "matches.description as contributionDescription, "
                        "[(o)-[:DNSH]-(do:Objective)-[:DNSH]-(c:Criteria)|{objective: do.name, criteria:[c.description]}] as dnsh, "
                        "[(o)-[:SC_CRITERIA]->(c:Criteria)|c.description] as substantialContributionCriteria",
                        params)
        return result.data()

    @staticmethod
    def _main_objectives_by_id_query(tx: ManagedTransaction, id: str):
        result = tx.run("MATCH(a:Activity WHERE id(a)=$id)-[matches:MATCHES]->(o:Objective WHERE o.key=$mitigation OR o.key=$adoptation) "
                        "RETURN a as activity, o as objective, "
                        "matches.contribution_type as activityContributionType, "
                        "matches.description as contributionDescription",
                        id=int(id), mitigation="mitigation", adoptation="adoptation")
        return result.data()

    @staticmethod
    def _main_objectives_by_name_query(tx: ManagedTransaction, name: str):
        result = tx.run("MATCH(a:Activity WHERE a.name=$name)-[matches:MATCHES]->(o:Objective WHERE o.key=$mitigation OR o.key=$adoptation) "
                        "RETURN a as activity, o as objective, "
                        "matches.contribution_type as activityContributionType, "
                        "matches.description as contributionDescription",
                        name=name, mitigation="mitigation", adoptation="adoptation")
        return result.data()

    @staticmethod
    def create_matches_with_objective_query(tx: ManagedTransaction, entity: Activity, objective: Objective):
        result = tx.run("MATCH (activity:Activity) "
                        "WHERE id(activity) = $activity_id "
                        "MATCH (objective:Objective) "
                        "WHERE id(objective) = $objective_id "
                        "CREATE (activity)-[rel:MATCHES]->(objective) "
                        "RETURN activity, rel, objective",
                        activity_id=entity.id, objective_id=objective.id)
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
                        "CREATE (activity)-[rel:MATCHES]->(objective) "
                        "DELETE rel",
                        activity_id=entity.id, objective_id=objective.id)
        return result

    @staticmethod
    def create_contribution_match_with_objective_query(tx: ManagedTransaction, activity: str, objective: str, match: dict):
        if None not in match.values():
            tx.run("MATCH (activity:Activity) WHERE activity.name = $activity_name "
                "MATCH (objective:Objective) WHERE objective.key = $objective_key "
                "MERGE (activity)-[:MATCHES{contribution_type:$contribution_type,description:$description}]->(objective)",
                activity_name=activity, objective_key=objective, **match)
        elif match["contribution_type"]:
            tx.run("MATCH (activity:Activity) WHERE activity.name = $activity_name "
                "MATCH (objective:Objective) WHERE objective.key = $objective_key "
                "MERGE (activity)-[:MATCHES{contribution_type:$contribution_type}]->(objective)",
                activity_name=activity, objective_key=objective, **match)
        elif match["description"]:
            tx.run("MATCH (activity:Activity) WHERE activity.name = $activity_name "
                "MATCH (objective:Objective) WHERE objective.key = $objective_key "
                "MERGE (activity)-[:MATCHES{description:$description}]->(objective)",
                activity_name=activity, objective_key=objective, **match)

    def create(self, entity: Activity):
        return self.db.execute_query(self._create_query, entity)

    def bulk_create(self, entities: list[Activity]):
        return self.db.execute_query(self._bulk_create_query, entities)

    def create_contribution_match_with_objective(self, activity: str, objective: str, match) -> Activity:
        return self.db.execute_query(self._create_contribution_match_with_objective_query, activity, objective, match)

    def update(self, entity: Activity) -> Tuple[bool, Optional[Activity]]:
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
        return self.db.execute_query(self._get_all_query, {})

    def get_main_objectives_all(self):
        return self.db.execute_query(self._main_objectives_all_by_id_query, {})

    def get_main_objectives_by_id(self, id: str):
        return self.db.execute_query(self._main_objectives_by_id_query, id)

    def get_main_objectives_by_name(self, name: str):
        return self.db.execute_query(self._main_objectives_by_name_query, name)

    def delete_by_id(self, id: str) -> bool:
        return self.db.execute_query(self._delete_query, id)

    def delete_relationship_with_objective(self, entity: Activity, objective: Objective) -> bool:
        return self.db.execute_query(self._delete_relationship_with_objective_query, entity, objective)
