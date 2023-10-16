from bson import json_util
from bson.objectid import ObjectId
from flask import jsonify, request, abort, Blueprint

from db import db
from models import Physician
from utils import validate_object_id

physicians_blueprint = Blueprint('physicians_blueprint', __name__)


@physicians_blueprint.route('/', methods=['POST'])
def add_physician():
    data = request.get_json()
    try:
        physician = Physician(name=data['name'], age=data['age'], specialty=data[
            'specialty'], department_id=data.get('department_id'))
        physician_data = physician.__dict__

        if "certifications" in data:
            physician_data["certifications"] = data["certifications"]

        db.physicians.insert_one(physician_data)
        return jsonify({"message": "Physician added successfully"}), 201

    except KeyError:
        abort(400, description="Invalid data")


@physicians_blueprint.route('/', methods=['GET'])
def get_physicians():
    physicians = db.physicians.find()
    return json_util.dumps(physicians), 200


@physicians_blueprint.route('/<physician_id>', methods=['DELETE'])
def remove_physician(physician_id):
    validate_object_id(physician_id)
    result = db.physicians.delete_one({"_id": ObjectId(physician_id)})
    if result.deleted_count:
        return jsonify({"message": "Physician removed successfully"}), 200
    else:
        abort(404, description="Physician not found")


@physicians_blueprint.route('/<physician_id>/certifications', methods=['POST'])
def add_certification_to_physician(physician_id):
    validate_object_id(physician_id)
    data = request.get_json()

    if not data or 'name' not in data:
        abort(400, description="Invalid data")

    result = db.physicians.update_one(
        {"_id": ObjectId(physician_id)},
        {"$push": {"certifications": data["name"]}}
    )

    if result.modified_count:
        return jsonify({"message": "Certification added to physician successfully"}), 201
    else:
        abort(500, description="Failed to add certification to physician")


@physicians_blueprint.route('/average-age', methods=['GET'])
def get_average_age():
    pipeline = [
        {"$group": {"_id": None, "averageAge": {"$avg": "$age"}}}
    ]
    result = list(db.physicians.aggregate(pipeline))
    if result and "averageAge" in result[0]:
        avg_age = round(result[0]["averageAge"], 2)
        return jsonify({"averageAge": avg_age}), 200
    else:
        return jsonify({"error": "Operation failed"}), 500


@physicians_blueprint.route('/specialty-count', methods=['GET'])
def get_physician_counts_by_specialty():
    pipeline = [
        {"$group": {"_id": "$specialty", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}  # descending
    ]
    result = list(db.physicians.aggregate(pipeline))
    if result:
        return jsonify(result), 200
    else:
        return jsonify({"error": "Operation failed"}), 500


@physicians_blueprint.route('/certifications-count', methods=['GET'])
def get_certification_counts():
    pipeline = [
        {"$unwind": "$certifications"},
        {"$group": {"_id": "$certifications.name", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}  # descending
    ]
    result = list(db.physicians.aggregate(pipeline))
    if result:
        return jsonify(result), 200
    else:
        return jsonify({"error": "Operation failed"}), 500
