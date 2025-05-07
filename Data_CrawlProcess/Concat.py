# -*- coding:utf-8 -*-
# @Software       :PyCharm
# @Project        :LOL-DeepWinPredictor
# @Path           :/Data_CrawlProcess
# @FileName       :Concat.py
# @Time           :2025/5/5 01:52
# @Author         :Viper373
# @GitHub         :https://github.com/Viper373
# @Home           :https://viper3.top
# @Blog           :https://blog.viper3.top

import asyncio

from Data_CrawlProcess.Process import Process
from tool_utils.log_utils import RichLogger
from tool_utils.mongo_utils import MongoUtils

process = Process()
mongo_utils = MongoUtils()
rich_logger = RichLogger()


class Concat:
    def __init__(self, rich_progress=None):
        """
        Concat类初始化方法。
        :param rich_progress: RichProgressUtils实例（用于全局进度条）
        :return: None
        """
        self.rich_progress = rich_progress

    async def concat_db(self, db1: str, col1: str, db2: str, col2: str, target_db: str, target_col: str, chunk_size: int = 1000, consumer_num: int = 1):
        """
        合并两个MongoDB集合到一个目标集合（异步队列，边处理边写入并实时推进进度条）
        :param db1: 源数据库1
        :param col1: 源集合1
        :param db2: 源数据库2
        :param col2: 源集合2
        :param target_db: 目标数据库
        :param target_col: 目标集合
        :param chunk_size: 每批写入数量
        :param consumer_num: 消费者数量
        :return: None
        """
        mongo_utils.use_db(db1)
        lpl_col = mongo_utils.use_collection(col1)
        mongo_utils.use_db(db2)
        wanplus_col = mongo_utils.use_collection(col2)
        mongo_utils.use_db(target_db)
        target_collection = mongo_utils.use_collection(target_col)
        total_count = lpl_col.count_documents({}) + wanplus_col.count_documents({})
        total_task = self.rich_progress.add_task("[Concat]合并LPL与Wanplus", total=total_count)
        lpl_docs = list(lpl_col.find({}, {'_id': 0}))
        wanplus_docs = list(wanplus_col.find({}, {'_id': 0}))
        all_docs = lpl_docs + wanplus_docs
        queue = asyncio.Queue(maxsize=10)

        async def producer():
            for i in range(0, len(all_docs), chunk_size):
                await queue.put(all_docs[i:i + chunk_size])
            for _ in range(consumer_num):
                await queue.put(None)  # 结束信号

        async def consumer():
            while True:
                chunk = await queue.get()
                if chunk is None:
                    break
                await asyncio.to_thread(target_collection.insert_many, chunk)
                await asyncio.to_thread(self.rich_progress.advance, total_task, len(chunk))

        await asyncio.gather(
            producer(),
            *(consumer() for _ in range(consumer_num))
        )
        rich_logger.info(f"[Concat] 合并完成丨共计[{total_count}]moba_lol_data")

    async def main(self, db1: str, col1: str, db2: str, col2: str, target_db: str, target_col: str, json_data: dict) -> None:
        """
        主流程方法，依次异步执行concat_db_async和append_counter_async
        :param db1: 源数据库1
        :param col1: 源集合1
        :param db2: 源数据库2
        :param col2: 源集合2
        :param target_db: 目标数据库
        :param target_col: 目标集合
        :param json_data: 包含counter信息的json数据
        """
        await self.concat_db(db1, col1, db2, col2, target_db, target_col)
        rich_logger.info("[Concat] main流程执行完毕")
