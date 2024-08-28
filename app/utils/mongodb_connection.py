from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://captaintedotron55:jP1S4oKKmwL5qZwf@maincluster.2mlpl.mongodb.net/?retryWrites=true&w=majority&appName=MainCluster"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

db = client.UECloud
users = db.users


def get_db():
    return client.UECloud

def get_collection_users():
    return get_db().users