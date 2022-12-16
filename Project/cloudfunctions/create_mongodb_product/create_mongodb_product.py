from pymongo import MongoClient
from flask import request

# Cloud function to create products in mongo


def create_mongodb_product(request):
    client = MongoClient(
        "mongodb+srv://michaeldb:5RAqimKx&LkG@advanceddevelopmentunit.ks4lp1l.mongodb.net/?retryWrites=true&w=majority")

    print("Connection successful to MongoDB version: " +
          client.server_info()['version'])

    db = client['GameStore']['Products']

    print("Connection successful to collection")

    product_data = {
        "title": str(request.args['title']),
        "ageRating": str(request.args['ageRating']),
        "pricePerUnit": str(request.args['pricePerUnit']),
        "qty": int(request.args['qty']),
        "imageID": str(request.args['imageID']),
        "tags": request.args['tags'].strip(',')
    }

    result = db.insert_one(product_data)

    print("Created object with ID: " + str(result.inserted_id))

    return str(result.inserted_id)
