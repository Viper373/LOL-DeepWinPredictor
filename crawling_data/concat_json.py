# -*- coding:utf-8 -*-
# @Project        :LPL
# @FileName       :concat_json.py
# @Time           :2025/3/5 00:14
# @Software       :PyCharm
# @Author         :Viper373
# @Index          :https://viper3.top
# @Blog           :https://blog.viper3.top

import json
import logging

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

logging.info(f"hero_info.json 合并完成 丨 {hero_list.get('version')} 丨 {hero_list.get('fileTime')}")
