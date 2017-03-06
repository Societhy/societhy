from mongokat import Collection, Document
from bson.objectid import ObjectId
from .clients import client

class ProductsDocument(Document):
	def __init__(self, doc=None, mongokat_collection=None, fetched_fields=None, gen_skel=None):
		super().__init__(doc, products, fetched_fields, gen_skel)

class ProductsCollection(Collection):
    product_info = [
        'isDigital',
        'owner',
        'name',
        'picture'
        'description',
        'price',
        'paymentMode',
        'shippingMode',
        'stock'
    ]

    document_class = ProductsDocument

products = ProductsCollection(collection=client.main.products)
