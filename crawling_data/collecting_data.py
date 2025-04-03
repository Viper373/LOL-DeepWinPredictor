# -*- coding:utf-8 -*-
# @Project        :LPL
# @FileName       :collecting_data.py
# @Time           :2025/3/5 00:13
# @Software       :PyCharm
# @Author         :Viper373
# @Index          :https://viper3.top
# @Blog           :https://blog.viper3.top

import os
import sys
import requests
from bs4 import BeautifulSoup
import json
import copy
from pymongo import MongoClient, errors, ASCENDING
from rich.logging import RichHandler
from rich.progress import Progress, BarColumn, SpinnerColumn, TimeRemainingColumn, TimeElapsedColumn, TransferSpeedColumn  # rich进度条
from rich.panel import Panel  # rich面板
from rich.box import DOUBLE  # rich面板样式
import logging  # 日志
from concurrent.futures import ThreadPoolExecutor, as_completed  # 线程池
import signal  # 信号处理
from threading import Event
from typing import Dict, List

from BILSTM_Att import env

# 获取当前脚本的目录
script_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目的根目录（假设你的项目根目录在上两级）
project_root = os.path.abspath(os.path.join(script_dir, os.pardir))
if project_root not in sys.path:
    sys.path.append(project_root)

# rich进度条样式配置
page_columns = [
    "[progress.description]{task.description}({task.completed}/{task.total})",  # 设置进度条头部
    SpinnerColumn(spinner_name='aesthetic', style="white"),  # 设置显示Spinner动画{spinner_name：头部动画名称；style：头部动画颜色}
    TransferSpeedColumn(),  # 设置传输速度
    BarColumn(complete_style="magenta", finished_style="green"),  # 设置进度条体{complete_style：进行中颜色；finished_style：完成颜色}
    "[progress.percentage][white]{task.percentage:>3.2f}%",  # 设置进度条尾部{[color]：百分比颜色；task.percentage：百分比格式化}
    "🕒",  # 设置进度条共计执行时间样式
    TimeElapsedColumn(),
    "⏳",  # 设置进度条预计剩余时间样式
    TimeRemainingColumn(),
]
# rich日志处理器配置
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

done_event = Event()


def handle_sigint(signum, frame):
    done_event.set()


signal.signal(signal.SIGINT, handle_sigint)


# rich Column类添加表格样式
class WriteProgress(Progress):
    def get_renderables(self):
        yield Panel(self.make_tasks_table(self.tasks), box=DOUBLE)


# 连接MongoDB
try:
    mongo_client = MongoClient(env.MONGO_URL)
# 如果连接失败
except errors.ConnectionFailure as cf_error:
    # 记录连接失败的具体原因
    log.error(f"连接MongoDB失败: {cf_error}")
except Exception as e:
    # 捕获其他所有异常
    log.error(f"发生未知错误: {e}")


