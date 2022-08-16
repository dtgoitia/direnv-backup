import os
from pathlib import Path
from unittest import mock

import pytest

from direnv_backup.config import Config
from scripts.bump import LOCAL_AUR_REPO_DIR_ENVVAR_NAME
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


@pytest.fixture
def fake_environment():
    """
    Restores `os.environ` values after each test to the values prior to each test.
    """
    environment_copy = os.environ.copy()
    with mock.patch.dict(os.environ, environment_copy):

        # Sometimes this env var might exist depending on whether tests run inside a
        # container or not
        if LOCAL_AUR_REPO_DIR_ENVVAR_NAME in os.environ:
            del os.environ[LOCAL_AUR_REPO_DIR_ENVVAR_NAME]

        yield
