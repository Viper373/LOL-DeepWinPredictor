# -*- coding:utf-8 -*-
# @Project        :LPL
# @FileName       :env.py
# @Time           :2025/3/5 04:13
# @Software       :PyCharm
# @Author         :Viper373
# @Index          :https://viper3.top
# @Blog           :https://blog.viper3.top

import os
import warnings
from dotenv import load_dotenv
from fake_useragent import UserAgent
import urllib3

# 禁用安全警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# 加载项目根目录中的环境变量文件
env_files = ['.env', '.env.local', '.env.example']
for env_file in env_files:
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), env_file), override=True)

# 请求头配置
UA = UserAgent().random
AUTHORIZATION = '7935be4c41d8760a28c05581a7b1f570'
GTK = "752018433"
PROXIES = None

# TiDB 配置（从环境变量中读取）
TIDB_CONFIG = {
    'host': os.getenv('TIDB_HOST'),
    'port': int(os.getenv('TIDB_PORT')),
    'user': os.getenv('TIDB_USER'),
    'password': os.getenv('TIDB_PASSWORD'),
    'charset': 'utf8mb4',
    'ssl_ca': os.path.join(os.path.dirname(os.path.abspath(__file__)), os.getenv('TIDB_CA_FILE')),
}

# LPL赛事
SEASONS = {
    "2025职业联赛": "218",
    "2024职业联赛": "206",
    "2023职业联赛": "190",
    "2022职业联赛": "167",
    "2021职业联赛": "148",
    "2020职业联赛": "134",
    "2019职业联赛": "115",
    "2024全球总决赛": "212",
    "2023全球总决赛": "201",
    "2022全球总决赛": "184",
    "2021全球总决赛": "156",
    "2020全球总决赛": "143",
    "2019全球总决赛": "128",
    "2018全球总决赛": "110",
    "2024季中冠军赛": "208",
    "2023季中冠军赛": "194",
    "2022季中冠军赛": "175",
    "2021季中冠军赛": "152",
    "2019季中冠军赛": "120",
    "2023德玛西亚杯": "204",
    "2022德玛西亚杯": "189",
    "2018德玛西亚杯": "132",
    "2023发展联赛": "192",
    "2022解说主持杯": "187",
    "2023亚洲挑战者之星邀请赛": "198"
}
