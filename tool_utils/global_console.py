from rich.console import Console

_console_singleton = None

def get_console():
    global _console_singleton
    if _console_singleton is None:
        _console_singleton = Console()
    return _console_singleton 