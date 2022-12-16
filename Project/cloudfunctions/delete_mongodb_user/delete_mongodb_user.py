from pymongo import MongoClient

# Cloud function to delete users in mongo

def delete_mongodb_user(request):
    client = MongoClient(
        "mongodb+srv://michaeldb:5RAqimKx&LkG@advanceddevelopmentunit.ks4lp1l.mongodb.net/?retryWrites=true&w=majority")

    print("Connection successful to MongoDB version: " +
          client.server_info()['version'])

    db = client['GameStore']['Users']

    print("Connection successful to collection")

    myquery = {"userId": request.form['userId']}

    db.delete_one(myquery)

    return '201'
