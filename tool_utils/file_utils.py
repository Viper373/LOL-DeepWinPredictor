# -*- coding: utf-8 -*-
# @Project   :td_gsc_scraper
# @FileName  :file_utils.py
# @Time      :2024/10/11 11:00
# @Author    :Zhangjinzhao
# @Software  :PyCharm

from pathlib import Path

from tool_utils.log_utils import RichLogger

rich_logger = RichLogger()


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
