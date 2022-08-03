from pathlib import Path

import pytest

from direnv_backup.config import Config
from tests.helpers.config import write_config


@pytest.fixture
def config(tmp_path: Path) -> Config:
    config = Config(
        root_dir=tmp_path / "root_dir",
        exclude=set(),
        backup_dir=tmp_path / "backup_dir",
        encrypt_backup=True,
        encryption_recipient="john@doe.com",
    )
    return config


@pytest.fixture
def config_file(tmp_path: Path, config: Config) -> Path:
    path = tmp_path / "config.json"
    write_config(path=path, config=config)
    return path
