# -*- coding: utf-8 -*-
# @Project   :td_gsc_scraper
# @FileName  :file_utils.py
# @Time      :2024/10/11 11:00
# @Author    :Zhangjinzhao
# @Software  :PyCharm

import mimetypes
import os
import subprocess
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

from tool_utils.log_utils import RichLogger

rich_logger = RichLogger()


class S3Utils:
    def __init__(self):
        s3endpoint = os.getenv('S3_ENDPOINT')  # 请填入控制台 “Bucket 设置” 页面底部的 “Endpoint” 标签中的信息
        s3region = os.getenv('S3_REGION')
        s3accessKeyId = os.getenv('S3_ACCESS_KEY')  # 请到控制台创建子账户，并为子账户创建相应 accessKey
        s3SecretKeyId = os.getenv('S3_SECRET_KEY')  # ！！切记，创建子账户时，需要手动为其分配具体权限！！
        self.bucket = os.getenv('S3_BUCKET')  # 请填入控制台 “Bucket 列表” 页面的 “Bucket 名称”
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=s3accessKeyId,
            aws_secret_access_key=s3SecretKeyId,
            endpoint_url=s3endpoint,
            region_name=s3region
        )

    @rich_logger
    def check_s3_file_exists(self, file_path):
        """
        检查文件在 S3 上是否已存在
        :param file_path: 本地文件路径
        :return: 存在返回 True，不存在返回 False
        """
        try:
            # 将路径替换为统一的单斜杠
            unified_path = file_path.replace("\\", "/")
            # 分割路径
            parts = unified_path.split("/")
            xovideos_indices = [i for i, part in enumerate(parts) if part == "XOVideos"]

            videos_index = xovideos_indices[1]  # 获取第二个 "XOVideos" 的索引
            s3_key = "/".join(parts[videos_index:])

            # 检查文件是否存在
            try:
                self.s3_client.head_object(Bucket=self.bucket, Key=s3_key)
                rich_logger.info(f"文件已存在于 S3: {s3_key}")
                return True
            except ClientError as e:
                error_code = e.response['Error'].get('Code', 'Unknown')
                if error_code == '404':
                    rich_logger.info(f"文件不存在于 S3: {s3_key}")
                    return False
                else:
                    rich_logger.error(f"检查 S3 文件时出错 ({error_code}): {e}")
                    return False

        except Exception as e:
            rich_logger.error(f"检查 S3 文件时发生未知错误: {e}")
            return False

    @rich_logger
    def s4_upload_file(self, file_path, delete_on_success=True, delete_on_failure=False):

        try:
            # 路径合规性检查
            if not os.path.isfile(file_path):
                rich_logger.error(f"文件不存在或不可读: {file_path}")
                return False

            # 将路径替换为统一的单斜杠
            unified_path = file_path.replace("\\", "/")
            # 分割路径
            parts = unified_path.split("/")
            xovideos_indices = [i for i, part in enumerate(parts) if part == "XOVideos"]

            videos_index = xovideos_indices[1]  # 获取第二个 "XOVideos" 的索引
            s3_key = "/".join(parts[videos_index:])

            # 检查文件是否存在
            try:
                self.s3_client.head_object(Bucket=self.bucket, Key=s3_key)
                rich_logger.info(f"S4文件已存在，跳过上传: {s3_key}")

                if delete_on_success:
                    try:
                        os.remove(file_path)
                    except OSError as e:
                        rich_logger.error(f"删除本地文件失败: {e}")
                return True
            except ClientError as e:
                error_code = e.response['Error'].get('Code', 'Unknown')
                if error_code != '404':
                    raise

            # 动态检测 MIME 类型
            content_type, _ = mimetypes.guess_type(file_path)
            extra_args = {
                "ContentType": content_type or "application/octet-stream",
                "ContentDisposition": "inline"
            }

            # 记录文件大小
            file_size = os.path.getsize(file_path)
            size_units = ['B', 'KB', 'MB', 'GB', 'TB']
            size_index = 0
            while file_size >= 1024 and size_index < len(size_units) - 1:
                file_size /= 1024.0
                size_index += 1
            size_str = f"{int(file_size)} {size_units[size_index]}" if size_index == 0 else f"{file_size:.2f} {size_units[size_index]}".rstrip('0').rstrip('.')
            rich_logger.info(f"S4开始上传: {s3_key}，大小: {size_str}")

            # 执行上传
            self.s3_client.upload_file(
                Filename=file_path,
                Bucket=self.bucket,
                Key=s3_key,
                ExtraArgs=extra_args
            )
            rich_logger.info(f"S4上传成功: {s3_key}")

            # 上传成功后删除本地文件
            if delete_on_success:
                try:
                    os.remove(file_path)
                except OSError as e:
                    rich_logger.error(f"删除本地文件失败: {e}")
            return True

        except ClientError as e:
            error_code = e.response['Error'].get('Code', 'Unknown')
            rich_logger.error(f"S4上传失败 ({error_code}): {e}")
            if delete_on_failure:
                try:
                    os.remove(file_path)
                except OSError as err:
                    rich_logger.error(f"删除本地文件失败: {err}")
            return False
        except Exception as e:
            rich_logger.exception(f"S4未知错误: {e}")
            if delete_on_failure:
                try:
                    os.remove(file_path)
                except OSError as err:
                    rich_logger.error(f"删除本地文件失败: {err}")
            return False

    @staticmethod
    @rich_logger
    def ffmpeg_video_streaming(input_file):
        """
        使用FFmpeg将视频转换为H.264格式，并进行流优化处理，使其能够流式传输。

        参数:
        - input_file: 输入的视频文件路径
        - output_file: 输出的优化后的视频文件路径

        返回:
        - 成功: 返回输出文件的路径
        - 失败: 返回 None
        """
        output_file = input_file.replace('.mp4', 'h264.mp4')
        command = [
            'ffmpeg',
            '-i', input_file,
            '-c:v', 'libx264',  # 使用H.264编解码器
            '-c:a', 'copy',  # 保留原始音频
            '-movflags', 'faststart',  # 使视频文件头放在文件开始处，优化流媒体播放
            output_file
        ]

        try:
            # 使用 subprocess.run 执行 FFmpeg 命令，并捕获 stdout 和 stderr 以便调试
            subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            rich_logger.info(f"视频优化和H.264转换完成: {output_file}")
            os.remove(input_file)  # 删除原视频，保留流式优化视频
            os.rename(output_file, input_file)
            return input_file
        except subprocess.CalledProcessError as e:
            # 捕获 FFmpeg 命令的返回码和输出
            rich_logger.exception(f"视频优化失败: {output_file}\n错误信息: {e.stderr.decode('utf-8')}")
            return None
        except Exception as e:
            # 捕获其他意外错误
            rich_logger.error(f"未知错误: {e}")
            return None


