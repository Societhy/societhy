from bson.objectid import ObjectId
from bson.json_util import dumps
from models.product import products, ProductsDocument
from models.organization import organizations

def addProduct(newProduct):
    newProduct['owner'] = ObjectId(newProduct['owner'])
    orga = organizations.find_one({'_id': newProduct['owner']})
    if orga is None:
        return {'data': 'Organization does not exist', 'status': 400}
    product = ProductsDocument(newProduct)
    product.save()
    return {'data': product, 'status': 200}

def getProductsByOwner(ownerId):
    productsFound = products.find({'owner': ObjectId(ownerId)})
    return {'data': dumps(productsFound), 'status': 200}

def updateProduct(productId, updateFields):
    result = products.update_one({'_id': ObjectId(productId)}, updateFields)
    if result.modified_count < 1:
        return {'data': 'Product does not exist', 'status': 400}
    return {'data': result.raw_result, 'status': 200}

def removeProduct(productId):
    result = products.delete_one({'_id': ObjectId(productId)})
    if result.deleted_count < 1:
        return {'data': 'Product does not exist', 'status': 400}
    return {'data': 'Product deleted', 'status': 200}

def changeProductStock(productId, value):
    result = update_one({'_id': ObjectId(productId)}, {'$inc': {'stock': value}})
    if result.modified_count:
        return {'data': 'Product does not exist', 'status': 400}
    return {'data': result.raw_result, 'status': 200}
