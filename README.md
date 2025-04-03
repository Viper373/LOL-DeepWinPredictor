
# 🎮 基于深度学习的英雄联盟胜率预测

[![Python](https://img.shields.io/badge/Python-3.10.7+-blue.svg)](https://www.python.org/) [![PyTorch](https://img.shields.io/badge/PyTorch-2.3.0-red.svg)](https://pytorch.org/) [![Flask](https://img.shields.io/badge/Flask-3.0.3-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Vercel部署状态](https://therealsujitk-vercel-badge.vercel.app/?app=lol-deepwinpredictor&style=flat)](https://lol.viper3.top/predict)

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

### 💡 核心特点
- 🌵**创新模型架构**：采用双向LSTM（BiLSTM_Att）结合注意力机制，能够有效捕捉英雄间的协同与克制关系
- 📊**大规模数据集**：数据来自LPL赛事和玩加电竞，共计约32900条比赛记录，覆盖多个赛季的职业比赛
- 🎯**高精度预测**：四大二分类指标（准确率、精确率、召回率、F1分数）均达到95%左右
- 🖥️**用户友好界面**：提供直观的Web界面，用户可以轻松输入阵容信息并获取预测结果
- ☁️**云端部署**：支持Vercel一键部署，便于分享和使用

### 🛠️ 技术栈

#### 后端技术
- **核心语言**：Python 3.10.7+
- **深度学习框架**：PyTorch 2.3.0
- **Web框架**：Flask 3.0.3
- **消息队列**：RocketMQ（用于异步处理预测请求）
- **数据库**：MongoDB（存储模型结果和用户数据）

#### 前端技术
- **基础技术**：HTML5, CSS3, JavaScript
- **UI框架**：jQuery UI
- **数据可视化**：ECharts
- **搜索功能**：Fuse.js（用于英雄搜索）

#### 部署环境
- **云平台**：Vercel
- **容器化**：支持Docker部署
- **版本控制**：Git

## 🚙 在线体验
- 🚀https://lol.viper3.top/

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
│  │  test——producer.py       # RockctMQ生产者
│  │  test——consumer.py       # RockctMQ消费者
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

## 🔑 主要功能

- **阵容分析**：分析双方阵容的优劣势，考虑英雄间的协同与克制关系
- **胜率预测**：基于历史数据和深度学习模型，预测比赛胜率
- **可视化展示**：直观展示预测结果和关键影响因素
- **英雄搜索**：支持模糊搜索，快速找到所需英雄
- **数据更新**：定期更新英雄数据和胜率统计
- **异步处理**：使用消息队列处理大量预测请求
- **响应式设计**：适配不同设备的屏幕尺寸

## 🚀 Vercel部署指南

可点击下方按钮立即部署：

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FViper373%2FLOL-DeepWinPredictor&env=MONGO_URL&project-name=lol-deepwinpredictor&repository-name=LOL-DeepWinPredictor)

本项目已配置为可在Vercel上部署。按照以下步骤操作：

1. **准备工作**
   - 确保你的项目已经推送到GitHub仓库
   - 准备好MongoDB数据库（可使用MongoDB Atlas免费层）

2. **Vercel账户设置**
   - 注册/登录[Vercel](https://vercel.com)
   - 可以使用GitHub账户直接登录

3. **导入项目**
   - 点击"New Project"
   - 从GitHub导入你的仓库
   - 选择包含本项目的仓库

4. **配置项目**
   - 框架预设：选择"Other"（因为我们使用了自定义的vercel.json）
   - 构建命令：不需要修改，使用vercel.json中的配置
   - 输出目录：不需要修改，使用vercel.json中的配置
   - 安装命令：`pip install -r requirements.txt`

5. **环境变量设置**
   - 在项目设置中找到"Environment Variables"
   - 添加以下环境变量：

   | 变量名         | 描述                 | 示例值                                                                                      | 是否必填 |
   |-------------|--------------------|------------------------------------------------------------------------------------------|------|
   | `MONGO_URL` | MongoDB数据库连接字符串    | mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority | ✅    |
   | `API_KEY`   | 外部API服务的访问密钥（如果使用） | sk_test_abcdefghijklmnopqrstuvwxyz                                                       | ❌    |

6. **部署**
   - 点击"Deploy"按钮开始部署
   - 等待部署完成
   - 部署成功后，Vercel会提供一个默认域名（例如：your-project.vercel.app）

7. **自定义域名（可选）**
   - 在项目设置中找到"Domains"
   - 添加你的自定义域名
   - 按照Vercel提供的说明配置DNS记录

8. **持续部署**
   - Vercel会自动监控你的GitHub仓库
   - 每次推送到主分支时，Vercel会自动重新部署

## 🍚 贡献指南

欢迎为本项目做出贡献！以下是参与方式：

1. **提交问题**
   - 使用GitHub Issues报告bug或提出新功能建议
   - 清晰描述问题或建议，并提供相关信息

2. **提交代码**
   - Fork本仓库
   - 创建新分支：`git checkout -b feature/your-feature-name`
   - 提交更改：`git commit -m 'Add some feature'`
   - 推送到分支：`git push origin feature/your-feature-name`
   - 提交Pull Request

3. **代码规范**
   - 遵循PEP 8 Python编码规范
   - 添加适当的注释和文档
   - 确保代码通过现有测试

## 🍖 许可证

本项目采用MIT许可证，详情请参阅 LICENSE 文件。

---

🔋 如有任何问题，请联系项目作者。

`🥗E-mail: 2020311228@bipt.edu.cn`

`🍟WeChat: Viper373`

`🍔QQ: 2483523414`
