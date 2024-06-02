import os
import sys
import csv
import json
import math

from rich.logging import RichHandler
from rich.progress import Progress, BarColumn, SpinnerColumn, TimeRemainingColumn, TimeElapsedColumn, TransferSpeedColumn  # rich进度条
from rich.panel import Panel  # rich面板
from rich.box import DOUBLE  # rich面板样式
import logging  # 日志
import pymongo
from pymongo import MongoClient  # MongoDB
import env  # 配置文件

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

script_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目的根目录
project_root = os.path.abspath(os.path.join(script_dir, os.pardir))
if project_root not in sys.path:
    sys.path.append(project_root)

# rich日志处理器配置
logging.basicConfig(
    level="INFO",
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    datefmt="[%Y-%m-%d %H:%M:%S]",
    handlers=[
        # 日志控制台处理器
        RichHandler(rich_tracebacks=True),
        # 日志文件处理器
        logging.FileHandler(os.path.join(project_root, 'log', 'lol.log'), mode='a', encoding='utf-8'),
    ],
)
log = logging.getLogger("rich")  # 日志对象


class WriteProgress(Progress):
    def get_renderables(self):
        yield Panel(self.make_tasks_table(self.tasks), box=DOUBLE)


class LPL:
    def __init__(self):
        self.mongo_client = MongoClient(env.MONGO_URL)['league_of_legends']

    @staticmethod
    def read_win_rate():
        with open(os.path.join(project_root, 'data', 'json', 'hero_win_rate.json'), "r", encoding="utf-8") as f:
            data = json.loads(f.read())['data']
            hero_win_rates = {}
            for d in data:
                heroId = d["champion"]["id"]
                for p in d["champion"]["positions"]:
                    playerLocation = p["name"][:3]
                    winRate = p["stats"]["win_rate"]
                    hero_win_rates[f'{heroId}{playerLocation}'] = winRate
            return hero_win_rates

    def process_lpl_data(self, org_col_name, target_col_name, batch_size=100):
        """
        结构化数据，采用分批处理方式
        :params: collection_name -> MongoDB集合名称
        :params: batch_size -> 每批次处理的数据量，默认为100
        :write_mongoDB collection_name -> league_of_legends.structured_data
        """
        progress = WriteProgress(*page_columns)
        hero_win_rates = self.read_win_rate()
        # 获取mongoDB集合数据
        match_data = self.mongo_client[org_col_name]

        with progress:
            total_batches = math.ceil(match_data.count_documents({}) / batch_size)
            total_task = progress.add_task(f"[bold blue]结构化[LPL]match_data", total=match_data.count_documents({}))

            for batch_num in range(total_batches):
                skip = batch_num * batch_size
                batch_match_data = match_data.find({}, {'_id': 0}).skip(skip).limit(batch_size)
                for match in batch_match_data:
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
                            count = 1
                            for player in playerInfos:
                                playerLocation = "ADC" if player["playerLocation"] == "BOT" else player["playerLocation"]
                                heroId, heroTitle, heroName = player["heroId"], player["heroTitle"], player["heroName"]
                                heroWinRate = hero_win_rates.get(f"{heroId}{playerLocation}", 0.50)
                                processed_data.update({
                                    f"{team_po}{count}playerLocation": playerLocation,
                                    f"{team_po}{count}heroId": heroId,
                                    f"{team_po}{count}heroName": f"{heroTitle}-{heroName}",
                                    f"{team_po}{count}heroWinRate": heroWinRate,

                                })
                                count += 1
                            team_po = "B"
                    self.mongo_client[target_col_name].insert_one(processed_data)
                    progress.update(total_task, advance=1)
            log.info(f"本次共计结构化[{match_data.count_documents({})}]LPL_match_data")


class Wanplus:
    def __init__(self):
        self.mongo_client = MongoClient(env.MONGO_URL)['wanplus']

    @staticmethod
    def read_win_rate():
        with open("../data/json/hero_win_rate.json", "r", encoding="utf-8") as f:
            data = json.loads(f.read())['data']
            hero_win_rates = {}
            for d in data:
                heroId = d["champion"]["id"]
                for p in d["champion"]["positions"]:
                    playerLocation = p["name"][:3]
                    winRate = p["stats"]["win_rate"]
                    hero_win_rates[f'{heroId}{playerLocation}'] = winRate
            return hero_win_rates

    def process_wanplus_data(self, org_col_name, target_col_name, batch_size=100):
        """
        结构化数据，采用分批处理方式
        :params: collection_name -> MongoDB集合名称
        :params: batch_size -> 每批次处理的数据量，默认为100
        :write_mongoDB collection_name -> league_of_legends.structured_data
        """
        progress = WriteProgress(*page_columns)
        hero_win_rates = self.read_win_rate()
        po_dict = {
            "1": "TOP",
            "2": "JUN",
            "3": "MID",
            "4": "ADC",
            "5": "SUP",
        }
        # 获取mongoDB集合数据
        match_data = self.mongo_client[org_col_name]

        def optimize_delete():
            bulk_operations = []
            for document in match_data.find():
                _match_data = document.get('match_data', {})
                _plList = _match_data.get('plList', [])
                if len(_plList) > 0 and len(_plList[0]) == 0:
                    bulk_operations.append(pymongo.DeleteOne({"_id": document["_id"]}))

                # Execute batch if it reaches a certain size to avoid memory overload
                if len(bulk_operations) >= 1000:
                    match_data.bulk_write(bulk_operations)
                    bulk_operations = []

            # Execute any remaining operations in bulk
            if bulk_operations:
                match_data.bulk_write(bulk_operations)

        # optimize_delete()
        with progress:
            total_batches = math.ceil(match_data.count_documents({}) / batch_size)
            total_task = progress.add_task(f"[bold blue]结构化[Wanplus]match_data", total=match_data.count_documents({}))

            for batch_num in range(total_batches):
                skip = batch_num * batch_size
                batch_match_data = match_data.find({}, {'_id': 0}).skip(skip).limit(batch_size)
                for match in batch_match_data:
                    processed_data = {
                        "boid": match['boid'],
                    }
                    new_match = match["match_data"]
                    plList = new_match["plList"]
                    info = new_match["info"]
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
                        for idx, p in pl.items():
                            for _id in po_dict:
                                playerLocation = po_dict.get(idx)
                            try:
                                heroId, heroName = p["cpheroid"], p["heroname"]
                            except Exception:
                                isbreak = True
                            heroWinRate = hero_win_rates.get(f"{heroId}{playerLocation}", 0.50)
                            processed_data.update({
                                f"{team_po}{idx}playerLocation": playerLocation,
                                f"{team_po}{idx}heroId": heroId,
                                f"{team_po}{idx}heroName": f"{heroName}",
                                f"{team_po}{idx}heroWinRate": heroWinRate,
                            })
                        team_po = "B"
                    if not isbreak:
                        self.mongo_client[target_col_name].insert_one(processed_data)
                    progress.update(total_task, advance=1)
            self.mongo_client[target_col_name].delete_many({"A1heroId": None})
            log.info(f"结构化完成丨共计[{match_data.count_documents({})}]Wanplus_match_data")


