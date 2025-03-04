# -*- coding:utf-8 -*-
# @Project        :LPL
# @FileName       :concat_json.py
# @Time           :2025/3/5 00:14
# @Software       :PyCharm
# @Author         :Viper373
# @Index          :https://viper3.top
# @Blog           :https://blog.viper3.top

import os
import json
import logging  # 日志
from rich.logging import RichHandler
# 获取当前脚本的目录
script_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目的根目录（假设你的项目根目录在上两级）
project_root = os.path.abspath(os.path.join(script_dir, os.pardir))

logging.basicConfig(
    level="INFO",
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    datefmt="[%Y-%m-%d %H:%M:%S]",
    handlers=[
        # 日志控制台处理器
        RichHandler(rich_tracebacks=True),
        # 日志文件处理器
        logging.FileHandler(os.path.join(project_root, 'logs', 'lol.logs'), mode='a', encoding='utf-8'),
    ],
)

log = logging.getLogger("rich")  # 日志对象
# 读取hero_list.json文件
with open('../data/json/hero_list.json', 'r', encoding='utf-8') as f:
    hero_list = json.load(f)

# 读取hero_logo.json文件
with open('../data/json/hero_logo.json', 'r', encoding='utf-8') as f:
    hero_logo = json.load(f)

# 创建一个heroId到heroLogo的映射
hero_logo_dict = {str(hero['heroId']): hero['heroLogo'] for hero in hero_logo}

# 更新hero_list.json中的数据，添加heroLogo字段
for hero in hero_list.get('hero'):
    hero_id = hero['heroId']
    if hero_id in hero_logo_dict:
        hero['heroLogo'] = hero_logo_dict[hero_id]

# 将更新后的数据写入新的JSON文件hero.json
with open('../data/json/hero_info.json', 'w', encoding='utf-8') as f:
    json.dump(hero_list, f, ensure_ascii=False, indent=4)

log.info(f"hero_info.json 合并完成 丨 {hero_list.get('version')} 丨 {hero_list.get('fileTime')}")
