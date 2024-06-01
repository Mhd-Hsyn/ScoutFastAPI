from pymongo import MongoClient


################   LIVE DB  ################################

def get_mongo_connection():
    URI = f"mongodb+srv://muhammadadil:Q4gd0FQktFGaUtwN@cluster0.hwqa22w.mongodb.net/"
    client = MongoClient(URI)
    db = client["Scout"]
    return db

################   LOCAL HOST  ################################

# def get_mongo_connection():
#     URI = "mongodb://localhost:27017/"
#     client = MongoClient(URI)
#     db = client["Scout"]
#     return db
