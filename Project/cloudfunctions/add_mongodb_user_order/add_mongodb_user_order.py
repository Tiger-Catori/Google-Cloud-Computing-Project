from pymongo import MongoClient
from bson.json_util import loads

# Cloud function to create an order and empty the basket


def add_mongodb_user_order(request):
    client = MongoClient(
        "mongodb+srv://michaeldb:5RAqimKx&LkG@advanceddevelopmentunit.ks4lp1l.mongodb.net/?retryWrites=true&w=majority")

    print("Connection successful to MongoDB version: " +
          client.server_info()['version'])

    db = client['GameStore']['Users']

    print("Connection successful to collection")

    userId = request.form['userId']

    content = loads(request.form['content'])

    orderDetails = {
            'timestamp': request.form['timestamp'],
            'name': request.form['name'],
            'address': request.form['address'],
            'paymentType': request.form['paymentType'],
            'content': content,
            'expectedDeliveryDate': request.form['expectedDeliveryDate'],
            'totalCost': request.form['totalCost'],
            'status': request.form['status']
    }

    myquery = {"userId": userId}
    orders = db.find_one(myquery)['orders']

    orders.append(orderDetails)

    # Add order
    newValues = {"$set": {"orders": orders}}
    response = db.update_one(myquery, newValues)

    # Empty basket
    newValues = {"$set": {"basket": []}}
    response = db.update_one(myquery, newValues)

    return "Order created", 201
