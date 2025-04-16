from pymongo import MongoClient

# 本地MongoDB连接
local_client = MongoClient('mongodb://localhost:27017/')
local_db = local_client['moba']

# 虚拟机MongoDB连接
vm_client = MongoClient('mongodb://master:27017/')
vm_db = vm_client['moba']

# 获取所有集合的名称
collections = local_db.list_collection_names()

BATCH_SIZE = 1000

for collection_name in collections:
    local_collection = local_db[collection_name]
    vm_collection = vm_db[collection_name]

    documents = local_collection.find()
    batch = []

    for document in documents:
        batch.append(document)
        if len(batch) == BATCH_SIZE:
            vm_collection.insert_many(batch)
            batch = []

    # 插入剩余的文档
    if batch:
        vm_collection.insert_many(batch)

print("数据复制完成！")
