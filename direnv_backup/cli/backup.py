import argparse
import logging
import sys
from pathlib import Path

from direnv_backup.backup import backup, remove_old_backups
from direnv_backup.config import ConfigError, read_config
from direnv_backup.encrypt import EncryptionError
from direnv_backup.logging import set_up_logging_config

logger = logging.getLogger(__name__)


def parse_arguments(args: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=str,
        help="Path to the config file",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Show debug logs")
    arguments = parser.parse_args(args)
    return arguments


def main(args: list[str] | None = None) -> str | None:
    arguments = parse_arguments(args=args)

    if not arguments.config:
        return "Please specify a config (see --help)"

    config_path = Path(arguments.config)
    if not config_path.exists():
        return f"Provided path for the config file does not exit: {config_path}"

    try:
        config = read_config(path=config_path)
    except ConfigError as error:
        return str(error)

    set_up_logging_config(debug_mode_on=arguments.verbose)

    logger.debug(f"Config loaded: {config}")

    try:
        backup(config=config)
    except EncryptionError as error:
        return str(error)

    remove_old_backups(config=config)

    return None


if __name__ == "__main__":
    if exit_value := main():
        sys.exit(exit_value)
