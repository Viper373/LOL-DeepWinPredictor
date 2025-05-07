import numpy as np
import pandas as pd
import torch
from BILS import LSTMModelWithAttention
from pyspark.sql import SparkSession
from pyspark.sql.functions import PandasUDFType, col, pandas_udf
from torch.utils.data import DataLoader, Dataset

# 初始化Spark会话
spark = SparkSession.builder \
    .appName("LOLPrediction") \
    .master("spark://master:7077") \
    .config("spark.executor.memory", "1g") \
    .config("spark.sql.debug.maxToStringFields", "500") \
    .config("spark.executor.cores", "4") \
    .getOrCreate()


# 定义测试数据集类
class TestLOLDataset(Dataset):
    def __init__(self, data):
        self.data = np.array(data)  # 将数据转换为 numpy 数组
        self.X = self.data[:].reshape(self.data.shape[0], 1, self.data.shape[1])

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        X = torch.Tensor(self.X[idx])  # 转换为张量
        return X


# 模拟一些预测数据
predict_data = np.array([[137, 57,
                          0, 897, 0.442805,
                          1, 76, 0.489073,
                          2, 777, 0.47542,
                          3, 235, 0.457096,
                          4, 111, 0.503742,
                          0, 24, 0.4998,
                          1, 113, 0.500385,
                          2, 61, 0.48015,
                          3, 429, 0.477242,
                          4, 22, 0.472276], ])

# 将数据转换为PySpark DataFrame
df = spark.createDataFrame(predict_data.tolist(), schema=["col{}".format(i) for i in range(predict_data.shape[1])])

# 加载模型
model = LSTMModelWithAttention(_input_size=predict_data.shape[1], _hidden_size=64, _output_size=1)
model.load_state_dict(torch.load('BILSTM_Att.pt'))  # 加载训练好的模型
model.eval()  # 将模型设置为评估模式


# UDF预测函数
@pandas_udf("float", PandasUDFType.SCALAR)
def predict_udf(*cols):
    data = np.array([cols]).T
    dataset = TestLOLDataset(data)
    dataloader = DataLoader(dataset, batch_size=1, shuffle=False)

    predictions = []
    with torch.no_grad():
        for X_batch in dataloader:
            outputs = model(X_batch)
            predictions.extend(outputs.cpu().numpy())

    prediction = np.array(predictions).flatten()[0]
    return pd.Series([float(prediction)] * len(cols[0]))


# 对DataFrame应用预测UDF
df_with_predictions = df.withColumn("prediction", predict_udf(*[col("col{}".format(i)) for i in range(predict_data.shape[1])]))

# 收集预测结果
predictions = df_with_predictions.select("prediction").collect()
predictions = np.array([row["prediction"] for row in predictions])

# 将预测结果转换为二分类（例如，大于0.5为正类，小于等于0.5为负类）
predictions_binary = np.where(predictions > 0.5, "A队胜利", "B队胜利")
A_win = predictions[0] * 100
B_win = (1 - predictions[0]) * 100

# 输出预测结果
print(f"A队胜率：{A_win:.2f}%, B队胜率：{B_win:.2f}%, 胜利情况：{predictions_binary[0]}")

# 停止Spark会话
spark.stop()
