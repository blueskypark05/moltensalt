import sys
import json
from pathlib import Path


def get_app_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parents[1]



APP_DIR = get_app_dir()

SETTINGS_DIR = APP_DIR / "config"
SETTING_PATH = SETTINGS_DIR / "setting.json"

def get_source_dir():
    return APP_DIR / "source"

def load_config():
    if not SETTING_PATH.exists():
        raise FileNotFoundError(f"Setting file not found:\n{SETTING_PATH}")

    try:
        with open(SETTING_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid setting file:\n{SETTING_PATH}\n\n{e}")