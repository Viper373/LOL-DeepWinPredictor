# -*- coding:utf-8 -*-
# @Project        :LPL
# @FileName       :collecting_hero.py
# @Time           :2025/3/5 00:12
# @Software       :PyCharm
# @Author         :Viper373
# @Index          :https://viper3.top
# @Blog           :https://blog.viper3.top

import os
import sys
import re
import requests
from lxml import etree
import json
from rich.logging import RichHandler
from rich.progress import Progress, BarColumn, SpinnerColumn, TimeRemainingColumn, TimeElapsedColumn, TransferSpeedColumn  # rich进度条
from rich.panel import Panel  # rich面板
from rich.box import DOUBLE  # rich面板样式
import logging  # 日志
import signal  # 信号处理
from threading import Event

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


class HeroData:

    def __init__(self):
        self.hero_list_url = "https://game.gtimg.cn/images/lol/act/img/js/heroList/hero_list.js"
        self.logo_url_template = "https://game.gtimg.cn/images/lol/act/img/champion/{alias}.png"  # 官方Logo URL模板

    def get_hero_list(self):
        """
        获取英雄列表并保存为格式化的JSON文件
        :return: None
        """
        try:
            response = requests.get(self.hero_list_url)

            if response.status_code != 200:
                log.error(f"请求失败，状态码: {response.status_code}")
                return

            try:
                # 直接解析 JSON 数据（自动处理 Unicode 转义）
                hero_data = response.json()
            except json.JSONDecodeError:
                log.error("响应内容不是有效的 JSON 格式")
                return

            # 保存格式化的 JSON 文件
            save_path = os.path.join(project_root, 'data', 'json', 'hero_list.json')
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(hero_data, f, ensure_ascii=False, indent=4)
            log.info(f"{hero_data.get('fileName')}保存完成 丨 version：{hero_data.get('version')} 丨 {hero_data.get('fileTime')}")
        except Exception as _error:
            log.error(f"获取英雄列表失败: {_error}")

    def generate_logo_data(self):
        """
        根据hero_list.json生成logo数据
        :return: None
        """
        hero_list_json = os.path.join(project_root, 'data', 'json', 'hero_list.json')
        save_path = os.path.join(project_root, 'data', 'json', 'hero_logo.json')
        try:
            # 读取英雄列表
            with open(hero_list_json, 'r', encoding='utf-8') as f:
                hero_list = json.load(f)

            # 生成Logo数据
            logo_data = []
            for hero in hero_list.get('hero'):
                try:
                    # 关键字段校验
                    hero_id = str(hero['heroId'])
                    name = hero['name']
                    alias = hero['alias']

                    # 生成官方Logo URL
                    logo_url = self.logo_url_template.format(alias=alias)

                    logo_data.append({
                        "heroId": hero_id,
                        "name": name,
                        "heroLogo": logo_url
                    })
                except KeyError as e:
                    log.warning(f"字段缺失: {e} | 英雄数据: {hero}")
                except Exception as e:
                    log.error(f"处理英雄异常: {str(e)} | 数据: {hero}")

            # 保存Logo数据
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(logo_data, f, ensure_ascii=False, indent=4)

            log.info(f"成功生成 {len(logo_data)} 条Logo数据")
            return True

        except FileNotFoundError:
            log.error("hero_list.json文件不存在")
        except json.JSONDecodeError:
            log.error("hero_list.json文件格式错误")
        except Exception as e:
            log.error(f"生成Logo数据失败: {str(e)}")
        return False


def main():
    hero_data = HeroData()
    # hero_data.get_hero_list()
    hero_data.generate_logo_data()


if __name__ == '__main__':
    main()
