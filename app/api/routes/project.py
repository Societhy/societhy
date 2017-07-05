from api import requires_auth, ensure_fields, populate_user
from flask import Blueprint, request, jsonify, make_response
from bson import objectid
from core import base_project, base_orga
from models.organization import organizations
from models.user import users

router = Blueprint('project', __name__)

@router.route('/getProject', methods=['POST'])
@populate_user
def getProject(user):
    if ensure_fields(['id'], request.json):
        ret = base_project.getProject(user, request.json.get('id'))
        return make_response(jsonify(ret.get('data')), ret.get('status'))
    else:
        return make_response('Wrong request format', 400)

@router.route('/getAllProjects', methods=['GET'])
def getAllProjects():
    ret = base_project.getAllProjects()
    return make_response(jsonify(ret.get('data')), ret.get('status'))

@router.route('/createProject', methods=['POST'])
@requires_auth
def createProject(user):
    if ensure_fields(['password', 'socketid', 'owner_id', {'newProject': ['name', 'description', 'campaign']}], request.json):
        orga_obj = organizations.find_one({"_id": objectid.ObjectId(request.json.get('owner_id'))})
        user_obj = users.find_one({"_id": objectid.ObjectId(request.json.get('owner_id'))})
        if orga_obj is not None:
            ret = base_orga.createProjectFromOrga(user, request.json.get('password'), orga_obj, request.json.get('newProject'))
        elif user_obj is not None:
            ret = base_project.createProject(user, request.json.get('password'), user_obj, request.json.get('newProject'))
        else:
            return make_response("Must be logged in or member of an organization", 400)
        return make_response(jsonify(ret.get('data')), ret.get('status'))
    else:
        return make_response("Wrong request format", 400)

@router.route('/joinProject', methods=['POST'])
@requires_auth
def joinProject(user):
    if ensure_fields(['password', 'socketid', 'proj_id', 'tag'], request.json):
        ret = base_project.joinProject(user, request.json.get('password'), request.json.get('proj_id'), request.json.get('tag'))
        return make_response(jsonify(ret.get('data')), ret.get('status'))
    else:
        return make_response("Wrong request format", 400)

@router.route('/leaveProject', methods=['POST'])
@requires_auth
def leaveProject(user):
    if ensure_fields(['password', 'socketid', 'proj_id'], request.json):
        ret = base_project.leaveProject(user, request.json.get('password'), request.json.get('proj_id'))
        return make_response(jsonify(ret.get('data')), ret.get('status'))
    else:
        return make_response("Wrong request format", 400)

@router.route('/donateToProject', methods=['POST'])
@requires_auth
def donateToProject(user):
    if ensure_fields(['password', 'socketid', 'proj_id', 'donation'], request.json):
        ret = base_project.donateToProject(user, request.json.get('password'), request.json.get('proj_id'), request.json.get('donation'))
        return make_response(jsonify(ret.get('data')), ret.get('status'))
    else:
        return make_response("Wrong request format", 400)

@router.route('/refreshProject/<project_id>')
def refreshProject(project_id):
    ret = base_project.refreshProject(project_id)
    return make_response(jsonify(ret.get('data')), ret.get('status'))
