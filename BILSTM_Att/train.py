import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import pymongo
import numpy as np
import os
from tqdm import tqdm
from BILSTM_Att import BiLSTMModelWithAttention, LOLDataset

# 检查CUDA是否可用
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 设置随机种子以便结果可复现
torch.manual_seed(42)

# 从MongoDB加载数据
mongo_client = pymongo.MongoClient(os.getenv('MONGO_URL'))
match_data = mongo_client['moba']['lol'].find({}, {'_id': 0})
all_data = []

# 用于转换玩家位置的字典
position_dict = {'TOP': 0, 'JUN': 1, 'MID': 2, 'ADC': 3, 'SUP': 4}

# 提取数据并进行转换
for value in match_data:
    info = [value['matchWin'], int(value['teamAId']), int(value['teamBId'])]
    for i in range(1, 6):
        info.extend([position_dict[value[f'A{i}playerLocation']], int(value[f'A{i}heroId']), value[f'A{i}heroWinRate']])
    for i in range(1, 6):
        info.extend([position_dict[value[f'B{i}playerLocation']], int(value[f'B{i}heroId']), value[f'B{i}heroWinRate']])
    all_data.append(info)

all_data = np.array(all_data)
np.random.shuffle(all_data)

# 划分训练集和验证集
train_size = int(0.8 * len(all_data))
train_data = all_data[:train_size]
valid_data = all_data[train_size:]

train_dataset = LOLDataset(train_data)
valid_dataset = LOLDataset(valid_data)

batch_size = 512
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
valid_loader = DataLoader(valid_dataset, batch_size=batch_size, shuffle=False)

# 模型参数
input_size = 32  # 输入特征的维度（减去标签）
hidden_size = 1024  # LSTM隐藏层的维度
num_layers = 2  # LSTM层数
output_size = 1  # 输出维度
learning_rate = 0.0001
num_epochs = 1000

# 初始化模型、损失函数和优化器
model = BiLSTMModelWithAttention(input_size, hidden_size, num_layers, output_size).to(device)
criterion = nn.BCELoss()  # 二分类交叉熵损失
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

# 训练模型
for epoch in tqdm(range(num_epochs)):
    model.train()
    epoch_loss = 0
    for X_batch, y_batch in train_loader:
        X_batch, y_batch = X_batch.to(device), y_batch.to(device)
        optimizer.zero_grad()
        outputs = model(X_batch)
        loss = criterion(outputs, y_batch)
        loss.backward()
        optimizer.step()
        epoch_loss += loss.item()
    avg_loss = epoch_loss / len(train_loader)
    print(f'Epoch {epoch + 1}/{num_epochs}, Loss: {avg_loss:.4f}')

# 保存模型
torch.save(model.state_dict(), 'BILSTM_Att_best.pt')