class ProjectRootFinder:
    PROJECT_MARKERS = {
        "Python": ["setup.py", "requirements.txt", "pyproject.toml", "manage.py", "Pipfile", "app.py"],
        "Java": ["pom.xml", "build.gradle", "settings.gradle", "build.xml", "gradlew", "mvnw"],
        "Node": ["package.json", "node_modules", "yarn.lock", "package-lock.json", "tsconfig.json", "webpack.config.js"],
        "Ruby": ["Gemfile", "Gemfile.lock", "Rakefile", "config.ru"],
        "PHP": ["composer.json", "composer.lock", "index.php", ".htaccess"],
        "Go": ["go.mod", "go.sum", "main.go"],
        "Rust": ["Cargo.toml", "Cargo.lock", "main.rs"],
        "C++": ["CMakeLists.txt", "Makefile", ".cpp", ".hpp"],
        "Git": [".git"],
        "Docker": ["Dockerfile", ".dockerignore"],
        "General": ["README.md", "LICENSE", ".gitignore", ".env", "CONTRIBUTING.md"]
    }

    def __init__(self, project_type=None):
        if project_type is None:
            self.markers = self._get_default_markers()
        else:
            self.markers = self.PROJECT_MARKERS.get(project_type, [])
            if not self.markers:
                raise ValueError(f"Unknown project type: {project_type}")
        self._root = None

    def _get_default_markers(self):
        # 合并所有标记，去重
        all_markers = set()
        for markers in self.PROJECT_MARKERS.values():
            all_markers.update(markers)
        return list(all_markers)

    def find_root(self):
        if self._root is not None:
            return self._root

        current_dir = Path.cwd()
        while current_dir != current_dir.parent:
            for marker in self.markers:
                if (current_dir / marker).exists():
                    self._root = current_dir
                    return self._root
            current_dir = current_dir.parent

        raise FileNotFoundError("Project root not found.")

    def get_root_name(self):
        root_path = self.find_root()
        return root_path.name


# 示例用法
if __name__ == "__main__":
    finder = ProjectRootFinder(project_type="Python")
    try:
        root_name = finder.get_root_name()
        print(f"Project root directory name: {root_name}")
    except FileNotFoundError as e:
        print(e)
