from pymongo import MongoClient
from bson.json_util import dumps

# Cloud function to get user summaries


def read_mongodb_user_summaries(request):
    client = MongoClient(
        "mongodb+srv://michaeldb:5RAqimKx&LkG@advanceddevelopmentunit.ks4lp1l.mongodb.net/?retryWrites=true&w=majority")

    print("Connection successful to MongoDB version: " +
          client.server_info()['version'])

    db = client['GameStore']['Users']

    print("Connection successful to collection")

    myCursor = None

    requestedData = {
        '_id': 0,
        'userId': 1,
        'email': 1,
        'name': 1,
        'admin': 1
    }

    myCursor = db.find({}, requestedData)
    list_items = list(myCursor)
    json_data = dumps(list_items)
    return json_data