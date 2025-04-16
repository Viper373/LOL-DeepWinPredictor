import torch
import numpy as np
from torch.utils.data import Dataset, DataLoader
from BILSTM_Att import BiLSTMModelWithAttention


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


predict_data = np.array([[137, 57,
                          0, 897, 0.442805,
                          1, 30, 0.520687,
                          2, 777, 0.47542,
                          3, 235, 0.457096,
                          4, 223, 0.515908,
                          0, 4, 0.496995,
                          1, 5, 0.516858,
                          2, 518, 0.502752,
                          3, 236, 0.49228,
                          4, 267, 0.507912], ])

batch_size = predict_data.shape[0]
input_size = predict_data.shape[1]
hidden_size = 1024
num_layers = 2
output_size = 1
# 加载测试数据
test_dataset = TestLOLDataset(predict_data)  # 假设test_data是测试数据，格式与训练数据类似
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

# 加载模型
model = BiLSTMModelWithAttention(input_size, hidden_size, num_layers, output_size)
model.load_state_dict(torch.load('BILSTM_Att.pt'))  # 加载训练好的模型
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
