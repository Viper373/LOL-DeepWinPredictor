# -*- coding:utf-8 -*-
# @Software       :PyCharm
# @Project        :LOL-DeepWinPredictor
# @Path           :/Data_CrawlProcess
# @FileName       :Other.py
# @Time           :2025/4/27 22:59
# @Author         :Viper373
# @GitHub         :https://github.com/Viper373
# @Home           :https://viper3.top
# @Blog           :https://blog.viper3.top

import re
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

import orjson
import requests

from Data_CrawlProcess import env
from tool_utils.log_utils import RichLogger
from tool_utils.mysql_utils import MySQLUtils
from tool_utils.progress_utils import RichProgressUtils

rich_logger = RichLogger()
mysql_utils = MySQLUtils()


class Other:

    def __init__(self, rich_progress: Optional[RichProgressUtils] = None):
        self.rich_progress = rich_progress or RichProgressUtils()
        self.hero_list_url = (
            "https://game.gtimg.cn/images/lol/act/img/js/heroList/hero_list.js"
        )
        self.logo_url_template = "https://game.gtimg.cn/images/lol/act/img/champion/{}.png"  # 官方Logo URL模板
        self.hero_win_rate_url = "https://op.gg/zh-cn/lol/champions"
        self.team_list_url = (
            "https://open.tjstats.com/match-auth-app/open/v1/compound/public/team"
        )
        self.hero_list_path = env.HERO_LIST
        self.hero_logo_path = env.HERO_LOGO
        self.hero_info_path = env.HERO_INFO
        self.hero_win_rate_path = env.HERO_WIN_RATE
        self.team_list_path = env.TEAM_LIST
        self.cookies = {
            "_ol": "zh_CN",
            "_olvt": "false",
            "_opvc": "7",
        }
        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "priority": "u=0, i",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1 Edg/135.0.0.0",
        }
        self.team_list_headers = {
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,ja;q=0.5,ko;q=0.4,fr;q=0.3",
            "authorization": "7935be4c41d8760a28c05581a7b1f570",
            "cache-control": "no-cache",
            "origin": "https://lpl.qq.com",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": "https://lpl.qq.com/",
            "sec-ch-ua": '"Microsoft Edge";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0",
        }
        self.params = {
            "tier": "all",
        }
        self.team_list_params = {
            "seasonId": None,
            "stageIds": None,
        }

    def get_hero_list(self) -> None:
        """
        获取英雄列表并保存为格式化的JSON文件，并写入MySQL（分路胜率表）。
        :return: None
        """
        try:
            task_id = self.rich_progress.add_task("[Other] 获取hero_list", total=1)
            response = requests.get(self.hero_list_url)
            if response.status_code != 200:
                rich_logger.error(
                    f"[Other] 请求hero_list失败，状态码: {response.status_code}"
                )
                return
            try:
                hero_data = response.json()
            except orjson.JSONDecodeError:
                rich_logger.error("[Other] hero_list 响应内容不是有效的 JSON 格式")
                return
            with open(self.hero_list_path, "wb") as f:
                f.write(orjson.dumps(hero_data, option=env.ORJSON_OPTS))
            rich_logger.info(
                f"[Other] {hero_data.get('fileName')}保存完成 丨 version：{hero_data.get('version')} 丨 {hero_data.get('fileTime')}"
            )
            self.rich_progress.advance(task_id)
        except Exception as _error:
            rich_logger.error(f"[Other] 获取hero_list失败: {_error}")

    def append_hero_id(self) -> None:
        """
        将英雄列表中的英雄ID添加到胜率数据中
        :return: None
        """
        try:
            task_id = self.rich_progress.add_task("[Other] append_hero_id", total=1)
            hero_win_rate = orjson.loads(open(self.hero_win_rate_path, "rb").read())
            hero_list = orjson.loads(open(self.hero_list_path, "rb").read())
            # 用alias（英文名，小写）做映射
            alias_to_id = {
                hero["alias"].lower(): hero["heroId"]
                for hero in hero_list.get("hero", [])
                if "alias" in hero and "heroId" in hero
            }
            for hero in hero_win_rate.get("data", []):
                key = hero.get("key", "").lower()
                if key in alias_to_id:
                    hero["champion_id"] = alias_to_id[key]
            with open(self.hero_win_rate_path, "wb") as f:
                f.write(orjson.dumps(hero_win_rate, option=orjson.OPT_INDENT_2))
            rich_logger.info(f"[Other] append_hero_id完成")
            self.rich_progress.advance(task_id)
        except Exception as e:
            rich_logger.error(f"[Other] append_hero_id失败: {e}")

    def get_hero_win_rate(self) -> None:
        """
        获取英雄胜率数据并保存为格式化的JSON文件，并写入MySQL（分路胜率表，每个英雄一条，分路缺失补0.5）。
        :return: None
        """
        try:
            task_id = self.rich_progress.add_task("[Other] 获取hero_win_rate", total=1)
            max_retries = 3
            retry_count = 0
            while retry_count < max_retries:
                try:
                    response = requests.get(
                        url=self.hero_win_rate_url,
                        params=self.params,
                        cookies=self.cookies,
                        headers=self.headers,
                    )
                    if response.status_code != 200:
                        rich_logger.warning(
                            f"请求失败，状态码: {response.status_code}，尝试重试"
                        )
                        retry_count += 1
                        continue

                    scripts = re.findall(
                        r"<script\b[^>]*>([\s\S]*?)<\/script>",
                        response.text,
                        re.IGNORECASE,
                    )
                    target_index = None
                    for index, content in enumerate(scripts, start=1):
                        if "positionWinRate" in content:
                            target_index = index
                            break
                    target_script = scripts[target_index - 1]
                    pattern = r"(\{.*\})"
                    match = re.search(pattern, target_script, re.DOTALL)
                    if not match:
                        rich_logger.warning("目标script中未匹配到JSON数据")
                        continue

                    json_str = match.group(1)
                    json_str = json_str.replace('\\"', '"').replace("\\\\", "\\")
                    try:
                        hero_data = orjson.loads(json_str.encode("utf-8"))
                        save_path = self.hero_win_rate_path
                        with open(save_path, "wb") as f:
                            f.write(
                                orjson.dumps(
                                    hero_data,
                                    option=orjson.OPT_INDENT_2
                                           | orjson.OPT_APPEND_NEWLINE,
                                )
                            )
                        rich_logger.info(f"[Other] hero_win_rate保存完成")
                        if task_id is not None:
                            self.rich_progress.advance(task_id)
                        return
                    except Exception as e:
                        rich_logger.error(f"[Other] JSON解析失败: {e}，尝试重试")
                        retry_count += 1
                        continue
                except Exception as _error:
                    rich_logger.error(
                        f"[Other] 获取hero_win_rate失败: {_error}，尝试重试"
                    )
                    retry_count += 1
                    continue
            rich_logger.error(f"[Other] 获取hero_win_rate失败：已重试 {max_retries} 次")
        except Exception as e:
            rich_logger.error(f"[Other] 获取hero_win_rate主流程异常: {e}")

    def write_hero_win_rate_to_mysql(self) -> None:
        """
        读取env.HERO_WIN_RATE路径的json数据，聚合后写入MySQL，每个英雄一条，分路缺失补0.5。
        :return: None
        """
        with open(self.hero_win_rate_path, "rb") as f:
            hero_data = orjson.loads(f.read())
        winrate_list = hero_data.get("data", [])
        hero_dict = {}
        # 分路名映射，兼容多种写法
        pos_map = {
            "TOP": "TOP",
            "JUN": "JUN", "JUNGLE": "JUN",
            "MID": "MID",
            "ADC": "ADC", "BOTTOM": "ADC",
            "SUP": "SUP", "SUPPORT": "SUP"
        }
        for hero in winrate_list:
            hero_id = int(hero.get("champion_id", 0))
            hero_name = hero.get("name", "")
            pos_raw = hero.get("positionName", "").upper()
            pos = pos_map.get(pos_raw)
            win_rate = hero.get("positionWinRate", 0.5)
            if hero_id == 0:
                continue
            if hero_id not in hero_dict:
                hero_dict[hero_id] = {
                    "hero_id": hero_id,
                    "hero_name": hero_name,
                    "TOP": 0.5,
                    "JUN": 0.5,
                    "MID": 0.5,
                    "ADC": 0.5,
                    "SUP": 0.5,
                }
            if pos:
                try:
                    hero_dict[hero_id][pos] = float(win_rate / 100)
                except Exception:
                    hero_dict[hero_id][pos] = 0.5
        insert_data = []
        for hero in hero_dict.values():
            insert_data.append(
                (
                    hero["hero_id"],
                    hero["hero_name"],
                    hero["TOP"],
                    hero["JUN"],
                    hero["MID"],
                    hero["ADC"],
                    hero["SUP"],
                )
            )
        mysql_task_id = self.rich_progress.add_task("[Other] hero_win_rate写入MySQL", total=len(insert_data))
        mysql_utils.insert_hero_win_rate(insert_data)
        for _ in range(len(insert_data)):
            self.rich_progress.advance(mysql_task_id)
        rich_logger.info(f"[Other] hero_win_rate已写入MySQL，共{len(insert_data)}条")

    def append_counter(self, json_path: str) -> None:
        """
        为MySQL hero_win_rate表中的每个英雄添加克制关系字段（counter，分路分组，字段为{"TOP": [...], "JUN": [...]}，多线程加速写入）。
        :param json_path: json文件路径
        :return: None
        """
        json_data = orjson.loads(open(json_path, "rb").read())
        # 分路名映射，兼容多种写法
        pos_map = {
            "TOP": "TOP",
            "JUN": "JUN", "JUNGLE": "JUN",
            "MID": "MID",
            "ADC": "ADC", "BOTTOM": "ADC",
            "SUP": "SUP", "SUPPORT": "SUP"
        }
        hero_counter_map = {}
        for hero in json_data.get("data", []):
            hero_id = int(hero.get("champion_id")) if "champion_id" in hero else None
            if hero_id is not None:
                if hero_id not in hero_counter_map:
                    hero_counter_map[hero_id] = {}
                pos_counters = hero_counter_map[hero_id]
                # 顶层分路
                if "positionCounters" in hero and isinstance(hero["positionCounters"], list):
                    pos_raw = hero.get("positionName", "").upper()
                    pos = pos_map.get(pos_raw)
                    if pos:
                        pos_counters[pos] = [int(c.get("champion_id")) for c in hero["positionCounters"] if isinstance(c, dict) and c.get("champion_id") is not None]
                # positions数组
                if "positions" in hero and isinstance(hero["positions"], list):
                    for pos_item in hero["positions"]:
                        pos_raw = pos_item.get("positionName", "").upper()
                        pos = pos_map.get(pos_raw)
                        if pos:
                            pos_counters[pos] = [int(c.get("champion_id")) for c in pos_item.get("positionCounters", []) if isinstance(c, dict) and c.get("champion_id") is not None]
        lane_order = ["TOP", "JUN", "MID", "ADC", "SUP"]
        # 多线程写入MySQL
        try:
            hero_ids = list(hero_counter_map.keys())
            task_id = self.rich_progress.add_task(f"[Other] hero_counter写入MySQL", total=len(hero_ids))
            def update_one(hero_id):
                counter_dict = hero_counter_map[hero_id]
                # 按顺序构造有序字典
                ordered_counter = OrderedDict()
                for lane in lane_order:
                    if lane in counter_dict:
                        ordered_counter[lane] = counter_dict[lane]
                mysql_utils.update_hero_counter(hero_id, ordered_counter)
                self.rich_progress.advance(task_id)
            with ThreadPoolExecutor(max_workers=12) as executor:
                futures = [executor.submit(update_one, hero_id) for hero_id in hero_ids]
                for _ in as_completed(futures):
                    pass
            rich_logger.info(f"[Other] hero_counter已写入MySQL，共{len(hero_ids)}条")
        except Exception as e:
            rich_logger.error(f"[Other] hero_counter写入MySQL失败: {e}")

    def generate_logo_data(self) -> None:
        """
        生成英雄Logo数据。
        """
        count = 0
        try:
            with open(self.hero_info_path, "rb") as f:
                hero_info = orjson.loads(f.read())
            logo_data = []
            total = len(hero_info)
            task_id = self.rich_progress.add_task("[Other] 生成hero_Logo", total=total)
            for hero in hero_info:
                try:
                    hero_id = str(hero.get("heroId"))
                    name = hero.get("name")
                    heroLogo = hero.get("heroLogo")
                    logo_url = self.logo_url_template.format(heroLogo)
                    logo_data.append(
                        {"heroId": hero_id, "name": name, "heroLogo": logo_url}
                    )
                    count += 1
                except KeyError as e:
                    rich_logger.warning(f"字段缺失: {str(e)} | 英雄数据: {hero}")
                except Exception as e:
                    rich_logger.error(f"处理英雄异常: {str(e)} | 数据: {hero}")
                self.rich_progress.advance(task_id)
            with open(self.hero_logo_path, "wb") as f:
                f.write(orjson.dumps(logo_data, option=orjson.OPT_INDENT_2))
            rich_logger.info(f"[Other] hero_Logo生成完成丨共{count}条")
        except Exception as e:
            rich_logger.error(f"[Other] hero_Logo生成失败: {str(e)}")

    def get_team_list(self) -> None:
        """
        获取队伍列表。
        """

        def get_latest_season_game_id():
            """
            从 env.py 中读取 SEASONS（list结构），返回 id 最大且 type 最大的赛季的 id 和 type。
            处理多余逗号导致的 JSON 解析报错。
            :return: (id, type)
            """
            with open(env.ENV_SEASONS, "r", encoding="utf-8") as f:
                content = f.read()
            seasons_match = re.search(r"SEASONS\s*=\s*(\[.*?\])", content, re.DOTALL)
            if not seasons_match:
                raise Exception(f"未在 {env.ENV_SEASONS} 中找到 SEASONS 变量")
            try:
                # 先去除多余的结尾逗号
                seasons_json_str = seasons_match.group(1)
                # 用正则去掉最后一个元素后面的逗号
                seasons_json_str = re.sub(r",\s*\]", "]", seasons_json_str)
                seasons_list = orjson.loads(seasons_json_str)
            except Exception as e:
                raise Exception(f"解析 SEASONS 出错: {e}")
            # 先找id最大，再在这些中找type最大
            max_id = max(int(s["id"]) for s in seasons_list if s.get("id"))
            candidates = [s for s in seasons_list if int(s["id"]) == max_id]

            def type_max(type_str):
                if not type_str:
                    return -1
                return max(int(x) for x in type_str.split(",") if x.isdigit())

            best = max(candidates, key=lambda s: type_max(s.get("type")))
            return best["id"], best["type"]

        seasonId, stageIds = get_latest_season_game_id()
        self.team_list_params["seasonId"] = seasonId
        self.team_list_params["stageIds"] = stageIds
        try:
            task_id = self.rich_progress.add_task("[Other] 获取team_list", total=1)
            response = requests.get(
                url=self.team_list_url,
                params=self.team_list_params,
                cookies=self.cookies,
                headers=self.team_list_headers,
                verify=False  # 忽略SSL证书校验
            )
            if response.status_code != 200:
                rich_logger.error(
                    f"[Other] 请求team_list失败，状态码：{response.status_code}"
                )
                return
            try:
                team_list = response.json()
            except orjson.JSONDecodeError:
                rich_logger.error("[Other] team_list 响应内容不是有效的 JSON 格式")
                return
            with open(self.team_list_path, "wb") as f:
                f.write(orjson.dumps(team_list, option=env.ORJSON_OPTS))
            rich_logger.info(f"[Other] team_list获取完成")
            self.rich_progress.advance(task_id)
        except Exception as _error:
            rich_logger.error(f"[Other] 获取team_list失败: {str(_error)}")

    def main(self) -> None:
        """
        英雄数据主流程。
        """
        self.get_hero_list()
        self.generate_logo_data()
        self.get_team_list()
        self.get_hero_win_rate()  # 只保存json
        self.append_hero_id()  # 补全champion_id
        self.write_hero_win_rate_to_mysql()  # 聚合并写入MySQL
        self.append_counter(self.hero_win_rate_path)
