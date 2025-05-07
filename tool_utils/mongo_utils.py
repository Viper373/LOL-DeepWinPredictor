from typing import Dict, List

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from Data_CrawlProcess import env


class MongoUtils:
    def __init__(self):
        uri = env.MONGO_URI
        self.client = MongoClient(uri, server_api=ServerApi('1'))
        self.db = None

    def use_db(self, db_name: str):
        self.db = self.client[db_name]
        return self.db

    def use_collection(self, col_name: str):
        return self.db[col_name]

    def insert_one(self, collection: str, data: Dict):
        return self.use_collection(collection).insert_one(data)

    def insert_many(self, collection: str, data_list: List[Dict]):
        return self.use_collection(collection).insert_many(data_list)

    def find(self, collection: str, query: Dict = None, projection: Dict = None):
        return self.use_collection(collection).find(query or {}, projection)

    def find_one(self, collection: str, query: Dict = None, projection: Dict = None):
        return self.use_collection(collection).find_one(query or {}, projection)

    def update_one(self, collection: str, query: Dict, update: Dict, upsert: bool = False):
        return self.use_collection(collection).update_one(query, update, upsert=upsert)

    def update_many(self, collection: str, query: Dict, update: Dict, upsert: bool = False):
        return self.use_collection(collection).update_many(query, update, upsert=upsert)

    def delete_one(self, collection: str, query: Dict):
        return self.use_collection(collection).delete_one(query)

    def delete_many(self, collection: str, query: Dict):
        return self.use_collection(collection).delete_many(query)

    def count_documents(self, collection: str, query: Dict = None):
        return self.use_collection(collection).count_documents(query or {})

    def create_index(self, collection: str, keys, **kwargs):
        return self.use_collection(collection).create_index(keys, **kwargs)

    def close(self):
        self.client.close()
