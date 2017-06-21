from api import requires_auth, ensure_fields
from flask import Blueprint, request, jsonify, make_response
from core import project_management

router = Blueprint('project', __name__)

@router.route('/getProject', methods=['POST'])
def getProject():
    if ensure_fields(['id'], request.json):
        ret = project_management.getProject(request.json.get('id'))
        return make_response(jsonify(ret.get('data')), ret.get('status'))
    else:
        return make_response('Wrong request format', 400)

@router.route('/getAllProjects', methods=['GET'])
def getAllProjects():
    ret = project_management.getAllProjects()
    return make_response(jsonify(ret.get('data')), ret.get('status'))

@router.route('/createProject', methods=['POST'])
def createProject():
    if ensure_fields([{'proj': ["name", "description", "amount"]}], request.json):
        ret = project_management.createProject(request.json.get('proj'))
        return make_response(jsonify(ret.get('data')), ret.get('status'))
    else:
        return make_response("Wrong request format", 400)
