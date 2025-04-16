# -*- coding:utf-8 -*-
# @Project        :LPL
# @FileName       :env.py
# @Time           :2025/3/5 04:13
# @Software       :PyCharm
# @Author         :Viper373
# @Index          :https://viper3.top
# @Blog           :https://blog.viper3.top

from fake_useragent import UserAgent

# 请求头配置
# 随机User-Agent
UA = UserAgent().random
# 身份验证
AUTHORIZATION = '7935be4c41d8760a28c05581a7b1f570'
GTK = "752018433"
# 代理
# PROXIES = {
#     'http': '127.0.0.1:7890',
#     'https': '127.0.0.1:7890'
# }
PROXIES = None

# MongoDB配置
# 从.env.local加载
import os
from dotenv import load_dotenv

# 加载.env.local文件中的环境变量
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env.local')
load_dotenv(env_path)

# 主机
# MONGO_URL = os.getenv('MONGO_URL')
MONGO_URL = "mongodb+srv://Viper3:ShadowZed666@pythonproject.1rxku.mongodb.net/?retryWrites=true&w=majority&appName=PythonProject"

# LPL赛事
SEASONS = {
    # 赛季名称: 赛季ID
    # 职业联赛
    "2024职业联赛": "206",
    "2023职业联赛": "190",
    "2022职业联赛": "167",
    "2021职业联赛": "148",
    "2020职业联赛": "134",
    "2019职业联赛": "115",
    # 全球总决赛
    "2023全球总决赛": "201",
    "2022全球总决赛": "184",
    "2021全球总决赛": "156",
    "2020全球总决赛": "143",
    "2019全球总决赛": "128",
    "2018全球总决赛": "110",
    # 季中冠军赛
    "2024季中冠军赛": "208",
    "2023季中冠军赛": "194",
    "2022季中冠军赛": "175",
    "2021季中冠军赛": "152",
    "2019季中冠军赛": "120",
    # 德玛西亚杯
    "2023德玛西亚杯": "204",
    "2022德玛西亚杯": "189",
    "2018德玛西亚杯": "132",
    # 发展联赛
    "2023发展联赛": "192",
    # 其他赛事
    "2022解说主持杯": "187",
    # 亚洲挑战者之星邀请赛
    "2023亚洲挑战者之星邀请赛": "198"
}
