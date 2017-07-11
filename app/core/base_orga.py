"""
This module is fot hangling all the basic organisations-related requests.
Every function is defined by her own.
"""

import json

from datetime import datetime
from bson import objectid, errors, json_util
from core.utils import toWei, getYoutubeID
from ethjsonrpc.exceptions import BadResponseError
from flask import Response
from models.clients import db_filesystem
from models.contract import contracts
from models.notification import NotificationDocument as notification
from models.orga_models import *
from models.organization import organizations
from models.transaction import transactions

from io import BytesIO


def getOrgaDocument(user, _id=None, name=None):
    """
    user : user model document that represent the user who made the request.
    id : ObjectId who represent the organisation.
    name : name of the orga
    You must provide id OR name.

    The function will return a description of the requested organisation and the associated rights.
    """

    orga = None
    rights = None

    if _id:
        try:
            _id = objectid.ObjectId(_id)
        except errors.InvalidId:
            return {"data": "Not a valid ObjectId, it must be a 12-byte input or a 24-character hex string",
                    "status": 400}
        orga = organizations.find_one({"_id": _id})
        if orga is None:
            return {"data": "Organization does not exist", "status": 400}

    elif name:
        orga = list(organizations.find({"name": name}))
        if len(orga) == 1:
            orga = orga[0]
        elif len(orga) < 1:
            return {"data": "Organization does not exist", "status": 400}

    if user:
        if user.get('account') in orga.get('members'):
            tag = orga["members"].get(user['account'])['tag']
            rights = orga['rights'][tag]
            orga["uploaded_documents"][:] = [doc for doc in orga["uploaded_documents"] if tag in doc["privacy"] or "default" in doc["privacy"]]

    if not rights:
        rights = orga.default_rights.get('default')
        orga["uploaded_documents"][:] = [doc for doc in orga["uploaded_documents"] if "default" in doc["privacy"]]

    if orga.get('profile_picture'):
        orga["picture"] = ("data:" + orga["profile_picture"]["profile_picture_type"] + ";base64," + json.loads(
            json_util.dumps(db_filesystem.get(orga["profile_picture"]["profile_picture_id"]).read()))["$binary"])
    return {
        "data": {"orga": orga, "rights": rights},
        "status": 200
    }


def getAllOrganizations():
    """
    Return all the registered organisations.
    """
    orgas = list(organizations.find({"rules.hidden": False}, organizations.public_info))
    return {
        "data": orgas,
        "status": 200
    }


def createOrga(user, password, newOrga):
    """
    user : user model document that represent the user who made the request.
    password : password of the user's ethereum wallet. Needed to trigger the action on the blockchain.
    newOrga : define the organisation the user want to create.

    The purpose of this function is to create an new organisation on Sociehty.
    It first unlock the ethereum account of the user who want to create an organisation.
    Then, it instanciate a new organisation model documentation.
    Then, it try to deploy the contract who represent the organisation on the blockchain.
    Status 200 is returned if all is OK, if not 400 is returned.
    """

    if not user.unlockAccount(password=password):
        return {"data": "Invalid password!", "status": 400}
    for entry in ["name", "description", "gov_model", "rules"]:
        if entry not in newOrga:
            return {"data": "Required field %s not found in organisation document" % entry, "status": 400}

    rules_contract = governances.get(newOrga["gov_model"]).get('rulesContract')
    token_contract = governances.get(newOrga["gov_model"]).get('tokenContract')
    token_freezer_contract = governances.get(newOrga["gov_model"]).get('tokenFreezerContract')
    registry_contract = 'ControlledRegistry' if newOrga.get('rules').get(
        'accessibility') == "private" else governances.get(newOrga["gov_model"]).get('registryContract')

    instance = governances[newOrga["gov_model"]]["templateClass"](
        doc=newOrga,
        owner=user.public(),
        board_contract='Societhy',
        rules_contract=rules_contract,
        token_contract=token_contract,
        token_freezer_contract=token_freezer_contract,
        registry_contract=registry_contract,
        gen_skel=True)
    try:
        tx_hash = instance.deployContract(from_=user, password=password, args=[newOrga.get('name')])
    except BadResponseError as e:
        return {"data": str(e), "status": 400}

    return {
        "data": {"orga": instance, "tx_hash": tx_hash},
        "status": 200
    }


