from api import requires_auth, ensure_fields
from flask import Blueprint, request, jsonify, make_response
from core import base_project

router = Blueprint('project', __name__)

@router.route('/getProject', methods=['POST'])
def getProject():
    if ensure_fields(['id'], request.json):
        ret = base_project.getProject(request.json.get('id'))
        return make_response(jsonify(ret.get('data')), ret.get('status'))
    else:
        return make_response('Wrong request format', 400)

@router.route('/getAllProjects', methods=['GET'])
def getAllProjects():
    ret = base_project.getAllProjects()
    return make_response(jsonify(ret.get('data')), ret.get('status'))

@router.route('/createProject', methods=['POST'])
def createProject():
    if ensure_fields([{'proj': ["name", "description", "amount"]}], request.json):
        ret = base_project.createProject(request.json.get('proj'))
        return make_response(jsonify(ret.get('data')), ret.get('status'))
    else:
        return make_response("Wrong request format", 400)
