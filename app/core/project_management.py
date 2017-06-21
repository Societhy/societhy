import json

from bson import errors, json_util
from bson.objectid import ObjectId
from models.project import projects

def getProject(id):
    proj = projects.find_one({'_id': ObjectId(id)})
    if proj is None:
        return {'data': 'This project does not exist', 'status': 400}
    return {'data': proj, 'status': 200}

def getAllProjects():
    projs = list(projects.find({}))
    return {
        'data': projs,
        'status': 200
    }