def addOrgaProfilePicture(user, orga_id, pic, pic_type):
    """
    user : user model document that represent the user who made the request.
    orga_id : id of the organisation the user want to add a profile picture.
    pic : the photo's bytes.
    pic_type : the MIME type of the photo. e.g. : image/jpeg.

    This function insert in the database the new photo of a given organisation.
    Thanks to the GridFS sytem, photos can be inserted in a database without performance loss.
    """

    _id = db_filesystem.put(pic)
    ret = organizations.update_one({"_id": objectid.ObjectId(orga_id)}, {
        "$set": {"profile_picture": {"profile_picture_id": _id, "profile_picture_type": pic_type}}})
    if ret.modified_count <= 1:
        return {"data": "Photo uploade failure, not inserted into database", "status": 400}
    return {"data": "OK", "status": 200}


def addOrgaDocuments(user, orga_id, doc, name, doc_type, size, privacy):
    """
    user : user model document that represent the user who made the request.
    orga_id : id of the organisation the user want to add documents.
    doc : document bytes
    name : document name
    doc_type : MIME type of the document.
    size : size of the document.
    privacy : privacy of the document.

    This function insert in the database documents related to a given organisation.
    Thanks to the GridFS sytem, documents can be inserted in a database without performance loss.
    """
    _id = db_filesystem.put(doc, doc_type=doc_type, name=name)
    orga = organizations.find_one({"_id": objectid.ObjectId(orga_id)})
    orga['uploaded_documents'].append({"doc_id": _id, "doc_type": doc_type, "doc_name": name, "size": size, "privacy": privacy})
    orga.save_partial()
    print(len(orga['uploaded_documents']))
    # ret = organizations.update_one({"_id": objectid.ObjectId(orga_id)}, {
    #     "$addToSet": {"uploaded_documents": {"doc_id": _id, "doc_type": doc_type, "doc_name": name, "size": size, "privacy": privacy}}})
    # if ret.modified_count < 1:
    #     return {"data": 'Cannot insert document', "status": 400}
    return {"data": 'Document uploaded', "status": 200}


def getOrgaUploadedDocument(doc_id, doc_name):
    """
    user : user model document that represent the user who made the request.
    doc_id : id of the document user want to retrieve.
    doc_name : name of the document user want to retrieve.

    This fuction allow user to download a document who has been previously uploaded.
    """

    # TODO : check if user allowed to download doc

    gfile = db_filesystem.get(objectid.ObjectId(doc_id))
    strIO = BytesIO()
    strIO.write(gfile.read())
    strIO.seek(0)
    return strIO


def joinOrga(user, password, orga_id, tag="member"):
    """
    user : user model document that represent the user who made the request
    password : password used to unlock the ethereum account of the user.
    orga_id : id of the orga the user want to join-in.
    rtag : role attribued to the user. Default is regular member.

    This function is called to add an user to an organisation.

    First, the eth. account is unlocked.
    The organisation in retrieved from database.
    The join() method of the orga model document is called to insert this new user in database.
    A notification is pushed.
    On an error, 400 is returned, on an OK 200 is returned.
    """
    if not user.unlockAccount(password=password):
        return {"data": "Invalid password!", "status": 400}
    orga = organizations.find_one({"_id": objectid.ObjectId(orga_id)})
    if not orga:
        return {"data": "Organization does not exists", "status": 400}
    try:
        tx_hash = orga.join(user, tag, password=password)
        if tx_hash is False:
            return {"data": "User does not have permission to join", "status": 400}
    except BadResponseError as e:
        return {"data": str(e), "status": 400}
    return {
        "data": tx_hash,
        "status": 200
    }


def allowUserTo(user, password, orga_id, allowed_user, action="join"):
    """
    user : user model document that represent the user who made the request
    password : password used to unlock the ethereum account of the user.
    orga_id : id of the orga the user want to join-in.
    rtag : role attribued to the user. Default is regular member.

    This function is called to add an user to an organisation.

    First, the eth. account is unlocked.
    The organisation in retrieved from database.
    The join() method of the orga model document is called to insert this new user in database.
    A notification is pushed.
    On an error, 400 is returned, on an OK 200 is returned.
    """
    if not user.unlockAccount(password=password):
        return {"data": "Invalid password!", "status": 400}
    orga = organizations.find_one({"_id": objectid.ObjectId(orga_id)})
    if not orga:
        return {"data": "Organization does not exists", "status": 400}
    try:
        tx_hash = orga.allow(user, allowed_user, action, password=password)
        if tx_hash is False:
            return {"data": "User does not have permission to join", "status": 400}
    except BadResponseError as e:
        return {"data": str(e), "status": 400}
    return {
        "data": tx_hash,
        "status": 200
    }


