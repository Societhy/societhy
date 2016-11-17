from copy import copy
from bson.objectid import ObjectId
import json

class UserJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

def serialize_user(user):
	serialized = copy(user)
	serialized.update({"_id": ObjectId(user.get('_id'))})
	return serialized

def deserialize_user(user):
	deserialized = copy(user)
	deserialized.update({"_id": str(user.get('_id'))})
	return deserialized
