import os
import tempfile


def get_runtime_dir() -> str:
    """Writable directory for runtime artifacts."""
    base = tempfile.gettempdir()
    path = os.path.join(base, "printado")
    os.makedirs(path, exist_ok=True)
    return path


def get_legacy_temp_screenshot_path() -> str:
    return os.path.abspath("temp_screenshot.png")


def get_temp_screenshot_path() -> str:
    return os.path.join(get_runtime_dir(), "temp_screenshot.png")


def delete_temp_screenshot():
    for temp_file in (get_legacy_temp_screenshot_path(), get_temp_screenshot_path()):
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except Exception:
            pass
