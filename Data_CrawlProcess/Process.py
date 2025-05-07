# -*- coding:utf-8 -*-
# @FileName: Process.py
# @Description: LOL数据处理通用方法（胜率、logo、hero_info、克制关系）

import os
from typing import Dict

import orjson

from Data_CrawlProcess import env
from tool_utils.log_utils import RichLogger
from tool_utils.mysql_utils import MySQLUtils

rich_logger = RichLogger()
mysql = MySQLUtils()

# 获取项目根目录
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, os.pardir))


class Process:
    def __init__(self, rich_progress=None):
        self.rich_progress = rich_progress
        self.hero_list_path = env.HERO_LIST
        self.hero_logo_path = env.HERO_LOGO
        self.hero_info_path = env.HERO_INFO
        self.hero_win_rate_path = env.HERO_WIN_RATE

    def concat_hero_info(self):
        count = 0
        try:
            with open(self.hero_list_path, 'rb') as f:
                hero_list = orjson.loads(f.read()).get('hero', [])
            with open(self.hero_logo_path, 'rb') as f:
                hero_logo = orjson.loads(f.read())
            hero_logo_dict = {str(hero.get('heroId')): hero.get('heroLogo') for hero in hero_logo}
            for hero in hero_list:
                hero_id = str(hero.get('heroId'))
                if hero_id in hero_logo_dict:
                    hero['heroLogo'] = hero_logo_dict[hero_id]
                    count += 1
            with open(self.hero_info_path, 'wb') as f:
                f.write(orjson.dumps(hero_list, option=orjson.OPT_INDENT_2))
            self.rich_progress.info(f"[Process] hero_info合并完成，共{count}条")
            return count
        except Exception as e:
            self.rich_progress.error(f"[Process] hero_info合并失败: {str(e)}")
            return 0

    def read_win_rate(self) -> Dict[str, float]:
        try:
            with open(self.hero_win_rate_path, "rb") as f:
                data = orjson.loads(f.read())['data']
            hero_win_rates = {}
            for d in data:
                heroId = d["champion_id"]
                playerLocation = d["positionName"][:3]
                winRate = d["positionWinRate"]
                hero_win_rates[f'{heroId}{playerLocation}'] = winRate
            rich_logger.info(f"[Process] 成功加载英雄胜率数据丨共[{len(hero_win_rates)}]条")
            return hero_win_rates
        except Exception as e:
            rich_logger.error(f"[Process] 读取英雄胜率数据失败: {str(e)}")
            return {}


