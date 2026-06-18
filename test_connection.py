from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")

print("Connected Successfully")
print(client.list_database_names())