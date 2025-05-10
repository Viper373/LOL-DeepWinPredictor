# -*- coding:utf-8 -*-
# @Software       :PyCharm
# @Project        :LOL-DeepWinPredictor
# @Path           :/Data_CrawlProcess
# @FileName       :Wanplus.py
# @Time           :2025/4/21 23:36
# @Author         :Viper373
# @GitHub         :https://github.com/Viper373
# @Home           :https://viper3.top
# @Blog           :https://blog.viper3.top


import asyncio
import copy
from functools import partial
from typing import List, Optional

import aiohttp
import orjson
import requests
from bs4 import BeautifulSoup
from pymongo import ASCENDING, errors

from Data_CrawlProcess import env
from Data_CrawlProcess.Process import Process
from tool_utils.log_utils import RichLogger
from tool_utils.mongo_utils import MongoUtils
from tool_utils.progress_utils import RichProgressUtils

process = Process()
rich_logger = RichLogger()
rich_progress = RichProgressUtils()
mongo_utils = MongoUtils()


class Wanplus:
    def __init__(self, rich_progress=None):
        """
        Wanplus类初始化方法。
        :param rich_progress: RichProgressUtils实例（用于全局进度条）
        :return: None
        """
        self.start_url = "https://wanplus.cn/ajax/stats/list"
        self.team_url = "https://www.wanplus.cn/ajax/team/recent"
        self.match_url = "https://www.wanplus.cn/schedule/{}.html"
        self.bo_url = "https://www.wanplus.cn/ajax/matchdetail/{}"
        self.headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,ja;q=0.5,ko;q=0.4,fr;q=0.3',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://www.wanplus.cn',
            'Pragma': 'no-cache',
            'Referer': 'https://www.wanplus.cn/lol/teamstats',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0',
            'X-CSRF-Token': '1568910741',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Microsoft Edge";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        self.cookies = {
            'wanplus_sid': '30a98b3049e7fdb540466e4b8ba8d3aa',
            'wp_pvid': '9102809835',
            'wp_info': 'ssid=s4318647280',
            'Hm_lvt_23f0107a6dc01005e1cee339f3e738e9': '1745729309,1745824404',
            'HMACCOUNT': '499406815A7E1420',
            'wanplus_token': 'e383c73bd4ebd47dd22cd018bdcece59',
            'wanplus_storage': 'w%2F0j5rOmbyuiKxm9zzaVzbybAqKwrSXHI5Ew3gGl58bh4NW5lPnTHHQ2gts8TehRKLE9zwNsxT4hH5VdpJiAgc%2FHlnes0bhxtraCZFLeY%2FhwzmvP%2BvZn22cC3VuqsLZLc%2FQ3wUwI9ScitpOHv8IFUfsiHg',
            'wanplus_csrf': '_csrf_tk_1485024661',
            'isShown': '1',
            'gameType': '2',
            'Hm_lpvt_23f0107a6dc01005e1cee339f3e738e9': '1745953169',
        }
        self.data = {
            '_gtk': env.GTK,
            'draw': '1',
            'columns[0][data]': 'order',
            'columns[0][name]': '',
            'columns[0][searchable]': 'true',
            'columns[0][orderable]': 'false',
            'columns[0][search][value]': '',
            'columns[0][search][regex]': 'false',
            'columns[1][data]': 'teamname',
            'columns[1][name]': '',
            'columns[1][searchable]': 'true',
            'columns[1][orderable]': 'false',
            'columns[1][search][value]': '',
            'columns[1][search][regex]': 'false',
            'columns[2][data]': 'kda',
            'columns[2][name]': '',
            'columns[2][searchable]': 'true',
            'columns[2][orderable]': 'true',
            'columns[2][search][value]': '',
            'columns[2][search][regex]': 'false',
            'columns[3][data]': 'killsPergame',
            'columns[3][name]': '',
            'columns[3][searchable]': 'true',
            'columns[3][orderable]': 'true',
            'columns[3][search][value]': '',
            'columns[3][search][regex]': 'false',
            'columns[4][data]': 'deathsPergame',
            'columns[4][name]': '',
            'columns[4][searchable]': 'true',
            'columns[4][orderable]': 'true',
            'columns[4][search][value]': '',
            'columns[4][search][regex]': 'false',
            'columns[5][data]': 'damagetoheroPermin',
            'columns[5][name]': '',
            'columns[5][searchable]': 'true',
            'columns[5][orderable]': 'true',
            'columns[5][search][value]': '',
            'columns[5][search][regex]': 'false',
            'columns[6][data]': 'fstbloodpercentage',
            'columns[6][name]': '',
            'columns[6][searchable]': 'true',
            'columns[6][orderable]': 'true',
            'columns[6][search][value]': '',
            'columns[6][search][regex]': 'false',
            'columns[7][data]': 'avgDuration',
            'columns[7][name]': '',
            'columns[7][searchable]': 'true',
            'columns[7][orderable]': 'true',
            'columns[7][search][value]': '',
            'columns[7][search][regex]': 'false',
            'columns[8][data]': 'goldpermatch',
            'columns[8][name]': '',
            'columns[8][searchable]': 'true',
            'columns[8][orderable]': 'true',
            'columns[8][search][value]': '',
            'columns[8][search][regex]': 'false',
            'columns[9][data]': 'goldsPermin',
            'columns[9][name]': '',
            'columns[9][searchable]': 'true',
            'columns[9][orderable]': 'true',
            'columns[9][search][value]': '',
            'columns[9][search][regex]': 'false',
            'columns[10][data]': 'lasthitPermin',
            'columns[10][name]': '',
            'columns[10][searchable]': 'true',
            'columns[10][orderable]': 'true',
            'columns[10][search][value]': '',
            'columns[10][search][regex]': 'false',
            'columns[11][data]': 'dragonkillsPergame',
            'columns[11][name]': '',
            'columns[11][searchable]': 'true',
            'columns[11][orderable]': 'true',
            'columns[11][search][value]': '',
            'columns[11][search][regex]': 'false',
            'columns[12][data]': 'dragonkillspercentage',
            'columns[12][name]': '',
            'columns[12][searchable]': 'true',
            'columns[12][orderable]': 'true',
            'columns[12][search][value]': '',
            'columns[12][search][regex]': 'false',
            'columns[13][data]': 'baronkillsPergame',
            'columns[13][name]': '',
            'columns[13][searchable]': 'true',
            'columns[13][orderable]': 'true',
            'columns[13][search][value]': '',
            'columns[13][search][regex]': 'false',
            'columns[14][data]': 'baronkillspercentage',
            'columns[14][name]': '',
            'columns[14][searchable]': 'true',
            'columns[14][orderable]': 'true',
            'columns[14][search][value]': '',
            'columns[14][search][regex]': 'false',
            'columns[15][data]': 'wardsplacedpermin',
            'columns[15][name]': '',
            'columns[15][searchable]': 'true',
            'columns[15][orderable]': 'true',
            'columns[15][search][value]': '',
            'columns[15][search][regex]': 'false',
            'columns[16][data]': 'wardskilledpermin',
            'columns[16][name]': '',
            'columns[16][searchable]': 'true',
            'columns[16][orderable]': 'true',
            'columns[16][search][value]': '',
            'columns[16][search][regex]': 'false',
            'columns[17][data]': 'wardskilledrate',
            'columns[17][name]': '',
            'columns[17][searchable]': 'true',
            'columns[17][orderable]': 'true',
            'columns[17][search][value]': '',
            'columns[17][search][regex]': 'false',
            'columns[18][data]': 'towertakensPergame',
            'columns[18][name]': '',
            'columns[18][searchable]': 'true',
            'columns[18][orderable]': 'true',
            'columns[18][search][value]': '',
            'columns[18][search][regex]': 'false',
            'columns[19][data]': 'towerdeathsPergame',
            'columns[19][name]': '',
            'columns[19][searchable]': 'true',
            'columns[19][orderable]': 'true',
            'columns[19][search][value]': '',
            'columns[19][search][regex]': 'false',
            'order[0][column]': '2',
            'order[0][dir]': 'desc',
            'start': '0',
            'length': '20',
            'search[value]': '',
            'search[regex]': 'false',
            'area': '',
            'eid': None,
            'type': 'team',
            'gametype': '2',
            'filter': '{"team":{},"player":{},"meta":{}}',
        }
        self.params = {
            'isAjax': '1',
            'teamId': '7320',
            'gameType': '2',
            'objTeamId': '0',
            'page': '99',
            'egid': '0',
            '_gtk': env.GTK,
        }
        self.proxies = env.PROXIES
        self.hero_win_rates = process.read_win_rate()
        self.po_dict = {"1": "TOP", "2": "JUN", "3": "MID", "4": "ADC", "5": "SUP"}
        self.rich_progress = rich_progress or RichProgressUtils()

    async def get_eids(self, db_name: str, col_name: str) -> None:
        """
        异步生产者-消费者：获取赛事ID并写入数据库。
        :param db_name: MongoDB数据库名称
        :param col_name: MongoDB集合名称
        :return: None
        """
        mongo_utils.use_db(db_name)
        collection = mongo_utils.use_collection(col_name)
        collection.create_index([("eid", ASCENDING)], unique=True)
        queue = asyncio.Queue(maxsize=20)

        # 先获取eids
        loop = asyncio.get_event_loop()
        request_func = partial(
            requests.post,
            url=self.start_url,
            headers=self.headers,
            cookies=self.cookies,
            data=self.data,
            proxies=self.proxies
        )
        response = await loop.run_in_executor(None, request_func)
        if response.status_code != 200:
            rich_logger.error(f"获取eids失败，状态码: {response.status_code}")
            return
        eid_dict = orjson.loads(response.text).get('eventList', {})
        if not eid_dict:
            rich_logger.warning("未获取到eids数据")
            return
        eids = [
            {"eid": eid, "name": info.get('name')}
            for eid, info in eid_dict.items()
        ]
        fetch_task_id = self.rich_progress.add_task("[Wanplus] eids生产", total=len(eids))
        store_task_id = self.rich_progress.add_task("[Wanplus] eids入库", total=len(eids))

        async def producer():
            for eid_info in eids:
                await queue.put(eid_info)
                self.rich_progress.advance(fetch_task_id)
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
                self.rich_progress.advance(store_task_id)
            self.rich_progress.update(store_task_id, completed=len(eids))
            rich_logger.info(f"[Wanplus] 赛事ID爬取完成丨共{count}条")

        await asyncio.gather(producer(), consumer())

    async def get_teamids(self, db_name: str, col_name: str, eid_list: list) -> None:
        """
        异步生产者-消费者：获取队伍ID并写入数据库。
        :param db_name: MongoDB数据库名称
        :param col_name: MongoDB集合名称
        :param eid_list: 赛事eid列表
        :return: None
        """
        mongo_utils.use_db(db_name)
        collection = mongo_utils.use_collection(col_name)
        collection.create_index([("teamid", ASCENDING)], unique=True)
        queue = asyncio.Queue(maxsize=100)
        # 先统计所有teamid的总数
        total_teamids = 0
        teamid_records = []
        loop = asyncio.get_event_loop()
        for _eid in eid_list:
            data = copy.deepcopy(self.data)
            data['eid'] = _eid
            try:
                request_func = partial(
                    requests.post,
                    url=self.start_url,
                    headers=self.headers,
                    cookies=self.cookies,
                    data=data,
                    proxies=self.proxies
                )
                response = await loop.run_in_executor(None, request_func)
                if response.status_code != 200:
                    continue
                response_json = orjson.loads(response.text)
                if response_json.get('msg') == 'success':
                    data_list = response_json.get('data')
                    if not data_list:
                        continue
                    for d in data_list:
                        if d.get('teamid'):
                            record = {
                                'teamid': d.get('teamid'),
                                'teamname': d.get('teamname')
                            }
                            teamid_records.append(record)
            except Exception:
                continue
        total_teamids = len(teamid_records)
        fetch_task_id = self.rich_progress.add_task("[Wanplus] teamids生产", total=total_teamids)
        store_task_id = self.rich_progress.add_task("[Wanplus] teamids入库", total=total_teamids)

        async def producer():
            for record in teamid_records:
                await queue.put(record)
                self.rich_progress.advance(fetch_task_id)
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
                self.rich_progress.advance(store_task_id)
            self.rich_progress.update(store_task_id, completed=total_teamids)
            rich_logger.info(f"[Wanplus] 队伍ID爬取完成丨共{count}条")

        await asyncio.gather(producer(), consumer())

    async def get_scheduleids(self, db_name: str, col_name: str, teamid_list: list) -> None:
        """
        异步并发生产者-消费者：获取赛程ID并写入数据库。
        :param db_name: MongoDB数据库名称
        :param col_name: MongoDB集合名称
        :param teamid_list: 队伍ID列表
        :return: None
        """
        mongo_utils.use_db(db_name)
        collection = mongo_utils.use_collection(col_name)
        collection.create_index([("scheduleid", ASCENDING)], unique=True)
        queue = asyncio.Queue(maxsize=100)

        async def fetch_one(_teamid):
            params = copy.deepcopy(self.params)
            params['teamId'] = _teamid
            try:
                loop = asyncio.get_event_loop()
                request_func = partial(
                    requests.post,
                    url=self.team_url,
                    headers=self.headers,
                    cookies=self.cookies,
                    params=params,
                    proxies=self.proxies
                )
                response = await loop.run_in_executor(None, request_func)
                if response.status_code != 200:
                    return []
                response_json = orjson.loads(response.text)
                data = response_json.get('data')
                if not data:
                    return []
                return [
                    {
                        'scheduleid': d.get('scheduleid'),
                        'desc': f"{d.get('oneseedname')} vs {d.get('twoseedname')}丨{d.get('starttime')}"
                    }
                    for d in data if d.get('scheduleid')
                ]
            except Exception:
                return []

        sem = asyncio.Semaphore(20)

        async def sem_fetch(_teamid):
            async with sem:
                return await fetch_one(_teamid)

        all_results = await asyncio.gather(*(sem_fetch(tid) for tid in teamid_list))
        scheduleid_records = [item for sublist in all_results for item in sublist]
        total_scheduleids = len(scheduleid_records)
        fetch_task_id = self.rich_progress.add_task("[Wanplus] scheduleids生产", total=total_scheduleids)
        store_task_id = self.rich_progress.add_task("[Wanplus] scheduleids入库", total=total_scheduleids)

        async def producer():
            for record in scheduleid_records:
                await queue.put(record)
                self.rich_progress.advance(fetch_task_id)
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
                self.rich_progress.advance(store_task_id)
            self.rich_progress.update(store_task_id, completed=total_scheduleids)
            rich_logger.info(f"[Wanplus] 赛程ID爬取完成丨共{count}条")

        await asyncio.gather(producer(), consumer())

    async def get_boids(self, db_name: str, col_name: str, scheduleid_list: list) -> None:
        """
        并发异步爬取boid并写入数据库，极大提升速度。
        :param db_name: MongoDB数据库名称
        :param col_name: MongoDB集合名称
        :param scheduleid_list: 赛程ID列表
        :return: None
        """
        mongo_utils.use_db(db_name)
        collection = mongo_utils.use_collection(col_name)
        collection.create_index([("boid", ASCENDING)], unique=True)
        total = len(scheduleid_list)
        fetch_task_id = self.rich_progress.add_task("[Wanplus] boid生产", total=total)
        sem = asyncio.Semaphore(50)

        async def fetch_one(_scheduleid):
            async with sem:
                url = self.match_url.format(_scheduleid)
                try:
                    loop = asyncio.get_event_loop()
                    request_func = partial(
                        requests.get,
                        url=url,
                        headers=self.headers,
                        cookies=self.cookies,
                        proxies=self.proxies
                    )
                    response = await loop.run_in_executor(None, request_func, *tuple())
                    if response.status_code != 200:
                        self.rich_progress.advance(fetch_task_id)
                        return []
                    soup = BeautifulSoup(response.text, 'html.parser')
                    team_detail_ov = soup.find('ul', attrs={'class': 'team-detail ov'})
                    if not team_detail_ov:
                        self.rich_progress.advance(fetch_task_id)
                        return []
                    try:
                        team_left = team_detail_ov.find('li', attrs={'class': 'team-left'}).find('a').find('span').text
                        bo_time = team_detail_ov.find('span', attrs={'class': 'time'}).text
                        team_right = team_detail_ov.find('li', attrs={'class': 'team-right tr'}).find('a').find('span').text
                        game_div = soup.find('div', attrs={'class': 'game'})
                        if not game_div:
                            self.rich_progress.advance(fetch_task_id)
                            return []
                        data_matchid = game_div.find_all('a')
                        records = []
                        for match_id in data_matchid:
                            bo_count = match_id.text[-1]
                            bo_detail = f"{bo_time}丨{team_left} vs {team_right}丨BO{bo_count}"
                            bo_id = match_id.get('data-matchid')
                            if bo_id:
                                record = {
                                    'boid': bo_id,
                                    'desc': bo_detail
                                }
                                records.append(record)
                        self.rich_progress.advance(fetch_task_id)
                        return records
                    except Exception:
                        self.rich_progress.advance(fetch_task_id)
                        return []
                except Exception:
                    self.rich_progress.advance(fetch_task_id)
                    return []

        # 1. 生产阶段：并发爬取所有boid
        all_results = await asyncio.gather(*(fetch_one(sid) for sid in scheduleid_list))
        boid_records = [item for sublist in all_results for item in sublist]

        # 2. 动态设置入库进度条
        store_task_id = self.rich_progress.add_task("[Wanplus] boid入库", total=len(boid_records))

        # 3. 入库阶段
        batch_size = 1000
        count = 0
        for i in range(0, len(boid_records), batch_size):
            batch = boid_records[i:i+batch_size]
            try:
                mongo_utils.insert_many(col_name, batch)
            except errors.BulkWriteError:
                pass  # 跳过重复主键等错误
            count += len(batch)
            self.rich_progress.advance(store_task_id, advance=len(batch))
        self.rich_progress.update(store_task_id, completed=count)
        rich_logger.info(f"[Wanplus] boid爬取完成丨共{count}条")

    async def get_match_data(self, boids_list: List[str], db_name: str, col_name: str):
        """
        生产者-消费者解耦：高并发爬取match_data并结构化入库，进度独立。
        :param boids_list: BOID列表
        :param db_name: MongoDB数据库名称
        :param col_name: MongoDB集合名称
        :return: None
        """
        session_timeout = aiohttp.ClientTimeout(total=30)
        fetch_task_id = self.rich_progress.add_task("[Wanplus] match_data爬取", total=len(boids_list))
        process_task_id = self.rich_progress.add_task("[Wanplus] match_data入库", total=len(boids_list))
        hero_win_rates = self.hero_win_rates
        total_count = len(boids_list)
        process_queue = asyncio.Queue(maxsize=500)
        sem = asyncio.Semaphore(200)

        async def fetcher():
            async with aiohttp.ClientSession(timeout=session_timeout) as session:
                async def fetch_one(boid):
                    url = self.bo_url.format(boid)
                    async with sem:
                        try:
                            async with session.get(url, headers=self.headers, cookies=self.cookies) as resp:
                                try:
                                    text = await resp.text()
                                    data = orjson.loads(text)
                                except Exception as e:
                                    rich_logger.error(f"[Wanplus] match_data爬取失败: {boid} {resp.status}, message='{e}', url='{url}', resp_text='{text[:100]}'")
                                    return
                                if data.get('msg') == 'success' and data.get('data'):
                                    match_data = data['data']
                                    # 类型判断，防止NoneType报错
                                    if not match_data or not isinstance(match_data, dict):
                                        return
                                    match = {"boid": boid, "match_data": match_data}
                                    await process_queue.put(match)
                        except Exception as e:
                            rich_logger.error(f"[Wanplus] match_data爬取失败: {boid} {e}")
                        self.rich_progress.advance(fetch_task_id)

                await asyncio.gather(*(fetch_one(boid) for boid in boids_list))
            await process_queue.put(None)

        async def processor():
            count = 0
            mongo_utils.use_db(db_name)
            collection = mongo_utils.use_collection(col_name)
            while True:
                match = await process_queue.get()
                if match is None:
                    break
                try:
                    # 类型判断，防止NoneType报错
                    if not match or not isinstance(match, dict):
                        process_queue.task_done()
                        continue
                    if 'boid' not in match or 'match_data' not in match:
                        process_queue.task_done()
                        continue
                    processed_data = {"boid": match['boid']}
                    new_match = match["match_data"]
                    if not new_match or not isinstance(new_match, dict):
                        process_queue.task_done()
                        continue
                    plList = new_match.get("plList")
                    info = new_match.get("info")
                    if not plList or not info:
                        process_queue.task_done()
                        continue
                    processed_data.update({
                        "teamAId": info["oneteam"]["teamid"],
                        "teamAName": info["oneteam"]["teamalias"],
                        "teamBId": info["twoteam"]["teamid"],
                        "teamBName": info["twoteam"]["teamalias"],
                        "matchWin": 1 if info["winner"] == info["oneteam"]["teamid"] else 0,
                    })
                    team_po = "A"
                    isbreak = False
                    for pl in plList:
                        if not isinstance(pl, dict):
                            continue  # 跳过空列表或异常结构
                        for idx, p in pl.items():
                            playerLocation = self.po_dict.get(idx)
                            try:
                                heroId, heroName = p["cpheroid"], p["heroname"]
                            except Exception:
                                isbreak = True
                                continue
                            key = f"{heroId}{playerLocation[:3].upper()}"
                            heroWinRate = hero_win_rates.get(key, 0.50)
                            processed_data.update({
                                f"{team_po}{idx}playerLocation": playerLocation,
                                f"{team_po}{idx}heroId": heroId,
                                f"{team_po}{idx}heroName": f"{heroName}",
                                f"{team_po}{idx}heroWinRate": heroWinRate,
                            })
                        team_po = "B"
                    if not isbreak:
                        collection.insert_one(processed_data)
                except Exception as e:
                    rich_logger.error(f"[Wanplus] process_data单条处理失败: {str(e)} | 数据: {match}")
                count += 1
                self.rich_progress.advance(process_task_id)
            self.rich_progress.update(process_task_id, completed=total_count)

        await asyncio.gather(fetcher(), processor())
        rich_logger.info(f"[Wanplus] match_data已全部入库")
        return None

    async def main(self, wanplus_db=None, col_eid=None, col_team=None, col_schedule=None, col_boid=None, col_match=None) -> None:
        """
        Wanplus主流程，自动串联所有流程：抓取eids、teamids、scheduleids、boids、match_data。
        :param wanplus_db: Wanplus专用MongoDB数据库名称
        :param col_eid: 赛事ID集合名
        :param col_team: 队伍ID集合名
        :param col_schedule: 赛程ID集合名
        :param col_boid: boid集合名
        :param col_match: 结构化比赛数据集合名
        :return: None
        """
        mongo_utils.use_db(wanplus_db)
        await self.get_eids(wanplus_db, col_eid)
        eid_list = [item['eid'] for item in mongo_utils.use_collection(col_eid).find({}, {'eid': 1, '_id': 0})]
        await self.get_teamids(wanplus_db, col_team, eid_list)
        teamid_list = [item['teamid'] for item in mongo_utils.use_collection(col_team).find({}, {'teamid': 1, '_id': 0})]
        await self.get_scheduleids(wanplus_db, col_schedule, teamid_list)
        scheduleid_list = [item.get('scheduleid') for item in mongo_utils.use_collection(col_schedule).find({}, {'scheduleid': 1, '_id': 0}) if item.get('scheduleid') is not None]
        await self.get_boids(wanplus_db, col_boid, scheduleid_list)
        boids_list = [item['boid'] for item in mongo_utils.use_collection(col_boid).find({}, {'boid': 1, '_id': 0})]
        await self.get_match_data(boids_list, wanplus_db, col_match)
        rich_logger.info(f"[Wanplus] main流程执行完毕")