def getOrgaMemberList(user, orga_id):
    """
    user : UserDoc
    orga_id : string for the mongo id
    """

    orga = organizations.find_one({"_id": objectid.ObjectId(orga_id)})
    if not orga:
        return {"data": "Organization does not exists", "status": 400}
    member_list = orga.getMemberList()
    return {
        "data": member_list,
        "status": 200
    }


def getOrgaTransaction(user):
    """
    user : UserDoc
    orga_id : string for the mongo id
    """

    trans = transactions.find_all({}, {"_id": 0});
    return {
        "data": trans,
        "status": 200
    }


def updateOrgaRights(user, orga_id, rights):
    """
    orga_id : string for the mongo id
    rights : data to be push in the database
    """
    orga = organizations.find_one({"_id": objectid.ObjectId(orga_id)})

    if orga.can(user, "edit_rights"):
        orga["rights"] = rights;
        orga.save_partial()
        user.needsReloading()
        tag = orga["members"].get(user['account'])['tag']
        print(tag)
        rights = orga['rights'][tag]
        return {
	        "data": {"rights": orga["rights"], "userRights": rights},
	        "status": 200
        }
    else:
        return {
	        "data": "You don't have the right to change the rights",
	        "status": 403
        }

def inviteUsers(user, orga_id, invited_users):
    """
    orga_id : string for the mongo id
    rights : data to be push in the database
    """
    orga = organizations.find_one({"_id": objectid.ObjectId(orga_id)})
    if orga.can(user, "recruit"):
        orga.inviteUsers(user, invited_users)
        return {
            "data": orga,
            "status": 200
        }
    else:
        return {
	        "data": "You don't have the right to invite",
	        "status": 403
        }

def updateMemberTag(user, orga_id, addr, tag):
    """
    orga_id : string for the mongo id
    rights : data to be push in the database
    """
    orga = organizations.find_one({"_id": objectid.ObjectId(orga_id)})

    if orga.can(user, "edit_jobs"):
        orga["members"][addr]["tag"] = tag;
        orga.save_partial()
        tag = orga["members"].get(user['account'])['tag']
        rights = orga['rights'][tag]
        return {
	        "data": {"rights": orga["rights"], "userRights": rights},
	        "status": 200
        }
    else:
        return {
	        "data": "You don't have the right to change tag",
	        "status": 403
        }


def donateToOrga(user, password, orga_id, donation):
    """
    user : user who want to give funds to an organisation.
    password : used to unlock the wallet of the user.
    orga_id : orga who will receive the funds.
    donation : amount of the donation.

    Function used to transfert funds from an user to an organisation.

    - The user account is unlocked thanks to the password.
    - The organisation is retrieved from the database.
    - A check is performed on the user wallet to see if he do have enough funds.
    - The transfert is lauched on the blockchain.
    - error -> 400 ; OK -> 200
    """

    if not user.unlockAccount(password=password):
        return {"data": "Invalid password!", "status": 400}
    orga = organizations.find_one({"_id": objectid.ObjectId(orga_id)})
    if not orga:
        return {"data": "Organization does not exists", "status": 400}
    donation_amount = float(donation.get('amount'))
    if user.refreshBalance() > donation_amount:
        tx_hash = orga.donate(user, toWei(donation_amount), password=password)
        if tx_hash is False:
            return {"data": "User does not have permission to donate", "status": 400}
    else:
        return {"data": "Not enough funds in your wallet to process donation", "status": 400}
    return {
        "data": tx_hash,
        "status": 200
    }


def createProjectFromOrga(user, password, orga_id, newProject):
    """
    user : user who want to give funds to an organisation.
    password : used to unlock the wallet of the user.
    orga_id : orga who will receive the funds.
    newProject : object that defines the projet user want to create.

    This function is used when an user want to create a project.


    - The wallet is unlocked.
    - The organisation is retrieved in database.
    - The project creations is commited on the blockchain.
    - error -> 400 ; OK -> 200
    """

    if not user.unlockAccount(password=password):
        return {"data": "Invalid password!", "status": 400}

    orga = organizations.find_one({"_id": objectid.ObjectId(orga_id)})
    if not orga:
        return {"data": "Organization does not exists", "status": 400}
    try:
        tx_hash = orga.createProject(user, newProject, password=password)
        if tx_hash is False:
            return {"data": "User does not have permission to create a project", "status": 400}

    except BadResponseError as e:
        return {"data": str(e), "status": 400}
    return {
        "data": tx_hash,
        "status": 200
    }


