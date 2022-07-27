import logging
from pathlib import Path

from src.config import read_config
from src.lib import backup

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    config = read_config(path=Path("config.json"))
    backup(config=config)
