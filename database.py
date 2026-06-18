from pymongo import MongoClient

mongo_client = MongoClient("mongodb://localhost:27017")

bank_database = mongo_client["bank_management_db"]

customer_collection = bank_database["customers"]
account_collection = bank_database["accounts"]
employee_collection = bank_database["employees"]
branch_collection = bank_database["branches"]
transaction_collection = bank_database["transactions"]