def leaveOrga(user, password, orga_id):
    """
    user : user who want to give funds to an organisation.
    password : used to unlock the wallet of the user.
    orga_id : id of the orga the user want to leave.

    This function is called when an user want to leave an organisation.

    - The wallet is unlocked.
    - The leave order is commited on the blockchain.
    - error -> 400 ; OK -> 200
    """

    if not user.unlockAccount(password=password):
        return {"data": "Invalid password!", "status": 400}

    orga_instance = organizations.find_one({"_id": objectid.ObjectId(orga_id)})
    try:
        tx_hash = orga_instance.leave(user, password=password)
        if tx_hash is False:
            return {"data": "User does not have permission to leave", "status": 400}
    except BadResponseError as e:
        return {"data": str(e), "status": 400}

    return {
        "data": tx_hash,
        "status": 200
    }


def removeMember(user, member_account, password, orga_id):
    """
    user : user who want to remove a member from the organisation.
    member_addr: member to be removed from the organisation.
    password : used to unlock the wallet of the user.
    orga_id : id of the orga the user want to leave.

    This function is called when an user wants to remove a member from the organisation.

    - The wallet is unlocked.
    - The leave order is commited on the blockchain.
    - error -> 400 ; OK -> 200
    """

    if not user.unlockAccount(password=password):
        return {"data": "Invalid password!", "status": 400}

    orga_instance = organizations.find_one({"_id": objectid.ObjectId(orga_id)})
    try:
        tx_hash = orga_instance.removeMember(user, member_account, password=password)
        if tx_hash is False:
            return {"data": "User does not have permission to leave", "status": 400}
    except BadResponseError as e:
        return {"data": str(e), "status": 400}

    return {
	"data": tx_hash,
	"status": 200
    }


def getHisto(token, orga_id, date):
    data = notification.getHisto(orga_id, date)
    return {
        "data": data,
        "status": 200
    }


def createOffer(user, password, orga_id, offer):
    if not user.unlockAccount(password=password):
        return {"data": "Invalid password!", "status": 400}
    orga_instance = organizations.find_one({"_id": objectid.ObjectId(orga_id)})
    if not orga_instance:
        return {"data": "Organization does not exists", "status": 400}
    try:
        tx_hash = orga_instance.createOffer(user, offer, password=password)
        if tx_hash is False:
            return {"data": "User does not have permission to create an offer", "status": 400}
        elif tx_hash == "missing param":
            return {"data": "Missing required field in the offer creation request", "status": 400}
    except BadResponseError as e:
        return {"data": str(e), "status": 400}
    return {
        "data": tx_hash,
        "status": 200
    }


def cancelOffer(user, password, orga_id, offer_id):
    if not user.unlockAccount(password=password):
        return {"data": "Invalid password!", "status": 400}
    orga_instance = organizations.find_one({"_id": objectid.ObjectId(orga_id)})
    if not orga_instance:
        return {"data": "Organization does not exists", "status": 400}
    try:
        tx_hash = orga_instance.cancelOffer(user, offer_id, password=password)
        if tx_hash is False:
            return {"data": "User does not have permission to create an offer", "status": 400}

    except BadResponseError as e:
        return {"data": str(e), "status": 400}
    return {
        "data": tx_hash,
        "status": 200
    }


def createProposal(user, password, orga_id, offer_id, duration=None):
    if not user.unlockAccount(password=password):
        return {"data": "Invalid password!", "status": 400}
    orga_instance = organizations.find_one({"_id": objectid.ObjectId(orga_id)})
    if not orga_instance:
        return {"data": "Organization does not exists", "status": 400}
    try:
        tx_hash = orga_instance.createProposal(user, offer_id, duration, password=password)
        if tx_hash is False:
            return {"data": "User does not have permission to create an offer", "status": 400}

    except BadResponseError as e:
        return {"data": str(e), "status": 400}
    return {
        "data": tx_hash,
        "status": 200
    }


def voteForProposal(user, password, orga_id, proposal_id, vote):
    if not user.unlockAccount(password=password):
        return {"data": "Invalid password!", "status": 400}
    orga_instance = organizations.find_one({"_id": objectid.ObjectId(orga_id)})
    if not orga_instance:
        return {"data": "Organization does not exists", "status": 400}
    try:
        tx_hash = orga_instance.voteForProposal(user, proposal_id, vote, password=password)
        if tx_hash is False:
            return {"data": "User does not have permission to create an offer", "status": 400}

    except BadResponseError as e:
        return {"data": str(e), "status": 400}
    return {
        "data": tx_hash,
        "status": 200
    }


