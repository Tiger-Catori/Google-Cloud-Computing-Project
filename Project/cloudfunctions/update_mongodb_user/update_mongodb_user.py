from pymongo import MongoClient
from bson.json_util import loads

# Cloud function to update users in mongo


def update_mongodb_user(request):
    client = MongoClient(
        "mongodb+srv://michaeldb:5RAqimKx&LkG@advanceddevelopmentunit.ks4lp1l.mongodb.net/?retryWrites=true&w=majority")

    print("Connection successful to MongoDB version: " +
          client.server_info()['version'])

    db = client['GameStore']['Users']

    print("Connection successful to collection")

    myquery = {"userId": request.form['userId']}

    orders = db.find_one(myquery)['orders']

    statusList = loads(request.form['orderStatuses'])

    statusListIndex = 0
    for order in orders:
        order['status'] = statusList[statusListIndex]
        statusListIndex += 1

    data_to_change = {
        'name': request.form['name'],
        'admin': request.form['admin'],
        'orders': orders
    }

    newvalues = {"$set": data_to_change}

    db.update_one(myquery, newvalues)

    return '201'
