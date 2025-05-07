# -*- coding:utf-8 -*-
# @Software       :PyCharm
# @Project        :LOL-DeepWinPredictor
# @Path           :/tool_utils
# @FileName       :mysql_utils.py
# @Time           :2025/4/23 14:45
# @Author         :Viper373
# @GitHub         :https://github.com/Viper373
# @Home           :https://viper3.top
# @Blog           :https://blog.viper3.top

from typing import Any, Dict, List, Optional, Tuple, Union

import orjson
import pymysql

from Data_CrawlProcess.env import MYSQL_CONFIG
from tool_utils.log_utils import RichLogger

rich_logger = RichLogger()


class Connect:
    def __enter__(self):
        # 从环境变量读取数据库配置
        self.conn = pymysql.connect(
            host=MYSQL_CONFIG.get("MYSQL_HOST"),
            port=int(MYSQL_CONFIG.get("MYSQL_PORT")),
            user=MYSQL_CONFIG.get("MYSQL_USER"),
            password=MYSQL_CONFIG.get("MYSQL_PASSWORD"),
            database=MYSQL_CONFIG.get("MYSQL_DATABASE"),
            charset=MYSQL_CONFIG.get("MYSQL_CHARSET"),
        )
        self.cur = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 标准with上下文管理器写法
        try:
            self.cur.close()
        except Exception as e:
            rich_logger.error(f"关闭游标失败: {e}")
        try:
            self.conn.close()
        except Exception as e:
            rich_logger.error(f"关闭连接失败: {e}")


class DBHelper:
    """
    通用数据库操作工具类，所有配置从env环境变量获取。
    支持异常捕获和日志输出，所有方法为类方法，便于继承和复用。
    """

    @classmethod
    def find(cls, sql: str) -> Optional[Tuple]:
        """无参数查询"""
        try:
            with Connect() as db:
                db.cur.execute(sql)
                result = db.cur.fetchall()
                return result
        except Exception as e:
            rich_logger.error(f"find 执行SQL失败: {sql}, 错误: {e}")
            return None

    @classmethod
    def find_one(cls, sql: str) -> Optional[Any]:
        """无参数查询，返回单条"""
        try:
            with Connect() as db:
                db.cur.execute(sql)
                result = db.cur.fetchone()
                return result
        except Exception as e:
            rich_logger.error(f"find_one 执行SQL失败: {sql}, 错误: {e}")
            return None

    @classmethod
    def find_para(cls, sql: str, tup: Union[Tuple, List]) -> Optional[Tuple]:
        """有参数查询"""
        try:
            with Connect() as db:
                db.cur.execute(sql, tup)
                result = db.cur.fetchall()
                return result
        except Exception as e:
            rich_logger.error(f"find_para 执行SQL失败: {sql}, 参数: {tup}, 错误: {e}")
            return None

    @classmethod
    def modify(cls, sql: str) -> None:
        """无参增删改"""
        try:
            with Connect() as db:
                db.cur.execute(sql)
                db.conn.commit()
        except Exception as e:
            rich_logger.error(f"modify 执行SQL失败: {sql}, 错误: {e}")

    @classmethod
    def modify_para(cls, sql: str, tup: Union[Tuple, List]) -> None:
        """有参增删改"""
        try:
            with Connect() as db:
                db.cur.execute(sql, tup)
                db.conn.commit()
        except Exception as e:
            rich_logger.error(f"modify_para 执行SQL失败: {sql}, 参数: {tup}, 错误: {e}")

    @classmethod
    def modify_many(cls, sql: str, data_list: List[Union[Tuple, List]]) -> None:
        """批量增删改"""
        if not data_list:
            return
        try:
            with Connect() as db:
                db.cur.executemany(sql, data_list)
                db.conn.commit()
        except Exception as e:
            rich_logger.error(
                f"modify_many 执行SQL失败: {sql}, 数据量: {len(data_list)}, 错误: {e}"
            )


class MySQLUtils:
    """
    MySQL数据库操作工具类
    """

    def __init__(self):
        self.db_helper = DBHelper
        self.init_database()

    def insert_hero_win_rate(self, data: List) -> None:
        """
        插入或更新英雄胜率数据（有则更新，无则插入）
        :param data: 英雄胜率数据列表
        """
        insert_sql = "REPLACE INTO hero_win_rates (hero_id, hero_name, TOP, JUN, MID, ADC, SUP) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        self.db_helper.modify_many(insert_sql, data)

    def select_hero_win_rate(self) -> Optional[Dict[str, Any]]:
        """
        查询英雄胜率数据
        """
        select_sql = 'SELECT hero_id, hero_name, TOP, JUN, MID, ADC, SUP FROM hero_win_rates'
        return self.db_helper.find(select_sql)

    def update_hero_counter(self, hero_id: int, counter_lane_dict) -> None:
        """
        更新英雄克制关系（分路追加/更新，不整体覆盖）
        :param hero_id: 英雄ID
        :param counter_lane_dict: 分路->counter英雄id列表的有序字典
        :return: None
        """
        select_sql = "SELECT Counter FROM hero_win_rates WHERE hero_id = %s"
        update_sql = "UPDATE hero_win_rates SET Counter = %s WHERE hero_id = %s"
        try:
            # 查询原有Counter
            old = self.db_helper.find_para(select_sql, (hero_id,))
            if old and old[0] and old[0][0]:
                try:
                    import orjson
                    old_dict = orjson.loads(old[0][0].encode("utf-8"))
                except Exception:
                    old_dict = {}
            else:
                old_dict = {}
            # 合并（新分路覆盖旧分路，其余保留）
            merged = dict(old_dict)
            merged.update(counter_lane_dict)
            # 保证顺序
            from collections import OrderedDict
            lane_order = ["TOP", "JUN", "MID", "ADC", "SUP"]
            ordered_merged = OrderedDict()
            for lane in lane_order:
                if lane in merged:
                    ordered_merged[lane] = merged[lane]
            import orjson
            counter_str = orjson.dumps(ordered_merged).decode("utf-8")
            self.db_helper.modify_para(update_sql, (counter_str, hero_id))
        except Exception as e:
            rich_logger.error(f"update_hero_counter 追加/更新失败: {e}")

    def init_database(self) -> None:
        """
        初始化数据库
        """
        # 创建表
        create_table_sql = """
                           CREATE TABLE IF NOT EXISTS hero_win_rates
                           (
                               hero_id   INT PRIMARY KEY,
                               hero_name VARCHAR(255),
                               TOP       FLOAT,
                               JUN       FLOAT,
                               MID       FLOAT,
                               ADC       FLOAT,
                               SUP       FLOAT,
                               Counter   TEXT
                           )
                           """
        self.db_helper.modify(create_table_sql)
