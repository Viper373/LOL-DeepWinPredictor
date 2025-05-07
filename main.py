# -*- coding:utf-8 -*-
# @Software       :PyCharm
# @Project        :LOL-DeepWinPredictor
# @Path           :/
# @FileName       :main.py
# @Time           :2025/4/21 23:38
# @Author         :Viper373
# @GitHub         :https://github.com/Viper373
# @Home           :https://viper3.top
# @Blog           :https://blog.viper3.top


import asyncio
import copy
import traceback

from Data_CrawlProcess import env
from Data_CrawlProcess.Concat import Concat
from Data_CrawlProcess.LPL import LPL
from Data_CrawlProcess.Other import Other
from Data_CrawlProcess.Process import Process
from Data_CrawlProcess.Wanplus import Wanplus
from tool_utils.log_utils import RichLogger
from tool_utils.mysql_utils import MySQLUtils
from tool_utils.progress_utils import RichProgressUtils

rich_logger = RichLogger()
mysql = MySQLUtils()
process = Process()


async def main():
    rich_progress = RichProgressUtils()
    rich_progress.start()
    try:
        # Other流程
        other = Other(rich_progress=rich_progress)
        other.main()

        # LPL流程
        lpl = LPL(rich_progress=rich_progress)
        seasons = copy.deepcopy(env.SEASONS)
        await lpl.main(
            env.LPL_DB,
            env.LPL_COL_SEASON,
            env.LPL_COL_BMATCH,
            env.LPL_COL_MATCH,
            seasons
        )

        # Wanplus流程
        wanplus = Wanplus(rich_progress=rich_progress)
        await wanplus.main(
            env.WANPLUS_DB,
            env.WANPLUS_COL_EID,
            env.WANPLUS_COL_TEAM,
            env.WANPLUS_COL_SCHEDULE,
            env.WANPLUS_COL_BOID,
            env.WANPLUS_COL_MATCH,
        )

        # Concat流程
        json_data = process.read_win_rate()
        concat = Concat(rich_progress=rich_progress)
        await concat.main(
            env.DB1,
            env.COL1,
            env.DB2,
            env.COL2,
            env.TARGET_DB,
            env.TARGET_COL,
            json_data
        )

        rich_logger.info("全部流程执行完毕！")
    except Exception as e:
        rich_logger.error(f"主流程异常: {str(e)}")
        traceback.print_exc()
    finally:
        rich_progress.stop()


if __name__ == '__main__':
    asyncio.run(main())
