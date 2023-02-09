from concurrent.futures import ThreadPoolExecutor
from flask import request, jsonify
from ariadne.constants import PLAYGROUND_HTML
from ariadne import load_schema_from_path, make_executable_schema, \
    graphql_sync, snake_case_fallback_resolvers, ObjectType
from flask import Flask
import os
from resolver.activity import get_activity_resolver, list_activities_resolver, \
    get_activity_main_objectives_by_id_resolver, get_activity_main_objectives_by_name_resolver, \
        get_activity_main_objectives_all_resolver
from service.integration import Integration, populate_database
from dao.database_factory import db
import requests

app = Flask(__name__)

logger = app.logger

app.config["DB_URL"] = os.getenv("DB_URL")
app.config["DB_USERNAME"] = os.getenv("DB_USERNAME")
app.config["DB_PASSWORD"] = os.getenv("DB_PASSWORD")

type_defs = load_schema_from_path("schema/eu_taxonamy.graphql")


@app.route("/populate")
def populate_db():
    integration = Integration(requests)
    populate_database(integration, db)
    return {"message": "started"}


query = ObjectType("Query")
query.set_field("getActivity", get_activity_resolver)
query.set_field("listActivities", list_activities_resolver)
query.set_field("getActivityMainObjectivesByID",
                get_activity_main_objectives_by_id_resolver)
query.set_field("getActivityMainObjectivesByName",
                get_activity_main_objectives_by_name_resolver)
query.set_field("getActivityAllMainObjectives",get_activity_main_objectives_all_resolver)

schema = make_executable_schema(
    type_defs, query, snake_case_fallback_resolvers
)


@app.route("/graphql", methods=["GET"])
def graphql_playground():
    return PLAYGROUND_HTML, 200


@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug
    )
    status_code = 200 if success else 400
    return jsonify(result), status_code
