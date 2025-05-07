# -*- coding: utf-8 -*-
# @Project   :td_gsc_scraper
# @FileName  :string_utils.py
# @Time      :2024/10/11 10:45
# @Author    :Zhangjinzhao
# @Software  :PyCharm

import hashlib
import re

from tool_utils.log_utils import RichLogger

rich_logger = RichLogger()


class StringUtils:

    def __init__(self):
        pass

    @staticmethod
    def md5_encode(str_data: str) -> str:
        """
        对字符串进行MD5加密。
        :param str_data: 需要加密的字符串
        :return: 加密后的字符串
        """
        md5_value = hashlib.md5()
        md5_value.update(str_data.encode('utf-8'))
        return md5_value.hexdigest()

    @staticmethod
    def extract_video_download_url(response_text):
        """
        使用正则表达式从响应文本中提取视频下载链接。
        :param response_text: 包含视频信息的JSON格式文本
        :return: 第一个videoUrl的值或None
        """
        response_text_cleaned = re.sub(r'\\/', '/', response_text)
        try:
            video_url = re.findall(r'"videoUrl":"(.*?)"', response_text_cleaned)[-2]
            return video_url
        except Exception as e:
            rich_logger.exception(f"提取视频链接时发生错误: {e}")
        return None
