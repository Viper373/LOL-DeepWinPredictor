import torch
import torch.nn as nn
from torch.utils.data import Dataset


# 定义注意力机制
class Attention(nn.Module):
    def __init__(self, hidden_size):
        super(Attention, self).__init__()
        self.attn_weight = nn.Parameter(torch.randn(hidden_size, 1))
        self.softmax = nn.Softmax(dim=1)

    def forward(self, lstm_output):
        # 使用注意力权重
        attn_weights = torch.matmul(lstm_output, self.attn_weight.unsqueeze(0).permute(1, 0))
        attn_weights = self.softmax(attn_weights)
        context = torch.sum(attn_weights * lstm_output, dim=1)
        return context, attn_weights


# 定义带有注意力机制的双向LSTM模型
class BiLSTMModelWithAttention(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size):
        super(BiLSTMModelWithAttention, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        # 双向LSTM层
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, bidirectional=True)

        # 全连接层
        self.fc = nn.Linear(hidden_size * 2, output_size)

    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        # 简单拼接LSTM的最后一个时间步的输出
        lstm_out_concat = torch.cat((lstm_out[:, -1, :self.hidden_size], lstm_out[:, 0, self.hidden_size:]), dim=1)
        final_output = self.fc(lstm_out_concat)
        final_output = torch.sigmoid(final_output)  # 确保输出为概率
        return final_output


# 自定义数据集类
class LOLDataset(Dataset):
    def __init__(self, _data):
        self.data = _data
        self.X = self.data[:, 1:].reshape(self.data.shape[0], 1, self.data.shape[1] - 1)
        self.y = self.data[:, 0]

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        X = self.X[idx]
        y = self.y[idx]
        return torch.Tensor(X), torch.Tensor([y])
