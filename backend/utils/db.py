import os
import pymongo
from dotenv import load_dotenv

# Explicitly load the .env file from the backend directory
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
env_file = os.path.join(backend_dir, ".env")
load_dotenv(env_file)

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

print(f"📝 Loaded MONGO_URI from .env: {MONGO_URI}")
print(f"📝 Loaded DATABASE_NAME from .env: {DATABASE_NAME}")

class Database:
    _client = None
    _db = None

    @classmethod
    def connect(cls):
        if cls._client is None or cls._db is None:
            try:
                print("🔗 Attempting to connect to MongoDB...")
                
                # Ensure the URI is valid
                if not MONGO_URI or not DATABASE_NAME:
                    raise ValueError("❌ MONGO_URI or DATABASE_NAME not set in .env file")

                # Attempt connection
                cls._client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
                # Test the connection
                cls._client.admin.command('ping')
                
                # Set the database
                cls._db = cls._client[DATABASE_NAME]
                print(f"✅ Connected to MongoDB database: {DATABASE_NAME}")

            except pymongo.errors.ConnectionFailure as e:
                print(f"❌ MongoDB connection failed: {e}")
                raise e

            except Exception as e:
                print(f"❌ Failed to connect to MongoDB: {e}")
                raise e

    @classmethod
    def get_database(cls):
        if cls._db is None:
            cls.connect()
        return cls._db

    @classmethod
    def get_collection(cls, collection_name):
        db = cls.get_database()
        if db is None:
            raise Exception("❌ No active database connection")
        return db[collection_name]

    @classmethod
    def close(cls):
        if cls._client:
            cls._client.close()
            print("✅ MongoDB connection closed.")
            cls._client = None
            cls._db = None
