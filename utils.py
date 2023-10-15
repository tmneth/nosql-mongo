from bson.errors import InvalidId
from bson.objectid import ObjectId
from flask import abort


def validate_object_id(oid):
    try:
        ObjectId(oid)
    except (InvalidId, TypeError):
        abort(400, description="Invalid ObjectId format.")
