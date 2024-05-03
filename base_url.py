from pymongo import MongoClient

# def get_mongo_connection():
#     CONNECT_TIMEOUT_MS = 900000
#     SOCKET_TIMEOUT_MS = 900000
#     client = MongoClient(
#         "mongodb://localhost:27018/",  # Change to use the Docker container port
#         connectTimeoutMS=CONNECT_TIMEOUT_MS,
#         socketTimeoutMS=SOCKET_TIMEOUT_MS,
#     )
#     db = client["Trending-dataDB"]  # Change to the specified database name
#     return db

# def get_database():
#     CONNECT_TIMEOUT_MS = 900000
#     SOCKET_TIMEOUT_MS = 900000
#     client = MongoClient(
#         "mongodb://localhost:27018/",  # Change to use the Docker container port
#         connectTimeoutMS=CONNECT_TIMEOUT_MS,
#         socketTimeoutMS=SOCKET_TIMEOUT_MS,
#     )
#     db = client["Trending-dataDB"]  # Change to the specified database name
#     return db





# def get_mongo_connection():
#     URI = "mongodb://localhost:27017/"
#     client = MongoClient(URI)
#     db = client["Scout"]
#     return db





def get_mongo_connection():
    URI = f"mongodb+srv://muhammadadil:fgBnah2l95vai00Y@cluster0.hwqa22w.mongodb.net/playerdb"
    client = MongoClient(URI)
    db = client["PLayersDB"]
    return db



# def get_database():
#     URI = f"mongodb+srv://muhammadadil:fgBnah2l95vai00Y@cluster0.hwqa22w.mongodb.net/playerdb"
#     client = MongoClient(URI)
#     db = client["racing-reference"]
#     return db