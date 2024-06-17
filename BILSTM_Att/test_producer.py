import pymongo
import json
from rocketmq.client import Producer, Message

# MongoDB配置
mongo_client = pymongo.MongoClient("mongodb://master:27017,node1:27017,node2:27017/moba?replicaSet=rs0")
collection = mongo_client['moba']['lol']

# RocketMQ配置
producer = Producer('LOLTestProducerGroup')
producer.set_namesrv_addr('127.0.0.1:9876')
producer.start()

location_mapping = {
    "TOP": 0,
    "JUN": 1,
    "MID": 2,
    "ADC": 3,
    "SUP": 4
}


def extract_fields(data):
    extracted_data = [
        data["matchWin"], data["teamAId"], data["teamBId"],
        location_mapping[data["A1playerLocation"]], data["A1heroId"], data["A1heroWinRate"],
        location_mapping[data["A2playerLocation"]], data["A2heroId"], data["A2heroWinRate"],
        location_mapping[data["A3playerLocation"]], data["A3heroId"], data["A3heroWinRate"],
        location_mapping[data["A4playerLocation"]], data["A4heroId"], data["A4heroWinRate"],
        location_mapping[data["A5playerLocation"]], data["A5heroId"], data["A5heroWinRate"],
        location_mapping[data["B1playerLocation"]], data["B1heroId"], data["B1heroWinRate"],
        location_mapping[data["B2playerLocation"]], data["B2heroId"], data["B2heroWinRate"],
        location_mapping[data["B3playerLocation"]], data["B3heroId"], data["B3heroWinRate"],
        location_mapping[data["B4playerLocation"]], data["B4heroId"], data["B4heroWinRate"],
        location_mapping[data["B5playerLocation"]], data["B5heroId"], data["B5heroWinRate"]
    ]
    return extracted_data


# 读取数据并发送到RocketMQ
for data in collection.find({}, {'_id': 0}):
    predict_data = extract_fields(data)
    msg = Message('LOLTestTopic')
    msg.set_body(json.dumps(predict_data))
    producer.send_sync(msg)

producer.shutdown()
