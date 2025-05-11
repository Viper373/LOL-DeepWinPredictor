---
title: LOL-DeepWinPredictor
emoji: 🎮
colorFrom: blue
colorTo: yellow
sdk: docker
sdk_version: "1.0"
app_file: api/app.py
pinned: false
---

# 🎮 基于深度学习的英雄联盟胜率预测

[![Python](https://img.shields.io/badge/Python-3.10.7+-blue.svg)](https://www.python.org/) [![PyTorch](https://img.shields.io/badge/PyTorch-2.3.0-red.svg)](https://pytorch.org/) [![Flask](https://img.shields.io/badge/Flask-3.0.3-green.svg)](https://flask.palletsprojects.com/)
![GitHub last commit](https://img.shields.io/github/last-commit/Viper373/LOL-DeepWinPredictor) ![Hugging Face Space Status](https://img.shields.io/badge/Space-Status-brightgreen) [![HuggingFace Spaces](https://img.shields.io/badge/Hugging%20Face-🤗-yellow?logo=huggingface)](https://huggingface.co/spaces/Viper373/LOL-DeepWinPredictor?badge=README) ![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/Viper373/LOL-DeepWinPredictor/total)

---

## 目录
- [项目简介](#项目简介)
- [主要功能](#主要功能)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [在线体验](#在线体验)
- [部署与使用](#部署与使用)
  - [使用已有模型（本地快速体验）](#使用已有模型本地快速体验)
  - [自行训练模型](#自行训练模型)
  - [云数据库注册](#云数据库注册)
  - [Hugging Face Spaces Docker 部署（推荐）](#hugging-face-spaces-docker-部署推荐)
  - [其他平台](#其他平台)
- [贡献指南](#贡献指南)
- [TODO](#todo)
- [常见问题](#常见问题)
- [联系方式](#联系方式)

---

## 项目简介

本项目为毕业设计，旨在通过深度学习技术预测英雄联盟（LOL）比赛的胜率，为玩家、教练和分析师提供数据支持。通过分析双方阵容选择，结合英雄特性和历史数据，模型能够给出较为准确的胜率预测。
> [!TIP]
> 
> 由于数据集和模型文件较大，完整的项目文档和部署指南已迁移至Hugging Face平台。请访问 [Hugging Face](https://huggingface.co/Viper373/LOL-DeepWinPredictor) 获取完整信息。
---

## 主要功能
- 阵容分析、胜率预测、可视化展示、英雄搜索、数据更新、异步处理、响应式设计
- 🌵**创新模型架构**：双向LSTM（BiLSTM_Att）+注意力机制
- 📊**大规模数据集**：5w+条职业比赛与表演赛数据
- 🎯**高精度预测**：准确率、精确率、召回率、F1分数均约95%
- 🖥️**用户友好界面**：Web界面，输入阵容即可预测

---

## 技术栈

**后端**：Python、PyTorch、Flask、RocketMQ、MySQL  
**前端**：HTML5、CSS3、JavaScript、jQuery UI、ECharts、Fuse.js

---

## 项目结构

```plaintext
.
├── api/                    # API服务
│   ├── app.py              # Flask主入口
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
│   └── BILSTM_Att.pt       # 训练好的模型权重
├── Data_CrawlProcess/      # 数据爬取与处理
├── data/                   # 数据文件
├── static/                 # 前端静态资源
├── templates/              # Jinja2模板
├── tool_utils/             # 工具类
├── logs/                   # 日志输出目录
└── ...
```

---

## 在线体验
✅[Huggingface Space 部署+CF反代](https://lol.viper3.us.kg/)

![在线演示界面](static/images/index_1.png)

---

## 部署与使用

### 使用已有模型（本地快速体验）

1. 克隆项目
   ```bash
   git clone https://github.com/Viper373/LOL-DeepWinPredictor.git
   cd LOL-DeepWinPredictor
   ```
2. 安装依赖（建议虚拟环境）
   ```bash
   python -m venv venv
   # Windows
   venv/Scripts/activate
   # Linux/Mac
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. 配置环境变量
   复制 `.env.example` 为 `.env.local`，填写变量值。
4. 启动 Web 服务
   ```bash
   python -m api.app
   # 访问 http://127.0.0.1:5000
   ```

### 自行训练模型

1. 克隆项目并安装依赖（同上）
2. 配置所有环境变量（详见 `.env.example`）
3. 采集全部数据
   ```bash
   python main.py
   ```
4. 训练模型
   - 调整 `BILSTM_Att/train.py` 中的模型参数，随后训练模型
   ```bash
   python BILSTM_Att/train.py
   ```
5. 模型部署
   - 训练完成后，将生成的模型文件重命名为 `BILSTM_Att.pt`，移动至 `static/saved_model/` 目录下。
6. 启动 Web 服务（同上）

### 云数据库注册

云端部署前需先注册云端免费数据库，获取环境变量所需值：

| 平台                                                                                                              | 数据库类型   | 注册地址                                                     | 注册教程                                |
|-----------------------------------------------------------------------------------------------------------------|---------|----------------------------------------------------------|-------------------------------------|
| ![SQLPub logo](https://sqlpub.com/logo.svg) SQLPub                                                              | MySQL   | https://sqlpub.com/                                      | https://www.appmiu.com/30458.html   |
| ![MongoDB Atlas logo](https://webassets.mongodb.com/_com_assets/cms/mongodb_logo1-76twgcu2dm.png) MongoDB Atlas | MongoDB | https://account.mongodb.com/account/login?signedOut=true | https://blog.aqcoder.cn/posts/b267/ |

### Hugging Face Spaces Docker 部署（推荐）

1. Duplicate this Space
2. 配置环境变量
   复制 `.env.example` 为 `.env.local`，填写变量值。
3. 等待构建完成，访问 Space 即可体验

### 其他平台

本项目已适配主流云平台，支持一键部署：

| 平台                 | 部署                                                                                                                                                                                                                                                       | 状态 |
|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----|
| Vercel             | [一键部署](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FViper373%2FLOL-DeepWinPredictor&env=MYSQL_HOST,MYSQL_PORT,MYSQL_USER,MYSQL_PASSWORD,MYSQL_DATABASE&project-name=lol-deepwinpredictor&repository-name=LOL-DeepWinPredictor) | ❌  |
| Netlify            | [一键部署](https://app.netlify.com/start/deploy?repository=https://github.com/Viper373/LOL-DeepWinPredictor)                                                                                                                                                 | ❌  |
| HuggingFace Spaces | [体验](https://huggingface.co/spaces/Viper373/LOL-DeepWinPredictor)                                                                                                                                                                                        | ✅  |
| Koyeb              | [一键部署](https://app.koyeb.com/deploy?type=git&repository=github.com/Viper373/LOL-DeepWinPredictor)                                                                                                                                                        | ✅  |

### GitHub 仓库环境变量设置

在 GitHub Actions 或云端部署时，需要在仓库的 Settings → Secrets and variables → Actions 中添加以下环境变量（参考 `.env.example` 文件）：

| 变量名           | 说明             | 是否必填 |
|----------------|----------------|--------|
| MYSQL_HOST     | MySQL主机地址    | 必填   |
| MYSQL_PORT     | MySQL端口        | 必填   |
| MYSQL_USER     | MySQL用户名      | 必填   |
| MYSQL_PASSWORD | MySQL密码        | 必填   |
| MYSQL_CHARSET  | MySQL字符集      | 必填   |
| MYSQL_DATABASE | MySQL数据库名    | 必填   |
| MONGO_URI      | MongoDB连接URI   | 必填   |
| PROXY          | 代理配置（JSON字符串，例：{'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}） | 可选   |
| GH_TOKEN   | GitHub访问令牌（用于自动发布Release） | 必填   |

> ⚠️ 代理配置（PROXY）为可选项，若部署环境无法直接访问外网或有特殊网络需求时可设置。

---

### GitHub Actions 自动化数据集更新

本项目已集成 GitHub Actions 工作流（见 `.github/workflows/main.yml`），支持：
- **定时自动运行**：每周日 0点自动拉取和更新数据集。
- **手动触发**：可在 GitHub Actions 页面点击手动运行。

只需在仓库设置好环境变量，GitHub Actions 会自动完成数据采集与更新，无需手动操作服务器。

---

## 贡献指南

1. 提交问题：使用GitHub Issues报告bug或建议
2. 提交代码：Fork仓库，创建分支，提交PR
3. 代码规范：遵循PEP8，添加注释和文档，确保测试通过

---

## TODO

- [ ] 调整参数，添加Counter数据重新训练（当前模型部分过拟合）
- [ ] Next.js前端重构
- [ ] 英雄数据展示（BAN、PICK、WinRate）
- [ ] 战队数据展示
- [ ] 选手数据展示
- [ ] LPL未来 / 历史比赛展示
- [ ] 前端结果导出

---

## 常见问题

- **Q: 云端部署时模型文件如何处理？**
  - A: 云端（如 Hugging Face）无法训练模型，需在本地训练好后，重命名为 `BILSTM_Att.pt` 上传到 `static/saved_model/` 目录。
- **Q: 其他平台（如 Vercel、Netlify）能否用？**
  - A: 理论支持，但受限于依赖体积和运行环境，推荐 Hugging Face Spaces Docker 部署。
- **Q: 数据库如何配置？**
  - A: 参考 `.env.example`，可用 SQLPub、MongoDB Atlas 等云数据库。

---

## 联系方式

如有任何问题，请联系项目作者（打上备注：LOL-DeepWinPredictor）。

- 🥗E-mail: 2483523414@qq.com
- 🍟WeChat: Viper373
- 🍔QQ: 2483523414t r i g g e r   r e l e a s e - p l e a s e  
 t e s t   r e l e a s e - p l e a s e  
 