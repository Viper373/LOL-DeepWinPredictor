import json
import os

import matplotlib.pyplot as plt
import numpy as np
import torch
from rocketmq.client import PushConsumer
from rocketmq.ffi import _CConsumeStatus
from sklearn.metrics import (accuracy_score, f1_score, precision_score,
                             recall_score)

from BILSTM_Att.BILSTM_Att import BiLSTMModelWithAttention

# RocketMQ配置
consumer = PushConsumer('LOLTestProducerGroup')
consumer.set_namesrv_addr('127.0.0.1:9876')
consumer.subscribe('LOLTestTopic', '*')

# 定义模型架构
input_size = 32  # 这里根据输入数据的特征数进行调整
hidden_size = 1024
num_layers = 2  # LSTM层数
output_size = 1

# 加载保存的 PyTorch 模型
model = BiLSTMModelWithAttention(input_size=input_size, hidden_size=hidden_size, num_layers=num_layers, output_size=output_size)
model.load_state_dict(torch.load('BILSTM_Att.pt', map_location=torch.device('cpu')))
model.eval()  # 将模型设置为评估模式

all_data = []
accuracy_list = []
precision_list = []
recall_list = []
f1_list = []


def callback(msg):
    global all_data
    data = json.loads(msg.body)
    all_data.append(data)
    return _CConsumeStatus.CONSUME_SUCCESS


consumer.register_message_listener(callback)
consumer.start()

# 处理数据
all_data = np.array(all_data)
np.random.shuffle(all_data)

# 进行5次不同的测试
for i in range(5):
    start_idx = i * 390
    end_idx = start_idx + 390
    test_data = all_data[start_idx:end_idx]

    x = test_data[:, 1:]
    x = torch.Tensor(x).unsqueeze(1)

    with torch.no_grad():
        pred_data_y = model(x).cpu().numpy()

    y_true = test_data[:, 0]

    accuracy = accuracy_score(y_true, (pred_data_y > 0.5).astype(int))
    precision = precision_score(y_true, (pred_data_y > 0.5).astype(int))
    recall = recall_score(y_true, (pred_data_y > 0.5).astype(int))
    f1 = f1_score(y_true, (pred_data_y > 0.5).astype(int))

    accuracy_list.append(accuracy)
    precision_list.append(precision)
    recall_list.append(recall)
    f1_list.append(f1)

consumer.shutdown()

# 绘制评估指标图表
metrics = ['Accuracy', 'Precision', 'Recall']
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#000000']
x = np.arange(1, 6)

fig, ax1 = plt.subplots(figsize=(14, 10))

bar_width = 0.15
ax1.bar(x - bar_width, accuracy_list, bar_width, color=colors[0], label='Accuracy')
ax1.bar(x, precision_list, bar_width, color=colors[1], label='Precision')
ax1.bar(x + bar_width, recall_list, bar_width, color=colors[2], label='Recall')

ax1.set_xlabel('Test Number')
ax1.set_ylabel('Score')
ax1.set_ylim(0, 1.1)
ax1.set_title('Evaluation Metrics for 5 Different Test Sets')
ax1.set_xticks(x)
ax1.set_xticklabels([f'{i * 390}-{(i + 1) * 390 - 1}' for i in range(5)], rotation=30)
ax1.grid(axis='y', linestyle='--', alpha=0.7)

for i in range(5):
    ax1.text(x[i] - bar_width, accuracy_list[i] + 0.01, f'{accuracy_list[i]:.2%}', ha='center', va='bottom', fontsize=10, color=colors[0])
    ax1.text(x[i], precision_list[i] + 0.08, f'{precision_list[i]:.2%}', ha='center', va='bottom', fontsize=10, color=colors[1])
    ax1.text(x[i] + bar_width, recall_list[i] + 0.03, f'{recall_list[i]:.2%}', ha='center', va='bottom', fontsize=10, color=colors[2])

ax2 = ax1.twinx()
ax2.plot(x, f1_list, marker='o', color=colors[3], label='F1 Score', linewidth=2)
ax2.set_ylabel('F1 Score')
ax2.set_ylim(0.9, 1)

for i in range(5):
    ax2.text(x[i], f1_list[i] + 0.01, f'{f1_list[i]:.2%}', ha='center', va='bottom', fontsize=10, color=colors[3])

fig.tight_layout(rect=[0, 0, 0.95, 0.95])
fig.legend(loc='upper left', bbox_to_anchor=(1, 1), bbox_transform=ax1.transAxes)

# 保存图像到HDFS
output_path = "/spark/model_test/BILSTM_Att_testImg.png"
os.system(f"hdfs dfs -put {output_path} /spark/model_test/BILSTM_Att_testImg.png")

plt.savefig(output_path)
plt.show()