class Concat:
    def __init__(self):
        self.mongo_client = MongoClient(env.MONGO_URL)

    @staticmethod
    def read_csv(csv_file):
        csv_data = []
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                csv_data.append(row)
        return csv_data

    @staticmethod
    def read_hero_list(json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            hero_list = json.load(f)
            heroId = [int(hero['heroId']) for hero in hero_list]
            hero_name = [hero['name'] for hero in hero_list]
            hero_title = [hero['title'] for hero in hero_list]
            hero_dict = {
                "heroId": heroId,
                "heroName": f"{hero_name}-{hero_title}",
            }
        return hero_dict

    @staticmethod
    def read_win_rate(json_file):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.loads(f.read())['data']
            hero_win_rates = {}
            for d in data:
                heroId = d["champion"]["id"]
                for p in d["champion"]["positions"]:
                    playerLocation = p["name"][:3]
                    winRate = p["stats"]["win_rate"]
                    hero_win_rates[f'{heroId}{playerLocation}'] = winRate
            return hero_win_rates

    def concat_db(self, db1, col1, db2, col2, target_db, target_col):
        """
        将两个MongoDB集合合并为一个
        :params: collection_name1 -> MongoDB集合名称1
        :params: collection_name2 -> MongoDB集合名称2
        :params: target_collection_name -> 目标MongoDB集合名称
        :write_mongoDB collection_name -> moba.lol
        """
        progress = WriteProgress(*page_columns)
        lpl_match_data = self.mongo_client[db1][col1]
        wanplus_match_data = self.mongo_client[db2][col2]
        total_count = lpl_match_data.count_documents({}) + wanplus_match_data.count_documents({})
        with progress:
            total_task = progress.add_task(f"[bold blue]结构化[moba]lol_data", total=total_count)
            for match in lpl_match_data.find({}, {'_id': 0}):
                processed_data = match
                self.mongo_client[target_db][target_col].insert_one(processed_data)
                progress.update(total_task, advance=1)
            for match in wanplus_match_data.find({}, {'_id': 0}):
                processed_data = match
                self.mongo_client[target_db][target_col].insert_one(processed_data)
                progress.update(total_task, advance=1)
            log.info(f"合并完成丨共计[{lpl_match_data.count_documents({}) + wanplus_match_data.count_documents({})}]moba_lol_data")

    def append_counter(self, json_data):
        # 连接到MongoDB数据库
        db = self.mongo_client["moba"]
        collection = db["lol"]
        progress = WriteProgress(*page_columns)
        # 读取所有数据
        documents = collection.find()
        with progress:
            total_task = progress.add_task(f"[bold blue]新增克制关系[moba]lol", total=collection.count_documents({}))
            # 遍历每个文档
            for doc in documents:
                # 提取所需的字段
                doc_id = doc["_id"]
                team_po = ["A", "B"]
                for po in team_po:
                    for j in range(1, 6):
                        hero_id = doc[f"{po}{j}heroId"]
                        for data_item in json_data.get('data'):
                            # 根据heroId查找对应的counterId
                            if data_item["id"] == hero_id:
                                counter_ids = [counter["champion_id"] for counter in data_item["positionCounters"]]
                                update_data = {f"{po}{j}heroCounter": counter_ids}
                                # 更新文档
                                collection.update_one({"_id": doc_id}, {"$set": update_data})
                            else:
                                continue
                progress.update(total_task, advance=1)
            log.info(f"新增克制关系完成丨共计[{collection.count_documents({})}]moba_lol_data")
        # 关闭数据库连接
        self.mongo_client.close()


def main():
    lpl = LPL()
    lpl.process_lpl_data("match_data", "structured_data")

    wanplus = Wanplus()
    wanplus.process_wanplus_data("match_data", "structured_data")

    concat = Concat()
    concat.concat_db(
        "league_of_legends", "structured_data",
        "wanplus", "structured_data",
        "moba", "lol"
    )
    with open(os.path.join(project_root, 'data', 'json', 'hero_win_rate.json'), "r", encoding="utf-8") as f:
        json_data = json.load(f)
    concat.append_counter(json_data)


if __name__ == '__main__':
    main()
