import argparse
import logging
from pathlib import Path

from src.config import ConfigError, read_config
from src.encrypt import EncryptionError
from src.lib import restore_backup
from src.logging import set_up_logging_config

logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=str,
        help="Path to the config file",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Show debug logs")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    arguments = parse_arguments()

    set_up_logging_config(debug_mode_on=arguments.verbose)

    if not arguments.config:
        exit("Please specify a config (see --help)")

    config_path = Path(arguments.config)
    if not config_path.exists():
        exit(f"Provided path for the config file does not exit: {config_path}")
    logger.debug(f"Provided config {str(config_path.absolute())!r} file exists")

    try:
        config = read_config(path=config_path)
    except ConfigError as error:
        exit(error)

    logger.debug(f"Config loaded: {config}")

    try:
        restore_backup(config=config)
    except EncryptionError as error:
        exit(error)
