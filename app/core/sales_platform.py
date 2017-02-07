from bson.objectid import ObjectId
from models.product import products, ProductsDocument
from models.organization import organizations

def addProduct(newProduct):
    orga = organizations.find_one({'_id': ObjectId(newProduct['owner'])})
    if orga is None:
        return {'data': 'Organization does not exist', 'status': 400}
    product = ProductsDocument(newProduct)
    product.save()
    return { 'data': product, 'status': 200}

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