class LPL:
    def __init__(self):
        self.url = "https://lpl.qq.com/web201612/data/LOL_MATCH2_MATCH_HOMEPAGE_BMATCH_LIST_{}.js"
        self.match_url = "https://open.tjstats.com/match-auth-app/open/v1/compound/matchDetail?matchId={}"
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
        self.cookies = {
            'tj_rp_did': '60013b4b18ce11efa938fe48ef6d951e',
        }
        self.proxies = env.PROXIES  # 代理
        self.mongo_client = MongoClient(env.MONGO_URL)
        self.mongo_db = self.mongo_client['league_of_legends']

        # 读取hero_list.json文件
        with open(os.path.join(project_root, 'data', 'json', 'hero_list.json'), 'r', encoding='utf-8') as f:
            self.hero_list = json.load(f)

    def get_seasonIds(self, seasons: Dict[str, str]) -> None:
        """
        单线程：获取season_id -> 赛季ID
        :params: seasons -> dict{str:str} 赛季ID映射
        :write_mongodb: collection -> league_of_legends.seasons
        """
        progress = WriteProgress(*page_columns)
        collection = self.mongo_db['seasons']
        collection.create_index([("season_id", ASCENDING)], unique=True)
        with progress:
            total_task = progress.add_task("[bold blue]获取[配置文件]season", total=len(seasons))
            for season_name, season_id in seasons.items():
                try:
                    collection.insert_one({"season_name": season_name, "season_id": season_id})
                except errors.DuplicateKeyError:
                    pass
                progress.update(total_task, advance=1)
        log.info(f"爬取完成丨共计[{len(seasons)}]LPL_season")

    def get_bMatchIds(self, seasons: Dict[str, str]) -> None:
        """
        多线程：获取bMatchId -> 赛程ID
        :params: seasons -> dict{season_id, season_name}
        :write_mongodb: collection -> league_of_legends.bmatchIds
        """
        progress = WriteProgress(*page_columns)
        collection = self.mongo_db['bMatchIds']
        collection.create_index([("bMatchId", ASCENDING)], unique=True)

        def fetch_season_data(_url: str):
            """
            单线程：获取bMatchId -> 赛程ID
            :params: url -> str: 请求url
            """
            try:
                if done_event.is_set():
                    return
                response = requests.get(url=_url, headers=self.headers, cookies=self.cookies, proxies=self.proxies)
                seasons_data = json.loads(response.text)
                if seasons_data.get('status') == "0":
                    msg = seasons_data.get('msg')
                    for match in msg:
                        record = {
                            'GameName': match.get('GameName'),
                            'bMatchName': match.get('bMatchName'),
                            'MatchDate': match.get('MatchDate'),
                            'bMatchId': match.get('bMatchId')
                        }
                        try:
                            collection.insert_one(record)
                        except errors.DuplicateKeyError:
                            pass
                    return len(msg)
            except Exception as _error:
                # 异常处理，可能需要重新尝试或记录错误
                log.error(f"爬取[LPL]bMatchId错误: {_error}")
                return 0

        with progress:
            total_task = progress.add_task(f"[bold blue]爬取[LPL]bMatchIds", total=len(seasons))
            bmatchId_count = 0
            with ThreadPoolExecutor(max_workers=8) as executor:
                urls = [self.url.format(season_id) for season_id in seasons.values()]
                futures = [executor.submit(fetch_season_data, url) for url in urls]
                # 使用as_completed来迭代已完成的Future，同时检查是否需要取消
                for future in as_completed(futures):
                    bmatchId_count += future.result()
                    progress.update(total_task, advance=1)
                    if done_event.is_set():
                        return
            log.info(f"爬取完成丨共计[{bmatchId_count}]LPL_bMatchId")

    def get_match_data(self, bmatch_ids: List[str]) -> None:
        """
        多线程：获取match_data -> 赛事数据
        :params: bmatch_ids -> list[bMatchId]
        :write_mongo: collection -> league_of_legends.match_data
        """
        progress = WriteProgress(*page_columns)
        collection = self.mongo_db['match_data']
        collection.create_index([("bMatchId", ASCENDING)], unique=True)

        def fetch_bMatchId_data(_url: str):
            """
            单线程：获取match_data -> 赛事数据
            :params: url -> str: 请求url
            """
            try:
                if done_event.is_set():
                    return
                response = requests.get(url=_url, headers=self.headers, cookies=self.cookies, proxies=self.proxies)
                match_data = json.loads(response.text)
                if match_data.get('success') is True:
                    msg = match_data.get('data')
                    try:
                        collection.insert_one(msg)
                    except errors.DuplicateKeyError:
                        pass
            except Exception as _error:
                log.error(f"爬取[LPL]match_data错误: {_error}")

        with progress:
            total_task = progress.add_task("[bold blue]爬取[LPL]match_data", total=len(bmatch_ids))
            with ThreadPoolExecutor(max_workers=8) as executor:
                urls = [self.match_url.format(bMatchId) for bMatchId in bmatch_ids]
                futures = [executor.submit(fetch_bMatchId_data, url) for url in urls]
                for future in futures:
                    future.result()  # 等待任务完成
                    progress.update(total_task, advance=1)  # 更新进度条
                    if done_event.is_set():
                        return  # 如果按下了 Ctrl+C，则立即退出循环
            log.info(f"爬取完成丨共计[{len(bmatch_ids)}]LPL_match_data")


