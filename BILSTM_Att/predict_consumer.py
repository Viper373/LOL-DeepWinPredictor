import json
import torch
import numpy as np
from torch.utils.data import Dataset, DataLoader
from pyspark.sql import SparkSession
from rocketmq.client import PushConsumer
from rocketmq.ffi import _CConsumeStatus
from BILSTM_Att import BiLSTMModelWithAttention, LOLDataset

# 创建SparkSession
spark = SparkSession.builder \
    .appName("BiLSTM_Predict") \
    .master("spark://master:7077") \
    .config("spark.executor.memory", "2g") \
    .config("spark.executor.cores", "2") \
    .config("spark.num.executors", "4") \
    .getOrCreate()


# 修改的LOLDataset类
class LOLDataset(Dataset):
    def __init__(self, data):
        self.data = torch.tensor(data, dtype=torch.float32)  # 转换为张量
        self.X = self.data.view(self.data.size(0), 1, self.data.size(1))  # 调整形状

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        X = self.X[idx]  # 获取张量
        return X


# 预测函数
def predict(data):
    predict_data = np.array([data])

    # 调试输出
    print(f"Received data: {predict_data}")

    if predict_data.size == 0 or predict_data[0] is None:
        print("Received invalid data")
        return

    batch_size = predict_data.shape[0]
    input_size = predict_data.shape[1]
    hidden_size = 1024
    num_layers = 2
    output_size = 1

    # 加载测试数据
    test_dataset = LOLDataset(predict_data)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    # 加载模型
    model = BiLSTMModelWithAttention(input_size, hidden_size, num_layers, output_size)
    model.load_state_dict(torch.load('BILSTM_Att.pt', map_location=torch.device('cpu')))  # 加载训练好的模型
    model.eval()  # 将模型设置为评估模式

    # 进行预测
    predictions = []
    with torch.no_grad():
        for X_batch in test_loader:
            outputs = model(X_batch)
            predictions.extend(outputs.cpu().numpy())

    # 将预测结果转换为二分类（例如，大于0.5为正类，小于等于0.5为负类）
    predictions = np.array(predictions).flatten()
    predictions_binary = np.where(predictions > 0.5, "A队胜利", "B队胜利")
    A_win = predictions[0] * 100
    B_win = (1 - predictions[0]) * 100

    # 输出预测结果
    print(f"A队胜率：{A_win:.2f}%, B队胜率：{B_win:.2f}%, 胜利情况：{predictions_binary[0]}")


# 设置RocketMQ消费者
consumer = PushConsumer('LOLProducerGroup')
consumer.set_namesrv_addr('master:9876')


def callback(msg):
    try:
        if not msg.body:
            print("Received empty message body")
            return _CConsumeStatus.CONSUME_SUCCESS

        data = json.loads(msg.body.decode('utf-8'))

        # 调试输出
        print(f"Received message: {data}")

        # 这里假设data包含需要的预测数据
        predict(data)
    except Exception as e:
        print(f"Error processing message: {e}")
    return _CConsumeStatus.CONSUME_SUCCESS


consumer.subscribe('LOLPredictTopic', callback)
consumer.start()

try:
    while True:
        pass
except KeyboardInterrupt:
    consumer.shutdown()
    spark.stop()
