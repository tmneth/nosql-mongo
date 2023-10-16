from typing import List, Optional

from bson.objectid import ObjectId


class Hospital:
    def __init__(self, name: str, address: str):
        self.name = name
        self.address = address
        self.departments: List[Department] = []


class Department:
    def __init__(self, _id: ObjectId, name: str):
        self._id = _id
        self.name = name
        self.equipment: List[Equipment] = []
        self.facilities: List[Facility] = []


class Equipment:
    def __init__(self, name: str, quantity: int):
        self.name = name
        self.quantity = quantity


class Facility:
    def __init__(self, name: str, rooms: int):
        self.name = name
        self.rooms = rooms


class Physician:
    def __init__(self, name: str, age: int, specialty: str, department_id: Optional[int] = None):
        self.name = name
        self.age = age
        self.specialty = specialty
        self.department_id = department_id
        self.certifications: List[Certification] = []


class Certification:
    def __init__(self, name: str, ):
        self.name = name
