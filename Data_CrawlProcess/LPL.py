# -*- coding:utf-8 -*-
# @Software       :PyCharm
# @Project        :LOL-DeepWinPredictor
# @Path           :/Data_CrawlProcess
# @FileName       :LPL.py
# @Time           :2025/4/21 23:36
# @Author         :Viper373
# @GitHub         :https://github.com/Viper373
# @Home           :https://viper3.top
# @Blog           :https://blog.viper3.top

import asyncio
import os
import re
from functools import partial
from typing import Dict, List

import aiohttp
import orjson
import requests
from pymongo import ASCENDING, errors

from Data_CrawlProcess import env
from Data_CrawlProcess.Process import Process
from tool_utils.log_utils import RichLogger
from tool_utils.mongo_utils import MongoUtils
from tool_utils.progress_utils import RichProgressUtils

process = Process()
rich_logger = RichLogger()
mongo_utils = MongoUtils()


class LPL:
    def __init__(self, rich_progress=None):
        """
        LPL类初始化方法。
        :param rich_progress: RichProgressUtils实例（用于全局进度条）
        :return: None
        """
        self.url = "https://lpl.qq.com/web201612/data/LOL_MATCH2_MATCH_HOMEPAGE_BMATCH_LIST_{}.js"
        self.match_url = "https://open.tjstats.com/match-auth-app/open/v1/compound/matchDetail?matchId={}"
        self.seasons_url = "https://lol.qq.com/act/AutoCMS/publish/LOLWeb/EventdataTab/EventdataTab.js"
        self.headers = {
            'sec-ch-ua': '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Referer': 'https://lpl.qq.com/web202301/schedule.html',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': env.UA,  # UA头
            'Authorization': env.AUTHORIZATION,  # 身份验证
            'sec-ch-ua-platform': '"Windows"',
        }
        self.seasonsIds_headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,ja;q=0.5,ko;q=0.4,fr;q=0.3',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=2',
            'referer': 'https://lpl.qq.com/web202301/schedule.html',
            'sec-ch-ua': '"Microsoft Edge";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'script',
            'sec-fetch-mode': 'no-cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0',
        }
        self.cookies = {
            'tj_rp_did': '60013b4b18ce11efa938fe48ef6d951e',
        }
        self.proxies = env.PROXIES  # 代理
        self.rich_progress = rich_progress

    async def auto_seasonIds(self, col_name: str, rich_progress) -> None:
        """
        自动从LPL官网获取赛季数据，合并env.py中的SEASONS并写入MongoDB。
        :param col_name: MongoDB集合名称
        :param rich_progress: RichProgressUtils实例
        :return: None
        """
        rich_progress = rich_progress or RichProgressUtils()
        collection = mongo_utils.use_collection(col_name)
        try:
            loop = asyncio.get_event_loop()
            request_func = partial(
                requests.get, url=self.seasons_url, headers=self.seasonsIds_headers, proxies=self.proxies
            )
            response = await loop.run_in_executor(None, request_func, *tuple())
            response.encoding = 'utf-8'
            match = re.search(r'return\s+(\[.*?\])[\s;]*}\)', response.text)
            if not match:
                rich_logger.error("[LPL] auto_seasonIds: 未找到JSON数据")
                return
            json_str = match.group(1)
            data = orjson.loads(json_str)
            seasons = []
            for season in data:
                for game in season.get('domestic', []):
                    seasons.append({
                        "name": game.get("gameName"),
                        "id": game.get("iGameId"),
                        "type": game.get("sGameType"),
                        "url": game.get("url")
                    })
                for game in season.get('abroad', []):
                    seasons.append({
                        "name": game.get("gameName"),
                        "id": game.get("iGameId"),
                        "type": game.get("sGameType"),
                        "url": game.get("url")
                    })
            rich_logger.info(f"[LPL] auto_seasonIds: 官网获取到 {len(seasons)} 个赛季数据")
        except Exception as e:
            rich_logger.error(f"[LPL] auto_seasonIds: 获取官网赛季数据失败: {e}")
            return

        def get_existing_seasons():
            if not os.path.exists(env.ENV_SEASONS):
                return []
            with open(env.ENV_SEASONS, 'r', encoding='utf-8') as f:
                content = f.read()
            match = re.search(r'SEASONS\s*=\s*(\[.*?\])', content, re.DOTALL)
            if not match:
                return []
            try:
                return orjson.loads(match.group(1))
            except:
                return []

        existing_seasons = get_existing_seasons()

        all_ids = set()
        merged_seasons = []
        for s in seasons + existing_seasons:
            if s['id'] not in all_ids:
                merged_seasons.append(s)
                all_ids.add(s['id'])
        rich_logger.info(f"[LPL] auto_seasonIds: 合并后共有 {len(merged_seasons)} 个赛季数据（已自动去重）")

        content = "SEASONS = " + orjson.dumps(merged_seasons, option=orjson.OPT_INDENT_2).decode('utf-8') + "\n"
        if os.path.exists(env.ENV_SEASONS):
            with open(env.ENV_SEASONS, 'r', encoding='utf-8') as f:
                existing_content = f.read()
            if 'SEASONS = [' in existing_content:
                new_content = re.sub(r'SEASONS = \[.*?\]', content, existing_content, flags=re.DOTALL)
            else:
                new_content = existing_content + '\n' + content
        else:
            new_content = content
        with open(env.ENV_SEASONS, 'w', encoding='utf-8') as f:
            f.write(new_content)
        rich_logger.info(f"[LPL] auto_seasonIds: 赛季数据已成功更新到env.py文件！")
        # 4. 写入MongoDB
        collection.create_index([("id", ASCENDING)], unique=True)
        queue = asyncio.Queue(maxsize=20)
        fetch_task_id = rich_progress.add_task("[LPL] auto_seasonIds生产", total=len(merged_seasons))
        store_task_id = rich_progress.add_task("[LPL] auto_seasonIds入库", total=len(merged_seasons))

        async def producer():
            for season in merged_seasons:
                await queue.put(season)
                rich_progress.advance(fetch_task_id)
            await queue.put(None)

        async def consumer():
            count = 0
            while True:
                item = await queue.get()
                if item is None:
                    break
                try:
                    collection.insert_one(item)
                except errors.DuplicateKeyError:
                    pass
                count += 1
                rich_progress.advance(store_task_id)
            rich_progress.update(store_task_id, completed=len(merged_seasons))

        await asyncio.gather(producer(), consumer())
        rich_logger.info(f"[LPL] auto_seasonIds: 赛季数据已全部入库，共{len(merged_seasons)}条")

    @staticmethod
    async def get_seasonIds(col_name: str, seasons: list, rich_progress) -> None:
        """
        异步生产者-消费者：获取赛季ID并写入数据库。
        :param col_name: MongoDB集合名称
        :param seasons: 赛季信息列表，每项为dict，需提取id和name，id去重
        :param rich_progress: RichProgressUtils实例
        :return: None
        """
        rich_progress = rich_progress or RichProgressUtils()
        collection = mongo_utils.use_collection(col_name)
        collection.create_index([("season_id", ASCENDING)], unique=True)
        # 只保留id和name，并对id去重
        seen_ids = set()
        season_pairs = []
        for s in seasons:
            sid = s.get('id')
            sname = s.get('name')
            if sid and sname and sid not in seen_ids:
                season_pairs.append({"season_name": sname, "season_id": sid})
                seen_ids.add(sid)
        queue = asyncio.Queue(maxsize=20)
        fetch_task_id = rich_progress.add_task("[LPL] seasonIDs生产", total=len(season_pairs))
        store_task_id = rich_progress.add_task("[LPL] seasonIDs入库", total=len(season_pairs))

        async def producer():
            for pair in season_pairs:
                await queue.put(pair)
                rich_progress.advance(fetch_task_id)
            await queue.put(None)

        async def consumer():
            count = 0
            while True:
                item = await queue.get()
                if item is None:
                    break
                try:
                    collection.insert_one(item)
                except errors.DuplicateKeyError:
                    pass
                count += 1
                rich_progress.advance(store_task_id)
            rich_progress.update(store_task_id, completed=len(season_pairs))

        await asyncio.gather(producer(), consumer())
        rich_logger.info(f"爬取完成丨共计[{len(season_pairs)}]LPL_season")

    async def get_bMatchIds(self, col_name: str, seasons: list, rich_progress) -> None:
        """
        异步生产者-消费者：获取bMatchId并写入数据库。
        :param col_name: MongoDB集合名称
        :param seasons: 赛季信息列表，每项为dict，需包含season_id
        :param rich_progress: RichProgressUtils实例
        :return: None
        """
        rich_progress = rich_progress or self.rich_progress
        collection = mongo_utils.use_collection(col_name)
        collection.create_index([("bMatchId", ASCENDING)], unique=True)
        queue = asyncio.Queue(maxsize=50)
        all_records = []

        # 先收集所有bMatchId
        async def fetch_all_records():
            async def fetch_season_data(_url: str):
                try:
                    loop = asyncio.get_event_loop()
                    request_func = partial(
                        requests.get, url=_url,
                        headers=self.headers,
                        cookies=self.cookies,
                        proxies=self.proxies
                    )
                    response = await loop.run_in_executor(None, request_func)
                    if response.status_code != 200:
                        rich_logger.error(f"获取bMatchId失败，状态码: {response.status_code}")
                        return
                    seasons_data = orjson.loads(response.text)
                    if seasons_data.get('status') == "0":
                        msg = seasons_data.get('msg')
                        for match in msg:
                            record = {
                                'GameName': match.get('GameName'),
                                'bMatchName': match.get('bMatchName'),
                                'MatchDate': match.get('MatchDate'),
                                'bMatchId': match.get('bMatchId')
                            }
                            all_records.append(record)
                except Exception as _error:
                    rich_logger.error(f"爬取[LPL]bMatchId错误: {_error}")

            urls = [self.url.format(season["season_id"]) for season in seasons]
            await asyncio.gather(*(fetch_season_data(url) for url in urls))

        await fetch_all_records()

        fetch_task_id = rich_progress.add_task("[LPL] bMatchId生产", total=len(all_records))
        store_task_id = rich_progress.add_task("[LPL] bMatchId入库", total=len(all_records))

        async def producer_queue():
            for record in all_records:
                await queue.put(record)
                rich_progress.advance(fetch_task_id)
            await queue.put(None)

        async def consumer():
            count = 0
            while True:
                item = await queue.get()
                if item is None:
                    break
                try:
                    collection.insert_one(item)
                except errors.DuplicateKeyError:
                    pass
                count += 1
                rich_progress.advance(store_task_id)
            rich_progress.update(store_task_id, completed=len(all_records))

        await asyncio.gather(producer_queue(), consumer())
        rich_logger.info(f"爬取完成丨LPL_bMatchId已全部入库")

    async def get_match_data(self, bmatch_ids: List[str], col_name: str, rich_progress=None) -> None:
        """
        生产者-消费者解耦：高并发爬取match_data并结构化入库，进度独立。
        :param bmatch_ids: 比赛ID列表
        :param col_name: MongoDB集合名称
        :param rich_progress: RichProgressUtils实例
        :return: None
        """
        collection = mongo_utils.use_collection(col_name)
        session_timeout = aiohttp.ClientTimeout(total=30)
        fetch_task_id = rich_progress.add_task("[LPL] match_data爬取", total=len(bmatch_ids))
        process_task_id = rich_progress.add_task("[LPL] process_data入库", total=len(bmatch_ids))
        hero_win_rates = process.read_win_rate()

        process_queue = asyncio.Queue(maxsize=500)
        total_count = len(bmatch_ids)

        async def fetcher():
            async with aiohttp.ClientSession(timeout=session_timeout) as session:
                sem = asyncio.Semaphore(50)

                async def fetch_one(bid):
                    url = self.match_url.format(bid)
                    async with sem:
                        try:
                            async with session.get(url, headers=self.headers, cookies=self.cookies) as resp:
                                data = await resp.json()
                                if data.get('success') and data.get('data'):
                                    match = data['data']
                                    await process_queue.put(match)
                        except Exception as e:
                            rich_logger.error(f"[LPL] match_data爬取失败: {bid} {e}")
                        self.rich_progress.advance(fetch_task_id)

                await asyncio.gather(*(fetch_one(bid) for bid in bmatch_ids))
            await process_queue.put(None)

        async def processor():
            count = 0
            while True:
                match = await process_queue.get()
                if match is None:
                    break
                try:
                    processed_data = {}
                    teamAId, teamAName, teamBId, teamBName = match['teamAId'], match['teamAName'], match['teamBId'], match['teamBName']
                    matchWin = 1 if match["matchWin"] == teamAId else 0
                    processed_data.update({
                        "teamAId": teamAId,
                        "teamAName": teamAName,
                        "teamBId": teamBId,
                        "teamBName": teamBName,
                        "matchWin": matchWin,
                    })
                    matchInfos = match["matchInfos"]
                    for bo in matchInfos:
                        teamInfos = bo["teamInfos"]
                        team_po = "A"
                        for team in teamInfos:
                            playerInfos = team["playerInfos"]
                            count_ = 1
                            for player in playerInfos:
                                playerLocation = "ADC" if player["playerLocation"] == "BOT" else player["playerLocation"]
                                heroId, heroTitle, heroName = player["heroId"], player["heroTitle"], player["heroName"]
                                key = f"{heroId}{playerLocation[:3].upper()}"
                                heroWinRate = hero_win_rates.get(key, 0.50)
                                processed_data.update({
                                    f"{team_po}{count_}playerLocation": playerLocation,
                                    f"{team_po}{count_}heroId": heroId,
                                    f"{team_po}{count_}heroName": f"{heroTitle}-{heroName}",
                                    f"{team_po}{count_}heroWinRate": heroWinRate,
                                })
                                count_ += 1
                            team_po = "B"
                    if isinstance(processed_data, dict):
                        collection.insert_one(processed_data)
                    else:
                        rich_logger.error(f"[LPL] processed_data类型错误: {type(processed_data)} | bMatchId: {match.get('bMatchId', 'unknown')}")
                except Exception as e:
                    match_id = match.get('bMatchId', 'unknown') if isinstance(match, dict) else 'unknown'
                    snippet = orjson.dumps(match)[:200].decode('utf-8') if isinstance(match, dict) else str(match)[:200]
                    rich_logger.error(f"[LPL] process_data单条处理失败: {str(e)} | bMatchId: {match_id} | 数据片段: {snippet} ...")
                count += 1
                rich_progress.advance(process_task_id)
            rich_progress.update(process_task_id, completed=total_count)

        await asyncio.gather(fetcher(), processor())
        rich_logger.info(f"[LPL] match_data已全部入库")
        return None

    async def main(self, lpl_db: str, col_season: str, col_bmatch: str, col_match: str, seasons: dict) -> None:
        """
        LPL主流程，自动串联所有流程：抓取seasonIds、bMatchIds、match_data。
        :param lpl_db: LPL专用MongoDB数据库名称
        :param col_season: 赛季ID集合名
        :param col_bmatch: bMatchId集合名
        :param col_match: 结构化比赛数据集合名
        :param seasons: 赛季ID映射字典{str: str}
        :return: None
        """
        mongo_utils.use_db(lpl_db)
        await self.get_seasonIds(col_season, seasons, self.rich_progress)
        await self.get_bMatchIds(col_bmatch, seasons, self.rich_progress)
        bmatch_ids = [item['bMatchId'] for item in mongo_utils.use_collection(col_bmatch).find({}, {'bMatchId': 1, '_id': 0})]
        await self.get_match_data(bmatch_ids, col_match, self.rich_progress)
        rich_logger.info("[LPL] main流程执行完毕")