class Wanplus:

    def __init__(self):
        self.start_url = "https://wanplus.cn/ajax/stats/list"
        self.team_url = "https://www.wanplus.cn/ajax/team/recent"
        self.match_url = "https://www.wanplus.cn/schedule/{}.html"
        self.bo_url = "https://www.wanplus.cn/ajax/matchdetail/{}"
        self.headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,ja;q=0.5,ko;q=0.4,fr;q=0.3',
            'Connection': 'keep-alive',
            'Referer': 'https://wanplus.cn/lol/team/5355',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
            'X-CSRF-Token': '752018433',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        self.cookies = {
            'wanplus_sid': 'ca52d80bd11453fc4fc546b14e3e98f8',
            'wp_pvid': '5502089598',
            'isShown': '1',
            'gameType': '2',
            'wanplus_token': 'a3dfb7eb6d517e564c5bc68fbd87a73e',
            'wanplus_storage': 'k6kitLSgOHmiKxm9zzbNnOnIWaHirSTBIMVggFTwtZu3sdPuw6bQGHM01YxlHuhRKLE9zwNsxT4hH5VdpJiAgc%2FHlne6yOZqoqvca0mIf91yhD7g%2BL9302dUxEe90vYZLal8hCRY4zwpuMuc4MZdQrwuTq9mek4GwA1adLPmx5uef4fvP41ZSYs',
            'wanplus_csrf': '_csrf_tk_684909569',
            'wp_info': 'ssid=s7961622084',
            'Hm_lvt_23f0107a6dc01005e1cee339f3e738e9': '1716268540,1716291295,1716355592,1716479272',
            'Hm_lpvt_23f0107a6dc01005e1cee339f3e738e9': '1716481776',
        }
        self.data = {
            '_gtk': '752018433',
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
            # 'totalPage': '15',
            # 'totalItems': '300',
            'egid': '0',
            '_gtk': '752018433',
        }
        self.proxies = env.PROXIES  # 代理
        self.mongo_client = MongoClient(env.MONGO_URL)
        self.mongo_db = self.mongo_client['wanplus']

    def get_eid(self):
        """
        获取赛季 ID
        :write_mongodb: collection -> wanplus:eids
        """
        progress = WriteProgress(*page_columns)
        collection = self.mongo_db['eids']
        with progress:
            response = requests.post(url=self.start_url, headers=self.headers, cookies=self.cookies, data=self.data, proxies=self.proxies)
            eid_dict = json.loads(response.text).get('eventList')
            total_task = progress.add_task(f"[bold blue]爬取[Wanplus]eids", total=len(eid_dict))
            for event in eid_dict.values():
                record = {
                    "name": event.get('name'),
                    "eid": event.get('eid')
                }
                collection.insert_one(record)
                progress.update(total_task, advance=1)
            log.info(f"爬取完成丨共计[{len(eid_dict)}]Wanplus_eid")

    def get_teamid(self, eid_list: List[str]) -> None:
        """
        获取队伍 ID
        :params: eid_list -> dict: 赛季 ID
        :write_mongodb: collection -> wanplus:teamids
        """
        progress = WriteProgress(*page_columns)
        collection = self.mongo_db['teamids']
        collection.create_index([("teamid", ASCENDING)], unique=True)

        def fetch_eid_data(_eid: str):
            """
            单线程：获取team_id -> 队伍ID
            :params: url -> str: 请求url
            """
            data = copy.deepcopy(self.data)
            try:
                if done_event.is_set():
                    return
                data['eid'] = _eid
                response = requests.post(url=self.start_url, headers=self.headers, cookies=self.cookies, data=data, proxies=self.proxies)
                if json.loads(response.text).get('msg') == "success":
                    data = json.loads(response.text).get('data')
                    for d in data:
                        teamid = d.get('teamid')
                        teamname = d.get('teamname')
                        teamid_dict = {
                            "teamid": teamid,
                            "teamname": teamname
                        }
                        try:
                            collection.insert_one(teamid_dict)
                        except errors.DuplicateKeyError:
                            pass  # 如果队伍 ID 已存在，跳过插入
                    return len(data)
            except Exception as _error:
                log.error(f"爬取[Wanplus]teamids错误: {_error}")
                return 0

        with progress:
            total_task = progress.add_task(f"[bold blue]爬取[Wanplus]丨teamids", total=len(eid_list))
            with ThreadPoolExecutor(max_workers=8) as executor:
                futures = [executor.submit(fetch_eid_data, eid) for eid in eid_list]
                for future in as_completed(futures):
                    future.result()
                    progress.update(total_task, advance=1)
                    if done_event.is_set():
                        return
            log.info(f"爬取完成丨共计[{collection.count_documents({})}]Wanplus_teamid")

    def get_scheduleids(self, teamid_list: List[str]) -> None:
        """
        获取赛程 ID
        :params: teamid_list -> dict: 队伍 ID
        :write_redis: hset -> wanplus:scheduleids: {teamname, scheduleid}
        """
        progress = WriteProgress(*page_columns)
        collection = self.mongo_db['scheduleids']
        collection.create_index([("scheduleid", ASCENDING)], unique=True)

        def fetch_team_data(_teamid: str):
            """
            单线程：获取赛程 ID
            :params: teamid -> str: 队伍 ID
            """
            params = copy.deepcopy(self.params)
            try:
                if done_event.is_set():
                    return
                params['teamId'] = _teamid
                response = requests.post(url=self.team_url, headers=self.headers, cookies=self.cookies, params=params, proxies=self.proxies)
                if json.loads(response.text).get('data') is not None:
                    data = json.loads(response.text).get('data')
                    for d in data:
                        teamname = f"{d.get('oneseedname')} vs {d.get('twoseedname')}丨{d.get('starttime')}"
                        scheduleid = d.get('scheduleid')
                        scheduleid_dict = {
                            "teamname": teamname,
                            "scheduleid": scheduleid
                        }
                        try:
                            collection.insert_one(scheduleid_dict)
                        except errors.DuplicateKeyError:
                            pass  # 如果赛程 ID 已存在，跳过插入
            except Exception as _error:
                log.error(f"爬取[Wanplus]scheduleids错误丨{_teamid}: {_error}")
                return 0

        with progress:
            total_task = progress.add_task(f"[bold blue]爬取[Wanplus]丨scheduleids", total=len(teamid_list))
            with ThreadPoolExecutor(max_workers=8) as executor:
                futures = [executor.submit(fetch_team_data, teamid) for teamid in teamid_list]
                for future in as_completed(futures):
                    future.result()
                    progress.update(total_task, advance=1)
                    if done_event.is_set():
                        return
            log.info(f"爬取完成丨共计[{collection.count_documents({})}]Wanplus_scheduleid")

    def get_boids(self, scheduleids_list: List[str]) -> None:
        """
        获取BO ID
        :params: scheduleids_list -> dict: 比赛 ID
        :write_mongodb: collection -> wanplus:boids
        """
        progress = WriteProgress(*page_columns)
        collection = self.mongo_db['boids']
        collection.create_index([("bo_id", ASCENDING)], unique=True)

        def fetch_scheduleid_data(_url: str):
            """
            单线程：获取BO ID
            :params: url -> str: 请求url
            """
            try:
                if done_event.is_set():
                    return
                response = requests.get(url=_url, headers=self.headers, cookies=self.cookies, proxies=self.proxies)
                soup = BeautifulSoup(response.text, 'html.parser')
                team_detail_ov = soup.find('ul', attrs={'class': 'team-detail ov'})
                team_left = team_detail_ov.find('li', attrs={'class': 'team-left'}).find('a').find('span').text
                bo_time = team_detail_ov.find('span', attrs={'class': 'time'}).text
                team_right = team_detail_ov.find('li', attrs={'class': 'team-right tr'}).find('a').find('span').text
                game_div = soup.find('div', attrs={'class': 'game'})
                try:
                    data_matchid = game_div.find_all('a')
                    for match_id in data_matchid:
                        bo_count = match_id.text[-1]
                        bo_detail = f"{bo_time}丨{team_left} vs {team_right}丨BO{bo_count}"
                        bo_id = match_id.get('data-matchid')
                        bo_dict = {
                            "bo_detail": bo_detail,
                            "bo_id": bo_id,
                        }
                        try:
                            collection.insert_one(bo_dict)
                        except errors.DuplicateKeyError:
                            pass
                except AttributeError:
                    pass
            except Exception as _error:
                log.error(f"爬取[Wanplus]boids错误: {_error}")
                return 0

        with progress:
            total_task = progress.add_task(f"[bold blue]爬取[Wanplus]丨boids", total=len(scheduleids_list))
            with ThreadPoolExecutor(max_workers=50) as executor:
                urls = [self.match_url.format(scheduleid) for scheduleid in scheduleids_list]
                futures = [executor.submit(fetch_scheduleid_data, url) for url in urls]
                for future in as_completed(futures):
                    future.result()
                    progress.update(total_task, advance=1)
                    if done_event.is_set():
                        return
            log.info(f"爬取完成丨共计[{collection.count_documents({})}]Wanplus_boid")

    def get_match_data(self, boids_list: List[str]) -> None:
        """
        并发获取比赛数据并显示进度
        :params: boids_dict -> dict: 比赛 ID
        :write_redis: hset -> wanplus:match_data: {bo_id, bo_data}
        """
        progress = WriteProgress(*page_columns)
        collection = self.mongo_db['match_data']
        collection.create_index([("boid", ASCENDING)], unique=True)

        def fetch_boid_data(_url: str):
            """
            单线程：获取比赛数据
            :params: boid -> str: 比赛 ID
            """
            try:
                if done_event.is_set():
                    return
                response = requests.get(url=_url, headers=self.headers, cookies=self.cookies, params={'_gtk': '752018433'})
                if json.loads(response.text).get('msg') == 'success':
                    bo_id = _url.split('/')[-1]
                    match_data = json.loads(response.text).get('data')
                    record = {
                        "boid": bo_id,
                        "match_data": match_data
                    }
                    try:
                        collection.insert_one(record)
                    except errors.DuplicateKeyError:
                        pass
            except Exception as _error:
                log.error(f"爬取[Wanplus]match_data错误: {_error}")
                return 0

        with progress:
            total_task = progress.add_task(f"[bold blue]爬取[Wanplus]丨match_data", total=len(boids_list))
            with ThreadPoolExecutor(max_workers=10) as executor:
                urls = [self.bo_url.format(boid) for boid in boids_list]
                futures = [executor.submit(fetch_boid_data, url) for url in urls]
                for future in as_completed(futures):
                    future.result()
                    progress.update(total_task, advance=1)
                    if done_event.is_set():
                        return
            log.info(f"爬取完成丨共计[{collection.count_documents({})}]Wanplus")


