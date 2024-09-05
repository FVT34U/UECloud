from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

_uri = "mongodb+srv://captaintedotron55:jP1S4oKKmwL5qZwf@maincluster.2mlpl.mongodb.net/?retryWrites=true&w=majority&appName=MainCluster"

# Create a new client and connect to the server
_client = MongoClient(_uri, server_api=ServerApi('1'))


def get_db():
    return _client.UECloud

def get_collection_users():
    return get_db().users

def get_collection_storage_entities():
    return get_db().storage_entities