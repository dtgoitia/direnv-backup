import dataclasses
import json
from pathlib import Path

from direnv_backup.config import Config


def write_config(path: Path, config: Config) -> None:
    data = dataclasses.asdict(config)

    if data.keys() != config.__dict__.keys():
        raise NotImplementedError("Some Config attributes are missing in the dict")

    # Convert paths to str
    clean_data = {}
    for key, value in data.items():
        if isinstance(value, Path):
            clean_data[key] = str(value)
        elif isinstance(value, set):
            clean_data[key] = str(list(value))
        else:
            clean_data[key] = value

    with path.open("w") as f:
        json.dump(clean_data, f, indent=2)
