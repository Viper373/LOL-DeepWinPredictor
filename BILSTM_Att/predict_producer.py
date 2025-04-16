import json
from pymongo import MongoClient
from rocketmq.client import Producer, Message

# MongoDB连接
client = MongoClient('mongodb://master:27017,node1:27017,node2:27017/?replicaSet=rs0')
db = client['moba']
collection = db['lol']

# 读取MongoDB中的一条数据
data = collection.find_one()

# 字典映射 playerLocation
location_mapping = {
    "TOP": 0,
    "JUN": 1,
    "MID": 2,
    "ADC": 3,
    "SUP": 4
}


def extract_fields(data):
    extracted_data = [
        data["teamAId"], data["teamBId"],
        location_mapping[data["A1playerLocation"]], data["A1heroId"], data["A1heroWinRate"], location_mapping[data["A2playerLocation"]], data["A2heroId"], data["A2heroWinRate"],
        location_mapping[data["A3playerLocation"]], data["A3heroId"], data["A3heroWinRate"], location_mapping[data["A4playerLocation"]], data["A4heroId"], data["A4heroWinRate"],
        location_mapping[data["A5playerLocation"]], data["A5heroId"], data["A5heroWinRate"], location_mapping[data["B1playerLocation"]], data["B1heroId"], data["B1heroWinRate"],
        location_mapping[data["B2playerLocation"]], data["B2heroId"], data["B2heroWinRate"], location_mapping[data["B3playerLocation"]], data["B3heroId"], data["B3heroWinRate"],
        location_mapping[data["B4playerLocation"]], data["B4heroId"], data["B4heroWinRate"],location_mapping[data["B5playerLocation"]], data["B5heroId"], data["B5heroWinRate"]
    ]
    return extracted_data


# 提取并转换数据
predict_data = extract_fields(data)

# 设置RocketMQ生产者
producer = Producer('LOLProducerGroup')
producer.set_namesrv_addr('master:9876')
producer.start()

# 将数据发送到RocketMQ
msg = Message('LOLPredictTopic')
msg.set_body(json.dumps(predict_data))
producer.send_sync(msg)
producer.shutdown()