def main():
    # LPL
    lpl = LPL()

    seasons = copy.deepcopy(env.SEASONS)
    lpl.get_seasonIds(seasons)

    lpl.get_bMatchIds(seasons)

    bMatchIds_dict = list(lpl.mongo_db['bMatchIds'].find({}, {'_id': 0, 'bMatchId': 1}))
    bMatchIds = [bMatchId['bMatchId'] for bMatchId in bMatchIds_dict]
    lpl.get_match_data(bMatchIds)

    # Wanplus
    wanplus = Wanplus()

    wanplus.get_eid()

    eids_list = [eid['eid'] for eid in wanplus.mongo_db['eids'].find({}, {'_id': 0, 'eid': 1})]
    wanplus.get_teamid(eids_list)

    teamid_list = [team_id['teamid'] for team_id in wanplus.mongo_db['teamids'].find({}, {'_id': 0, 'teamid': 1})]
    wanplus.get_scheduleids(teamid_list)

    scheduleid_list = [scheduleid['scheduleid'] for scheduleid in wanplus.mongo_db['scheduleids'].find({}, {'_id': 0, 'scheduleid': 1})]
    wanplus.get_boids(scheduleid_list)

    boid_list = [boid['bo_id'] for boid in wanplus.mongo_db['boids'].find({}, {'_id': 0, 'bo_id': 1})]
    wanplus.get_match_data(boid_list)


if __name__ == '__main__':
    main()
