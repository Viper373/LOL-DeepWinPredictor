import os
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import Dict

from rich.align import Align
from rich.live import Live
from rich.panel import Panel
from rich.progress import (BarColumn, MofNCompleteColumn, Progress,
                           SpinnerColumn, TextColumn, TimeElapsedColumn,
                           TimeRemainingColumn, TransferSpeedColumn)

from tool_utils.file_utils import ProjectRootFinder
from tool_utils.global_console import get_console
from tool_utils.log_utils import RichLogger

rich_logger = RichLogger()
console = get_console()
project_root_finder = ProjectRootFinder(project_type="Python")
project_root = project_root_finder.get_root_name()


class RichProgressUtils:
    """
    同步多任务进度条管理类，所有进度条在一个Panel内，Panel始终在终端下方。
    日志输出请使用日志类，进度条类不负责日志打印。
    """

    def __init__(self, panel_title=project_root, panel_width=160):
        self.progress = Progress(
            TextColumn("🍔 [#ff8c00]{task.description}[/#ff8c00]"),
            SpinnerColumn(spinner_name="dots", style="#ffa500"),
            BarColumn(bar_width=None, complete_style="#ffe066", finished_style="#43ea80"),
            "🍢",
            MofNCompleteColumn(separator="/"),
            "🍰",
            TransferSpeedColumn(),
            "🧁",
            TextColumn("[#9370db]{task.percentage:>5.1f}%[/#9370db]"),
            "🍭",
            TimeElapsedColumn(),
            "🍸",
            TimeRemainingColumn(),
            expand=True,
            console=console,
        )
        self.panel_title = panel_title
        self.panel_width = panel_width
        self.live = None
        self._task_ids: Dict[str, int] = {}

    def _render_panel(self):
        table = self.progress.make_tasks_table(self.progress.tasks)
        panel = Panel(
            Align.left(table),
            title=self.panel_title,
            border_style="white",
            width=self.panel_width,
        )
        return panel

    def start(self):
        if self.live is None:
            self.live = Live(self._render_panel(), refresh_per_second=10, transient=False, console=console)
            self.live.start()

    def stop(self):
        if self.live:
            self.live.stop()
            self.live = None

    def add_task(self, description, total, start=True):
        task_id = self.progress.add_task(description, total=total, start=start)
        self._refresh()
        return task_id

    def advance(self, task_id, step=1):
        self.progress.advance(task_id, step)
        self._refresh()

    def update(self, task_id, **kwargs):
        self.progress.update(task_id, **kwargs)
        self._refresh()

    def remove_task(self, task_id):
        self.progress.remove_task(task_id)
        self._refresh()

    def _refresh(self):
        if self.live:
            self.live.update(self._render_panel())


# ================== 用法示例 =====================
if __name__ == "__main__":
    rich_progress = RichProgressUtils()
    rich_progress.start()
    try:
        def inner_worker(task_id, steps, sleep_min=0.01, sleep_max=0.05):
            for _ in range(steps):
                time.sleep(random.uniform(sleep_min, sleep_max))
                rich_progress.advance(task_id)


        def outer_worker(task_id, total_steps, inner_threads=5):
            steps_per_thread = total_steps // inner_threads
            with ThreadPoolExecutor(max_workers=inner_threads) as inner_executor:
                futures = [inner_executor.submit(inner_worker, task_id, steps_per_thread) for _ in range(inner_threads)]
                for f in futures:
                    f.result()
            # 补齐余数
            remainder = total_steps % inner_threads
            if remainder:
                inner_worker(task_id, remainder)
            rich_progress.update(task_id, completed=total_steps)


        num_tasks = 4
        steps_per_task = 200
        task_ids = []
        for i in range(num_tasks):
            task_ids.append(rich_progress.add_task(f"多线程任务{i + 1}", total=steps_per_task))

        with ThreadPoolExecutor(max_workers=num_tasks) as executor:
            futures = [executor.submit(outer_worker, task_id, steps_per_task) for task_id in task_ids]
            for f in futures:
                f.result()
    finally:
        rich_progress.stop()