def refreshProposals(orga_id):
    orga_instance = organizations.find_one({"_id": objectid.ObjectId(orga_id)})
    if not orga_instance:
        return {"data": "Organization does not exists", "status": 400}
    ret = orga_instance.refreshProposals()
    return {
        "data": ret,
        "status": 200
    }


def executeProposal(user, password, orga_id, proposal_id):
    if not user.unlockAccount(password=password):
        return {"data": "Invalid password!", "status": 400}
    orga_instance = organizations.find_one({"_id": objectid.ObjectId(orga_id)})
    if not orga_instance:
        return {"data": "Organization does not exists", "status": 400}
    try:
        tx_hash = orga_instance.executeProposal(user, proposal_id, password=password)
        if tx_hash is False:
            return {"data": "User does not have permission to create an offer", "status": 400}

    except BadResponseError as e:
        return {"data": str(e), "status": 400}
    return {
        "data": tx_hash,
        "status": 200
    }


def withdrawFundsFromOffer(user, password, orga_id, offer_id):
    if not user.unlockAccount(password=password):
        return {"data": "Invalid password!", "status": 400}

    offer_instance = contracts.find_one({"_id": objectid.ObjectId(offer_id)})
    orga_instance = organizations.find_one({"_id": objectid.ObjectId(orga_id)})

    if not offer_instance:
        return {"data": "Offer does not exists", "status": 400}
    try:
        tx_hash = orga_instance.withdrawFundsFromOffer(user, offer_instance, password=password)
        if tx_hash is False:
            return {"data": "User does not have permission to create an offer", "status": 400}

    except BadResponseError as e:
        return {"data": str(e), "status": 400}
    return {
        "data": tx_hash,
        "status": 200
    }


def publishNews(user, title, text, orga_id, yt_url):
    orga = organizations.find_one({"_id": objectid.ObjectId(orga_id)})
    if not orga:
        return {"data": "orga does not exist", "status": 400}
    if not orga.can(user, "publish_news"):
        return {"data": "you can not publish news !", "status": 400}
    date = json.dumps(datetime.now(), default=json_util.default)
    date = json.loads(date)["$date"]
    payload = {
            "title": title,
            "text": text,
            "createdAt": date,
            "writer": user["name"],
        }
    yt_url = getYoutubeID(yt_url)
    if yt_url != "":
        payload["yt_url"] = yt_url
    orga.get("news").append(payload)
    orga.save_partial()
    for k, v in orga.get("members").items():
        notif = notification({
            "sender": {"id": objectid.ObjectId(orga.get("_id")), "type": "organization"},
            "subject": {"id": v.get("_id"), "type": "user"},
            "category": "newsPublished",
            "angularState": {
                "route": "app.organization",
                "params": {
                    "_id": str(orga.get("_id")),
                    "name": orga.get("name")
                }
            },
            "description": "Organisation " + orga.get("name") + " published \"" + title + "\""
        })
        notif.save()
    return {"data": {"orga": orga, "news_key": date}, "status": 200}


def publishNewsPhoto(user, orga_id, news_key, doc, name, doc_type):
    orga = organizations.find_one({"_id": objectid.ObjectId(orga_id)})
    if not orga:
        return {"data": "orga does not exist", "status": 400}
    if not orga.can(user, "publish_news"):
        return {"data": "you can not publish news !", "status": 400}
    news = None
    for item in orga.get("news"):
        if str(item["createdAt"]) == news_key:
            news = item
    if news is None:
        return {"data": "news don't exist !", "status": 400}
    _id = db_filesystem.put(doc, doc_type=doc_type, name=name)
    if not news.get("img"):
        news["img"] = []
    news["img"].append(
        {
            "_id": _id,
            "doc_type": doc_type
        }
    )
    orga.save_partial()
    return {"data": {"orga": orga}, "status": 200}


def getNewsPhoto(orga_id, news_key):
    orga = organizations.find_one({"_id": objectid.ObjectId(orga_id)})
    images = []
    if not orga:
        return {"data": "orga does not exist", "status": 400}
    news = None
    for item in orga.get("news"):
        if str(item["createdAt"]) == str(news_key):
            news = item
    if news is None:
        return {"data": "news don't exist !", "status": 400}
    if news.get('img'):
        for img in news.get('img'):
            payload = json.loads(json_util.dumps(db_filesystem.get(img["_id"]).read()))["$binary"]
            images.append("data:" +
                          img["doc_type"] +
                          ";base64," +
                          payload)
    return {'data': images, 'status': 200}
