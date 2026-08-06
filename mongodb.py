import os
from dotenv import load_dotenv
from pymongo import MongoClient
load_dotenv()

MONGO_URI = os.environ.get("MONGO_URI")

client = MongoClient(MONGO_URI)

db = client["leadflow"]

admin_collection = db["admin"]
leads_collection = db["leads"]
followups_collection = db["followups"]
settings_collection = db["settings"]
admin_profile_collection = db["admin_profile"]
activities_collection = db['activities']