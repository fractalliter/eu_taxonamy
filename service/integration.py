from functools import cache
from typing import NamedTuple
from requests import Request
from repository.activity import ActivityRepository
from repository.objective import ObjectiveRepository
from repository.sector import SectorRepository
from repository.criteria import CriteriaRepository
from entity.Sector import Sector
from entity.Activity import Activity
from entity.Objective import Objective
from itertools import chain
import logging


class Integration(NamedTuple):
    request: Request
    __eu_taxonamy_url = "https://ec.europa.eu/sustainable-finance-taxonomy/assets/taxonomy.json"

    @cache
    def fetch_eu_taxonamy(self) -> dict:
        res = self.request.get(self.__eu_taxonamy_url)
        return res.json()

    @staticmethod
    def persist_to_db(tx, data):
        print("started")
        matches = data["matches"]
        sectors = [Sector(**sector) for sector in data["sectors"]]
        activities = [Activity(**activity) for activity in data["activities"]]
        objectives = [Objective(**objective)
                      for objective in data["objectives"]]

        print("bulk create started")
        # bulk creation of nodes
        SectorRepository.bulk_create_query(tx, sectors)
        ObjectiveRepository.bulk_create_query(tx, objectives)
        ActivityRepository.bulk_create_query(tx, activities)
        print("bulk create finished")

        print("activity matches started")
        # create relationship between Sector and Activity
        for activity in data["activities"]:
            SectorRepository.create_match_with_activity_query(tx, activity)
        print("activity matches created")

        print("matches started")
        # create matches
        for match in matches:
            ActivityRepository.create_contribution_match_with_objective_query(
                tx,
                match["activity"],
                match["objective"],
                {"contribution_type": match.get("activity_contribution_type", None),
                 "description": match.get("contribution_description", None)}
            )
            dnsh_criteria = [c["criteria"] for c in match["dnsh"]]
            sc_criteria = match["substantial_contribution_criteria"]
            criteria = list(chain(*dnsh_criteria))
            criteria += list(sc_criteria)
            CriteriaRepository.bulk_create_query(tx, criteria)
            for dnsh in match["dnsh"]:
                # create objective DNSH
                ObjectiveRepository.create_dnsh_objective_query(
                    tx, match["objective"], dnsh["objective"])
                for criteria in dnsh["criteria"]:
                    ObjectiveRepository.create_dnsh_match_with_criteria_query(
                        tx, dnsh["objective"], criteria)
            for criteria in sc_criteria:
                # create sc objective criteria
                ObjectiveRepository.create_sc_criteria_query(
                    tx, match["objective"], criteria)
        print("matches finished")


def populate_database(integration, db):
    logger = logging.getLogger(populate_database.__name__)
    print("start populating")
    data = integration.fetch_eu_taxonamy()
    with db.driver.session() as session:
        session.execute_write(Integration.persist_to_db, data)
    print("population finished")
