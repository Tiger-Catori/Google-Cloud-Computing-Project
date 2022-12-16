from pymongo import MongoClient

# Cloud function to remove item from basket


def remove_mongodb_user_basket(request):
    client = MongoClient(
        "mongodb+srv://michaeldb:5RAqimKx&LkG@advanceddevelopmentunit.ks4lp1l.mongodb.net/?retryWrites=true&w=majority")

    print("Connection successful to MongoDB version: " +
          client.server_info()['version'])

    db = client['GameStore']['Users']

    print("Connection successful to collection")

    userId = request.form['userId']
    basketIndex = int(request.form['basketIndex'])

    myquery = {"userId": userId}
    basket = db.find_one(myquery)['basket']

    del basket[basketIndex]

    newValues = {"$set": {"basket": basket}}

    response = db.update_one(myquery, newValues)

    return "Updated basket", 201