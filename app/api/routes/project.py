from flask import Blueprint

router = Blueprint('project', __name__)

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
