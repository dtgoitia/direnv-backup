
import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from pprint import pprint

logger = logging.getLogger(__name__)

config_envvar_name = "DIRENV_BACKUP_CONFIG"

@dataclass
class Config:
    root_dir: Path  # top of the filesystem where to start scanning for direnv files
    user: str
    exclude: list[str]


class ConfigError(Exception):
    ...


def load_config(cli_path: str) -> Config:
    try:
        return load_config_from_envvar(envvar_name=config_envvar_name)
    except ConfigError as env_error:
        logger.debug(env_error)

    if not cli_path:
        raise ConfigError(f'Config not found')

    try:
        return try_loading_config_from_cli()
    except ConfigError as env_error:
        logger.debug(env_error)

def load_config_from_envvar(envvar_name: str) -> Config:
    if path_str := os.environ.get(envvar_name):
        logger.debug(f"{envvar_name!r} found set to {path_str}")
        path = Path(path_str)
        if not path.exists():
            logger.debug(f"{envvar_name!r} environment variable not set")
            raise ConfigError(f"{envvar_name!r} environment variable not set")
        config = read_config(path=path)
        return config
    else:
        raise ConfigError(f"{config_envvar_name!r} environment variable not set")

def try_loading_config_from_cli():
    ...



def read_config(path: Path) -> Config:
    """
    Assumption: path exists
    If paths contain curly braces, try to replace interpolate with env vars
    """

    raw_config = path.read_text()

    # interpolate environemnt variables
    # TODO
    interpolated_config = raw_config

    # parse from JSON string
    config_data = json.loads(interpolated_config)
    config = Config(
        root_dir=Path(config_data["root_dir"]),
        user=os.environ["USER"],
        exclude=set(config_data["exclude"])
    )

    return config

def find_direnv_files(config: Config) -> list[Path]:
    direnv_files: set[Path] = set()

    stack: list[Path] = [config.root_dir]
    while True:
        if not stack:
            break

        curr_path = stack.pop()
        if curr_path.stem in config.exclude:
            continue

        for path in curr_path.glob("*"):
            stem = path.stem

            if stem == ".envrc":
                direnv_files.add(path)
                continue

            if stem in config.exclude:
                continue

            stack.append(path)

    logger.debug(f'Found {len(direnv_files)} direnv files')

    result = sorted(list(direnv_files))
    return result

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    config = read_config(path=Path('config.json'))
    paths = find_direnv_files(config=config)
    for path in paths:
        print(path)

