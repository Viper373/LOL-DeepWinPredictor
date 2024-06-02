import os
import sys
import numpy as np
import pymongo
import torch
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import env
from BILSTM_Att import BiLSTMModelWithAttention
import matplotlib.pyplot as plt

script_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目的根目录
project_root = os.path.abspath(os.path.join(script_dir, os.pardir))
if project_root not in sys.path:
    sys.path.append(project_root)

# 从MongoDB加载数据
mongo_client = pymongo.MongoClient(env.MONGO_URL)
match_data = mongo_client['moba']['lol'].find({}, {'_id': 0})
all_data = []

# 用于替换玩家位置的字典
position_dict = {'TOP': 0, 'JUN': 1, 'MID': 2, 'ADC': 3, 'SUP': 4}

for value in match_data:
    info = [value['matchWin'], int(value['teamAId']), int(value['teamBId'])]
    for i in range(1, 6):
        info.extend([position_dict[value[f'A{i}playerLocation']], int(value[f'A{i}heroId']), value[f'A{i}heroWinRate']])
    for i in range(1, 6):
        info.extend([position_dict[value[f'B{i}playerLocation']], int(value[f'B{i}heroId']), value[f'B{i}heroWinRate']])
    all_data.append(info)

# 转换为numpy数组
all_data = np.array(all_data)
np.random.shuffle(all_data)

# 定义模型架构
input_size = all_data.shape[1] - 1
hidden_size = 1024
num_layers = 2  # LSTM层数
output_size = 1

# 加载保存的 PyTorch 模型
model = BiLSTMModelWithAttention(input_size=input_size, hidden_size=hidden_size, num_layers=num_layers, output_size=output_size)
model.load_state_dict(torch.load('BILSTM_Att.pt'))
model.eval()  # 将模型设置为评估模式

# 存储评估结果的列表
accuracy_list = []
precision_list = []
recall_list = []
f1_list = []

# 进行5次不同的测试
for i in range(5):
    # 选择不同的测试数据切片
    start_idx = 30000 + i * 390
    end_idx = start_idx + 390
    test_data = all_data[start_idx:end_idx]

    # 准备输入数据进行预测
    x = test_data[:, 1:]
    x = torch.Tensor(x).unsqueeze(1)  # 增加维度以适应批次大小和序列长度

    # 进行预测
    with torch.no_grad():
        pred_data_y = model(x).cpu().numpy()

    # 评估预测结果
    y_true = test_data[:, 0]

    # 计算评估指标
    accuracy = accuracy_score(y_true, (pred_data_y > 0.5).astype(int))
    precision = precision_score(y_true, (pred_data_y > 0.5).astype(int))
    recall = recall_score(y_true, (pred_data_y > 0.5).astype(int))
    f1 = f1_score(y_true, (pred_data_y > 0.5).astype(int))

    # 存储结果
    accuracy_list.append(accuracy)
    precision_list.append(precision)
    recall_list.append(recall)
    f1_list.append(f1)

# 绘制评估指标图表
metrics = ['Accuracy', 'Precision', 'Recall']
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#000000']  # 为每个评估指标使用协调的颜色
x = np.arange(1, 6)  # 测试集编号

fig, ax1 = plt.subplots(figsize=(14, 10))

# 绘制竖着的条形图
bar_width = 0.15
ax1.bar(x - bar_width, accuracy_list, bar_width, color=colors[0], label='Accuracy')
ax1.bar(x, precision_list, bar_width, color=colors[1], label='Precision')
ax1.bar(x + bar_width, recall_list, bar_width, color=colors[2], label='Recall')

ax1.set_xlabel('Test Number')
ax1.set_ylabel('Score')
ax1.set_ylim(0, 1.1)
ax1.set_title('Evaluation Metrics for 5 Different Test Sets')
ax1.set_xticks(x)
ax1.set_xticklabels([f'{30000 + i*390}-{30000 + (i+1)*390 - 1}' for i in range(5)], rotation=30)
ax1.grid(axis='y', linestyle='--', alpha=0.7)

# 添加数值标签，调整位置使其不重叠，并交错放置
for i in range(5):
    ax1.text(x[i] - bar_width, accuracy_list[i] + 0.01, f'{accuracy_list[i]:.2%}', ha='center', va='bottom', fontsize=10, color=colors[0])
    ax1.text(x[i], precision_list[i] + 0.08, f'{precision_list[i]:.2%}', ha='center', va='bottom', fontsize=10, color=colors[1])
    ax1.text(x[i] + bar_width, recall_list[i] + 0.03, f'{recall_list[i]:.2%}', ha='center', va='bottom', fontsize=10, color=colors[2])

# 创建第二个y轴，用于绘制F1值的折线图
ax2 = ax1.twinx()
ax2.plot(x, f1_list, marker='o', color=colors[3], label='F1 Score', linewidth=2)
ax2.set_ylabel('F1 Score')
ax2.set_ylim(0.9, 1)

# 添加F1值数值标签，调整位置使其不重叠
for i in range(5):
    ax2.text(x[i], f1_list[i] + 0.01, f'{f1_list[i]:.2%}', ha='center', va='bottom', fontsize=10, color=colors[3])

fig.tight_layout(rect=[0, 0, 0.95, 0.95])  # 增加上边距
fig.legend(loc='upper left', bbox_to_anchor=(1, 1), bbox_transform=ax1.transAxes)

plt.show()
