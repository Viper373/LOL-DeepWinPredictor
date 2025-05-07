---
license: mit
language:
  - zh
base_model:
  - Viper373/LOL-DeepWinPredictor
---

[![Python](https://img.shields.io/badge/Python-3.10.7+-blue.svg)](https://www.python.org/) [![PyTorch](https://img.shields.io/badge/PyTorch-2.3.0-red.svg)](https://pytorch.org/) [![Flask](https://img.shields.io/badge/Flask-3.0.3-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Vercel部署状态](https://therealsujitk-vercel-badge.vercel.app/?app=lol-deepwinpredictor&style=flat)](https://lol.viper3.top/predict)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-🤗-yellow?logo=huggingface)](https://huggingface.co/Viper373/LOL-DeepWinPredictor)
[![HuggingFace Spaces](https://img.shields.io/badge/Spaces-README-blue?logo=huggingface)](https://huggingface.co/spaces/Viper373/LOL-DeepWinPredictor?badge=README)
[![GitHub Clones](https://img.shields.io/badge/dynamic/json?color=success&label=Clones&query=count&url=https://api.github.com/repos/Viper373/LOL-DeepWinPredictor/traffic/clones)](https://github.com/Viper373/LOL-DeepWinPredictor)
[![GitHub All Releases](https://img.shields.io/github/downloads/Viper373/LOL-DeepWinPredictor/total.svg)](https://github.com/Viper373/LOL-DeepWinPredictor/releases)

# 🎮 基于深度学习的英雄联盟胜率预测

## 📚 项目简介

### 🎓 学术背景
- 🌴项目为本人毕业设计
- 🌱论文题目为《基于深度学习的英雄联盟胜率预测研究》
- 🌲毕业院校：北京石油化工学院（BIPT） 
- 🌳院系：经济管理学院 
- 🌾专业：大数据管理与应用 
- 🌿年级：20级

### 🔍 项目概述
本项目旨在通过深度学习技术预测英雄联盟（LOL）比赛的胜率，为玩家、教练和分析师提供数据支持。通过分析双方阵容选择，结合英雄特性和历史数据，模型能够给出较为准确的胜率预测。

> **📢 重要提示**：由于数据集和模型文件较大，完整的项目文档和部署指南已迁移至Hugging Face平台。请访问 [![Hugging Face](https://img.shields.io/badge/Hugging%20Face-🤗-yellow)](https://huggingface.co/Viper373/LOL-DeepWinPredictor) 获取完整信息。

### 💡 核心特点
- 🌵**创新模型架构**：采用双向LSTM（BiLSTM_Att）结合注意力机制，能够有效捕捉英雄间的协同与克制关系
- 📊**大规模数据集**：数据来自LPL赛事和玩加电竞，共计5w+条比赛记录，覆盖多个赛季职业比赛与表演赛数据
- 🎯**高精度预测**：四大二分类指标（准确率、精确率、召回率、F1分数）均达到95%左右
- 🖥️**用户友好界面**：提供直观的Web界面，用户可以轻松输入阵容信息并获取预测结果


### 🛠️ 技术栈

#### 后端技术
- **核心语言**：Python
- **深度学习框架**：PyTorch
- **Web框架**：Flask
- **消息队列**：RocketMQ
- **数据库**：MySQL

#### 前端技术
- **基础技术**：HTML5, CSS3, JavaScript
- **UI框架**：jQuery UI
- **数据可视化**：ECharts
- **搜索功能**：Fuse.js

## 📂 项目结构

```plaintext
.
├── api/                    # 适配Vercel的API服务
│   ├── app.py              # Web应用主入口，Flask服务
├── main.py                 # 数据全流程自动化主入口
├── requirements.txt        # 依赖包列表
├── vercel.json             # Vercel部署配置
├── README.md               # 项目说明文件
├── .env.example            # 环境变量示例
├── .env.local              # 本地环境变量
├── BILSTM_Att/             # 深度学习模型与推理相关
│   ├── BILSTM_Att.py       # BiLSTM_Att模型结构
│   ├── train.py            # 模型训练脚本
│   ├── predict.py          # 单次预测脚本
│   ├── test.py             # 模型测试脚本
│   ├── predict_producer.py # RocketMQ生产者
│   ├── predict_consumer.py # RocketMQ消费者
│   ├── test_producer.py    # RocketMQ生产者
│   ├── test_consumer.py    # RocketMQ消费者
│   └── BILSTM_Att.pt       # 训练好的模型权重
├── Data_CrawlProcess/      # 数据爬取与处理
│   ├── env.py              # 环境与路径配置
│   ├── LPL.py              # LPL赛事数据爬虫
│   ├── Wanplus.py          # 玩加电竞数据爬虫
│   ├── Other.py            # 其他数据爬虫
│   ├── Concat.py           # 数据合并
│   └── Process.py          # 数据预处理
├── data/                   # 数据文件
│   ├── json/               # JSON数据（英雄、队伍、胜率等）
│   └── deprecated/         # 历史/弃用数据
├── static/                 # 前端静态资源
│   ├── css/                # 样式文件
│   ├── js/                 # 前端脚本
│   ├── images/             # 图片资源
│   ├── saved_model/        # 前端用模型文件
│   └── *.ico               # 网站图标
├── templates/              # Jinja2模板（index.html等）
├── tool_utils/             # 工具类（数据库、日志、进度条等）
├── logs/                   # 日志输出目录
└── ...
```

## 🚀 在线体验
- [https://lol.viper3.top/](https://lol.viper3.top/)

- 在线演示界面截图：
![在线演示界面](static/images/index_1.png)

## ⚙️ 私有部署（⭐需先fork仓库进行环境变量的配置）

本项目支持多种私有化部署方式，分为“使用已有模型”和“自行训练模型”两种典型流程。

### 1. 使用已有模型（推荐，最快速体验）
 - ⭐觉得项目不错的可以点一个Star微薄支持一下谢谢

1. **克隆项目**
   ```bash
   git clone https://github.com/Viper373/LOL-DeepWinPredictor.git
   cd LOL-DeepWinPredictor
   ```
2. **安装依赖（建议虚拟环境）**
   - 先取消requirements.txt中的`torch==2.3.0+cu121`注释（该注释是为了避免云端部署依赖安装的错误）

   ```bash
   python -m venv venv
   # Windows
   venv/Scripts/activate
   # Linux/Mac
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **配置环境变量**
   复制 `.env.example` 为 `.env.local`，填写变量值：
   ```env
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_USER=root
   MYSQL_PASSWORD=your_password
   MYSQL_DATABASE=your_database
   
   MONGO_URI=mongodb://localhost:27017/
   
   PROXY="{'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}"
   ```
4. **采集数据（只需采集Other数据）**
   - 打开 `main.py`，注释掉除Other以外的所有执行流程，仅保留Other相关部分。
   - 执行：
     ```bash
     python main.py
     ```
5. **启动Web服务**
   ```bash
   python app.py
   # 访问 http://127.0.0.1:5000
   ```

### 2. 自行训练模型

1. **克隆项目并安装依赖**（同上）

2. **配置所有环境变量**（详见 `.env.example`）

3. **采集全部数据**
   - 直接执行：
     ```bash
     python main.py
     ```

4. **训练模型**
   - 调整BILSTM_Att/train.py中的模型参数，随后训练模型
   ```bash
   python BILSTM_Att/train.py
   ```

5. **模型部署**
   - 训练完成后，将生成的模型文件重命名为 `BILSTM_Att.pt`，移动至 `static/saved_model/` 目录下。

6. **启动Web服务**（同上）

### 3. 云端部署

**注意事项：**

- 云端部署（Vercel、Netlify、HuggingFace、Koyeb等）**无法在云端训练模型**，只能使用已有模型权重`static/saved_model/BILSTM_Att.pt`，或需自行在本地训练好模型后上传到对应目录再进行云端部署。
- ✅推荐先 Fork 本仓库到自己的 GitHub 账号，再进行一键部署，这样可以自定义和管理自己的部署实例。
- 若需更换模型，需在本地训练好后上传到你的仓库的 `static/saved_model/` 目录。

🔺云端部署前需先注册云端免费数据库，获取环境变量所需值

| 平台                                                                                                              | 数据库类型   | 注册地址                                                     | 注册教程                                |
|-----------------------------------------------------------------------------------------------------------------|---------|----------------------------------------------------------|-------------------------------------|
| ![SQLPub logo](https://sqlpub.com/logo.svg) SQLPub                                                              | MySQL   | https://sqlpub.com/                                      | https://www.appmiu.com/30458.html   |
| ![MongoDB Atlas logo](https://webassets.mongodb.com/_com_assets/cms/mongodb_logo1-76twgcu2dm.png) MongoDB Atlas | MongoDB | https://account.mongodb.com/account/login?signedOut=true | https://blog.aqcoder.cn/posts/b267/ |



本项目已适配主流云平台，支持一键部署：

<table>
  <thead>
    <tr>
      <th style="text-align:center;vertical-align:middle;">平台</th>
      <th style="text-align:center;vertical-align:middle;">部署</th>
      <th style="text-align:center;vertical-align:middle;">状态</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center" valign="middle"><b>Vercel</b></td>
      <td align="center" valign="middle">
        <a href="https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FViper373%2FLOL-DeepWinPredictor&env=MYSQL_HOST,MYSQL_PORT,MYSQL_USER,MYSQL_PASSWORD,MYSQL_DATABASE&project-name=lol-deepwinpredictor&repository-name=LOL-DeepWinPredictor">
          <img src="https://vercel.com/button" alt="Deploy with Vercel" height="32" style="display:block;margin:auto;"/>
        </a>
      </td>
      <td align="center" valign="middle">✅</td>
    </tr>
    <tr>
      <td align="center" valign="middle"><b>Netlify</b></td>
      <td align="center" valign="middle">
        <a href="https://app.netlify.com/start/deploy?repository=https://github.com/Viper373/LOL-DeepWinPredictor">
          <img src="https://www.netlify.com/img/deploy/button.svg" alt="Deploy to Netlify" height="32" style="display:block;margin:auto;"/>
        </a>
      </td>
      <td align="center" valign="middle">✅</td>
    </tr>
    <tr>
      <td align="center" valign="middle"><b>HuggingFace Spaces</b></td>
      <td align="center" valign="middle">
        <a href="https://huggingface.co/spaces/Viper373/LOL-DeepWinPredictor">
          <img src="https://huggingface.co/datasets/huggingface/badges/raw/main/open-in-hf-spaces-sm-dark.svg" alt="Open in Spaces" height="26" style="display:block;margin:auto;"/>
        </a>
      </td>
      <td align="center" valign="middle">✅</td>
    </tr>
    <tr>
      <td align="center" valign="middle"><b>Koyeb</b></td>
      <td align="center" valign="middle">
        <a href="https://app.koyeb.com/deploy?type=git&repository=github.com/Viper373/LOL-DeepWinPredictor">
          <img src="https://www.koyeb.com/static/images/deploy/button.svg" alt="Deploy on Koyeb" height="40" style="display:block;margin:auto;"/>
        </a>
      </td>
      <td align="center" valign="middle">⛔</td>
    </tr>
  </tbody>
</table>


## 🧩 主要功能
- 阵容分析、胜率预测、可视化展示、英雄搜索、数据更新、异步处理、响应式设计等

## 🧬 贡献指南（欢迎贡献本项目）

1. **提交问题**：使用GitHub Issues报告bug或建议
2. **提交代码**：Fork仓库，创建分支，提交PR
3. **代码规范**：遵循PEP8，添加注释和文档，确保测试通过

## 🗂️ TODO

- [ ] 调整参数，添加Counter数据重新训练（当前模型部分过拟合）
- [ ] Next.js前端重构
- [ ] 英雄数据展示（BAN、PICK、WinRate）
- [ ] 战队数据展示
- [ ] 选手数据展示
- [ ] LPL未来 / 历史比赛展示
- [ ] 前端结果导出
- [ ] Docker镜像与CI/CD自动化

---

🔋 如有任何问题，请联系项目作者（打上备注：LOL-DeepWinPredictor）。

`🥗E-mail: 2483523414@qq.com`

`🍟WeChat: Viper373`

`🍔QQ: 2483523414`