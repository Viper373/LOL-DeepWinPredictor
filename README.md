
# 🎮 基于深度学习的英雄联盟胜率预测

## 📚 项目简介
- 🌴项目为本人毕业设计
- 🌱论文题目为《基于深度学习的英雄联盟胜率预测研究》
- 🌲毕业院校：北京石油化工学院（BIPT） 
- 🌳院系：经济管理学院 
- 🌾专业：大数据管理与应用 
- 🌿年级：20级
- 🌵本项目旨在使用双向LSTM（BiLSTM_Att）结合注意力机制预测英雄联盟比赛的胜率。数据来自LPL赛事和玩加电竞，共计约32900条比赛记录。四大二分类指标均达到95%左右。
模型基于Pytorch构建，依据双方阵容选择来预测比赛胜率，通过注意力机制来提取关键信息，提高模型的准确性。

## 🛠 项目结构

```plaintext
.
│  app.py                     # Web应用入口
│  README.md                  # 项目说明文件
│  requirements.txt           # 项目依赖
│  venv                       # 虚拟环境
│  env.py                  # 环境配置
│
├─BILSTM_Att                  # 模型相关目录
│  │  BILSTM_Att.pt           # 训练好的模型文件
│  │  BILSTM_Att.py           # 模型定义与实现
│  │  predict.py              # 模型预测
│  │  predict——producer.py    # RockctMQ生产者
│  │  predict——consumer.py    # RockctMQ消费者
│  │  test.py                 # 模型测试
│  │  train.py                # 模型训练
│
├─crawling_data               # 数据爬取与处理
│  │  collecting_data.py      # 数据收集
│  │  concat_json.py          # JSON数据合并
│  │  process_data.py         # 数据预处理
│
├─data                        # 数据目录
│  ├─csv
│  │      lol_rank.csv        # 排名数据
│  │
│  └─json
│          example_data.json  # 示例数据
│          hero_info.json     # 英雄信息
│          hero_list.json     # 英雄列表
│          hero_win_rate.json # 英雄胜率
│          team_list.json     # 队伍列表
│
├─log                        # 日志文件夹
│      lol.log
│
├─static                     # 静态文件
│  │  lol.ico
│  │  lpl.ico
│  │
│  ├─css
│  │      style.css          # 页面样式
│  │      themes_base_jquery-ui.css
│  │
│  ├─images
│  │      avatar.png         # 头像
│  │      background.jpg     # 背景图片
│  │      leagueoflegends.webp # 英雄联盟图标
│  │
│  ├─js
│  │      beifen.js          # 前端脚本
│  │      echarts.min.js
│  │      fuse.min.js
│  │      jquery-3.6.0.min.js
│  │      main.js
│  │      ui_1.12.1_jquery-ui.js
│  │
│  └─saved_model
│          BILSTM_Att.pt
│
└─templates                  # 模板文件目录
        index.html           # 前端HTML页面
```

## 🕹 运行环境

确保安装以下依赖：
- 🌶Python 3.10.7+
- 🌽Flask
- 🥕PyTorch
- 🍅其他依赖请参考 `requirements.txt`

## 🧬 安装依赖（建议使用虚拟环境）

```bash
python -m venv venv  # 创建虚拟环境
venv/Scripts/activate  # 激活虚拟环境
```

```bash
pip install -r requirements.txt
```

## 🧲 数据收集与预处理

1. 🍓运行数据收集脚本：

    ```bash
    python collecting_data.py
    ```

2. 🍒运行数据合并脚本：

    ```bash
    python concat_json.py
    ```

3. 🍑运行数据预处理脚本：

    ```bash
    python process_data.py
    ```

## 🧩 训练模型

```bash
python train.py
```

## 🎐 进行预测

```bash
python predict.py
```

## 🎯 启动Web应用

```bash
python app.py
```

打开浏览器访问 `http://127.0.0.1:5000`，使用页面输入队伍信息并预测胜率。

## 🔑 详细文件说明

### `🍍BILSTM_Att.py`

实现了BiLSTM_Att模型和注意力机制，用于训练和预测。主要模块包括：
- 🍐模型架构定义
- 🍏前向传播
- 🍎损失函数和优化器配置
- 🥭引入注意力机制

### `🍌env.py`

设置了项目所需的环境变量和配置。

### `🍋predict.py`

加载训练好的模型，并对新数据进行预测。

### `🍊test.py`

用于模型测试的脚本。

### `🍉train.py`

包含了训练模型的完整流程，包括数据加载、模型训练和评估。

### `🍈collecting_data.py`

通过爬虫或API收集数据。

### `🍇concat_json.py`

将多个JSON文件合并为一个，以便进行统一的预处理和分析。

### `🥥process_data.py`

进行数据清洗和预处理，包括数据格式转换、归一化等操作。

### `🥝app.py`

使用Flask框架构建的Web应用程序入口，提供前端接口和后台逻辑。

### `🍰index.html`

前端HTML页面，用于用户交互，选择队伍和英雄进行胜率预测。

### `🍧beifen.js`

前端JavaScript代码，实现页面的动态功能，包括自动补全、图表绘制和预测结果展示。

### `🍜style.css`

前端CSS样式表，定义了页面的布局和样式。

## 🍚贡献

欢迎提出问题、建议和贡献代码。请通过GitHub issue进行讨论和提交PR。

## 🍖许可证

本项目采用MIT许可证，详情请参阅 LICENSE 文件。

---

🔋 如有任何问题，请联系项目作者。

`🥗E-mail: 2020311228@bipt.edu.cn`

`🍟WeChat: Viper373`

`🍔QQ: 2483523414`