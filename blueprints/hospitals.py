from bson import json_util
from bson.objectid import ObjectId
from flask import jsonify, request, abort, Blueprint

from db import db
from models import Hospital, Department, Facility, Equipment
from utils import validate_object_id

hospitals_blueprint = Blueprint('hospitals_blueprint', __name__)


@hospitals_blueprint.route("/", methods=['POST'])
def add_hospital():
    data = request.get_json()
    try:
        hospital = Hospital(name=data['name'], address=data['address'])
        db.hospitals.insert_one(hospital.__dict__)
        return jsonify({"message": "Hospital added!"}), 201
    except KeyError:
        abort(400, description="Invalid data.")


@hospitals_blueprint.route("/", methods=['GET'])
def get_hospitals():
    hospitals = db.hospitals.find()
    return json_util.dumps(hospitals), 200


@hospitals_blueprint.route('/<hospital_id>', methods=['DELETE'])
def remove_hospital(hospital_id):
    validate_object_id(hospital_id)
    result = db.hospitals.delete_one({"_id": ObjectId(hospital_id)})
    if result.deleted_count:
        return jsonify({"message": "Hospital removed!"}), 200
    else:
        abort(404, description="Hospital not found.")


@hospitals_blueprint.route('/<hospital_id>/departments', methods=['POST'])
def add_department_to_hospital(hospital_id):
    data = request.get_json()
    try:
        department_id = ObjectId()
        department = Department(_id=department_id, name=data['name'])
        db.hospitals.update_one({"_id": ObjectId(hospital_id)}, {"$push": {"departments": department.__dict__}})
        return jsonify({"message": "Department added to hospital!", "department_id": str(department_id)}), 201
    except KeyError:
        abort(400, description="Invalid data.")


@hospitals_blueprint.route('/<hospital_id>/departments', methods=['GET'])
def get_departments_in_hospital(hospital_id):
    hospital = db.hospitals.find_one({"_id": ObjectId(hospital_id)})
    if not hospital:
        abort(404, description="Hospital not found.")
    return json_util.dumps(hospital["departments"]), 200


@hospitals_blueprint.route('/<hospital_id>/departments/<department_id>', methods=['DELETE'])
def remove_department_from_hospital(hospital_id, department_id):
    result = db.hospitals.update_one({"_id": ObjectId(hospital_id)},
                                     {"$pull": {"departments": {"_id": ObjectId(department_id)}}})
    if result.modified_count:
        return jsonify({"message": "Department removed from hospital!"}), 200
    else:
        abort(404, description="Department not found in the specified hospital.")


@hospitals_blueprint.route('/<hospital_id>/departments/<department_id>/equipment', methods=['POST'])
def add_equipment_to_department(hospital_id, department_id):
    data = request.get_json()
    try:
        equipment = Equipment(name=data['name'], quantity=data['quantity'])
        result = db.hospitals.update_one(
            {"_id": ObjectId(hospital_id), "departments._id": ObjectId(department_id)},
            {"$push": {"departments.$.equipment": equipment.__dict__}}
        )
        if result.modified_count:
            return jsonify({"message": "Equipment added to department!"}), 201
        else:
            abort(404, description="Department not found in the specified hospital.")
    except KeyError:
        abort(400, description="Invalid data.")


@hospitals_blueprint.route('/<hospital_id>/departments/<department_id>/facilities', methods=['POST'])
def add_facility_to_department(hospital_id, department_id):
    data = request.get_json()
    try:
        facility = Facility(name=data['name'], rooms=data['rooms'])
        result = db.hospitals.update_one(
            {"_id": ObjectId(hospital_id), "departments._id": ObjectId(department_id)},
            {"$push": {"departments.$.facilities": facility.__dict__}}
        )
        if result.modified_count:
            return jsonify({"message": "Facility added to department!"}), 201
        else:
            abort(404, description="Department not found in the specified hospital.")
    except KeyError:
        abort(400, description="Invalid data.")


@hospitals_blueprint.route('/<hospital_id>/all-equipment', methods=['GET'])
def get_all_equipment_for_hospital(hospital_id):
    hospital = db.hospitals.find_one({"_id": ObjectId(hospital_id)})

    if not hospital:
        abort(404, description="Hospital not found.")

    all_equipment = []

    for department in hospital["departments"]:
        all_equipment.extend(department["equipment"])

    return json_util.dumps(all_equipment), 200


@hospitals_blueprint.route('/<hospital_id>/all-facilities', methods=['GET'])
def get_all_facilities_for_hospital(hospital_id):
    hospital = db.hospitals.find_one({"_id": ObjectId(hospital_id)})

    if not hospital:
        abort(404, description="Hospital not found.")

    all_facilities = []

    for department in hospital["departments"]:
        all_facilities.extend(department["facilities"])

    return json_util.dumps(all_facilities), 200
