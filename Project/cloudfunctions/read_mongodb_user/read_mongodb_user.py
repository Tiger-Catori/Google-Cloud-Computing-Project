from pymongo import MongoClient
from bson.json_util import dumps

# Cloud function to get user details from mongo


def read_mongodb_user(request):
    client = MongoClient(
        "mongodb+srv://michaeldb:5RAqimKx&LkG@advanceddevelopmentunit.ks4lp1l.mongodb.net/?retryWrites=true&w=majority")

    print("Connection successful to MongoDB version: " +
          client.server_info()['version'])

    db = client['GameStore']['Users']

    print("Connection successful to collection")

    myCursor = None

    userId = request.args['userId']

    print("Attempting to access ID: " + userId)
    myquery = {"userId": userId}
    myCursor = db.find_one(myquery)

    if myCursor is None:
        # Create an account
        print("Account not found, create account")
        data = {
            'userId': request.args['userId'],
            'email': request.args['email'],
            'name': request.args['name'],
            'admin': False,
            'orders': [],
            'basket': []
        }
        result = db.insert_one(data)

        # Get the new account
        myCursor = db.find_one(myquery)

    json_data = dumps(myCursor)
    return json_data
