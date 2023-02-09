from dao.database_factory import db
from repository.activity import ActivityRepository


def get_activity_resolver(obj, info, id: str):
    try:
        activity = ActivityRepository(db).get_by_id(id)
        payload = {
            "success": True,
            "activity": activity
        }
    except Exception as error:
        payload = {
            "success": False,
            "errors": [str(error)]
        }
    return payload


def get_activity_main_objectives_by_id_resolver(obj, info, id: str):
    try:
        activity = ActivityRepository(db).get_main_objectives_by_id(id)
        print(activity)
        payload = {
            "success": True,
            "activityMainObjectives": activity
        }
    except Exception as error:
        payload = {
            "success": False,
            "errors": [str(error)]
        }
    return payload


def get_activity_main_objectives_all_resolver(obj, info):
    try:
        activity = ActivityRepository(db).get_main_objectives_all()
        print(activity)
        payload = {
            "success": True,
            "activityMainObjectives": activity
        }
    except Exception as error:
        payload = {
            "success": False,
            "errors": [str(error)]
        }
    return payload


def get_activity_main_objectives_by_name_resolver(obj, info, name: str):
    try:
        print(name)
        activity = ActivityRepository(db).get_main_objectives_by_name(name)
        print(activity)
        payload = {
            "success": True,
            "activityMainObjectives": activity
        }
    except Exception as error:
        payload = {
            "success": False,
            "errors": [str(error)]
        }
    return payload


def list_activities_resolver(obj, info):
    try:
        activities = ActivityRepository(db).get_all()
        print(activities)
        payload = {
            "success": True,
            "activities": activities
        }
    except Exception as error:
        payload = {
            "success": False,
            "errors": [str(error)]
        }
    return payload
