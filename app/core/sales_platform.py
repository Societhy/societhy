"""
This module is used to handle request relative to the sales platform functionalities.
Each function correspond to a route.
"""

import json

from bson.json_util import dumps
from bson.objectid import ObjectId
from models.clients import db_filesystem
from models.organization import organizations
from models.product import products, ProductsDocument

def addProduct(newProduct):
    """
    newProduct : object that defines the newProduct.

    This function is used to add a product to an organisation's catalog.

    - The organisation is retrieved in the catalog.
    - The product is crafted.
    - The product is saved in the database.
    - OK -> 200, error -> 400
    """
    newProduct['owner'] = ObjectId(newProduct['owner'])
    orga = organizations.find_one({'_id': newProduct['owner']})
    if orga is None:
        return {'data': 'Organization does not exist', 'status': 400}
    product = ProductsDocument(newProduct)
    product.save()
    return {'data': product, 'status': 200}

def getProductsByOwner(ownerId):
    """
    ownerId : the id of the user you want to get the products.

    This function is used to retrieved every products a user have created.

    - A database request is perform to retrieve the products.
    - OK -> 200
    """
    productsFound = products.find({'owner': ObjectId(ownerId)})
    return {'data': dumps(productsFound), 'status': 200}

def addProductImage(prod_id, pic, type):
    _id = db_filesystem.put(pic)
    ret = products.update_one({'_id': ObjectId(prod_id)}, {'$addToSet': {'pictures' : {'id': _id, 'type': type}}})
    if ret.modified_count < 1:
        print('Image upload failed')
        return {'data': 'Image upload failed ' + str(_id), 'status': 400}
    return {'data': 'Image uploaded', 'status': 200}

def getProductImages(prod_id):
    images = []
    prod = products.find_one({'_id': ObjectId(prod_id)})
    if prod.get('pictures'):
        for img in prod.get('pictures'):
            images.append("data:"+ img["type"]+";base64," + json.loads(dumps(db_filesystem.get(img["id"]).read()))["$binary"])
    return {'data': images, 'status': 200}


def updateProduct(productId, updateFields):
    """
    productId : The id of the product that will be updated.
    updateFields : object that represent the fields to update.

    This function is used to update some data about a given product

    - A database request is perform to update the fields.
    - OK -> 200, error -> 400
    """
    result = products.update_one({'_id': ObjectId(productId)}, updateFields)
    if result.modified_count < 1:
        return {'data': 'Product does not exist', 'status': 400}
    return {'data': result.raw_result, 'status': 200}

def addReviewToProduct(productId, review):
    """
    """
    result = products.update_one({'_id': ObjectId(productId)}, {'$addToSet': {'reviewList': review}})
    if result.modified_count < 1:
        return {'data': 'Product does not exist', 'status': 400}
    return {'data': 'Review added', 'status': 200}

def removeProduct(productId):
    """
    productId : id of the product that will be removed.

    This function is used to delete a product in the database.

    - A databse request is performed to delete the product.
    - OK -> 200, error -> 400
    """
    result = products.delete_one({'_id': ObjectId(productId)})
    if result.deleted_count < 1:
        return {'data': 'Product does not exist', 'status': 400}
    return {'data': 'Product deleted', 'status': 200}

def changeProductStock(productId, value):
    """
    productId : id of the product who the stock  will be updated.
    value : the new stock.

    This function is used to update the stock of an product

    - A databse request is performed to update the product's stock.
    - OK -> 200, error -> 400
    """
    result = update_one({'_id': ObjectId(productId)}, {'$inc': {'stock': value}})
    if result.modified_count:
        return {'data': 'Product does not exist', 'status': 400}
    return {'data': result.raw_result, 'status': 200}
