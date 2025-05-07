# -*- coding: utf-8 -*-
# @Project   :td_gsc_scraper
# @FileName  :api_utils.py
# @Time      :2024/10/12 10:34
# @Author    :Zhangjinzhao
# @Software  :PyCharm

import asyncio
import base64
import mimetypes
import os
import time

import aiohttp
import orjson
import requests
from dotenv import load_dotenv
from requests.exceptions import RequestException

from Data_CrawlProcess.env import ORJSON_OPTS
from tool_utils.log_utils import RichLogger
from tool_utils.proxy_utils import ProxyUtils

rich_logger = RichLogger()
proxy_utils = ProxyUtils()
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(root_dir, '.env'))


class APIUtils:
    def __init__(self):
        pass

    @staticmethod
    def requests_retry(url, headers=None, cookies=None, params=None, proxies=None, retries=5, delay=2, timeout=30):
        """
        发起请求并加入重试机制。
        :param url: 请求的URL
        :param headers: 请求头
        :param cookies: 请求Cookies
        :param params: URL参数
        :param proxies: 代理
        :param retries: 最大重试次数
        :param delay: 每次重试的间隔时间（秒）
        :param timeout: 请求超时时间（秒）
        :return: requests.Response对象 或 None
        """
        attempt = 0
        while attempt < retries:
            try:
                response = requests.get(url, headers=headers, cookies=cookies, params=params, proxies=proxies, timeout=timeout)
                if response.status_code == 200:
                    return response
                else:
                    rich_logger.error(f"请求失败: {response.status_code} | URL: {url}")
            except RequestException as e:
                rich_logger.error(f"请求出错: {e} | 尝试 {attempt + 1}/{retries} 次，URL: {url}")

            attempt += 1
            if attempt < retries:
                rich_logger.info(f"重试请求，等待 {delay} 秒... (尝试 {attempt + 1}/{retries})")
                time.sleep(delay)

        rich_logger.error(f"请求失败，已达到最大重试次数: {url}")
        return None


class GitHubUtils:
    def __init__(self):
        self.token = os.getenv("GH_TOKEN")
        self.repo_owner = os.getenv("GH_OWNER")
        self.repo_name = os.getenv("GH_REPO")
        self.api_base = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/"
        self.gh_headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json"
        }
        self.ph_headers = {
            'accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,ja;q=0.5,ko;q=0.4,fr;q=0.3',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0',
        }

    async def async_upload_from_url(self, session, image_url, target_path, retries=3, delay=2):
        """
        异步从URL下载图片并上传到GitHub
        """
        attempt = 0
        while attempt < retries:
            try:
                # 异步下载图片
                async with session.get(image_url, headers=self.ph_headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        content = await response.read()
                        content_type = response.headers.get('Content-Type')
                        file_extension = mimetypes.guess_extension(content_type) or '.jpg'
                        # 确保 target_path 使用正确的扩展名
                        if not target_path.endswith(file_extension):
                            target_path = target_path.rsplit('.', 1)[0] + file_extension
                        break
                    else:
                        raise Exception(f"下载图片失败，状态码: {response.status}")
            except Exception as e:
                attempt += 1
                if attempt < retries:
                    rich_logger.error(f"下载失败: {e}，尝试 {attempt}/{retries}，等待 {delay} 秒后重试...")
                    await asyncio.sleep(delay)
                else:
                    rich_logger.error(f"下载图片失败，已达到最大重试次数: {image_url}")
                    return False

        # 将图片内容编码为base64
        content_b64 = base64.b64encode(content).decode()

        # 准备GitHub API请求数据
        data = {
            "message": f"Upload {target_path}",
            "content": content_b64,
            "sha": await self._async_get_existing_sha(session, target_path),
            "committer": {"name": "Viper373", "email": "2020311228@bipt.edu.cn"}
        }

        # 异步上传到GitHub
        async with session.put(
                f"{self.api_base}{target_path}",
                headers=self.gh_headers,
                data=orjson.dumps(data).decode('utf-8')
        ) as response:
            if response.status not in [200, 201]:
                rich_logger.error(f"上传失败: {await response.text()}")
                return False
            if response.status == 403:
                rich_logger.error("可能触发 GitHub API 速率限制，等待 60 秒后重试...")
                await asyncio.sleep(60)
                return False  # 让调用方重试

        rich_logger.info(f"上传成功: {self._get_cdn_url(target_path)}")
        return True

    async def _async_get_existing_sha(self, session, path):
        """
        异步获取文件的SHA值（如果文件已存在）
        """
        try:
            async with session.get(f"{self.api_base}{path}", headers=self.gh_headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("sha")
                return None
        except Exception as e:
            rich_logger.error(f"获取SHA失败: {e}")
            return None

    def _get_cdn_url(self, path):
        """生成CDN URL"""
        return f"https://cdn.jsdelivr.net/gh/{self.repo_owner}/{self.repo_name}/{path}"
