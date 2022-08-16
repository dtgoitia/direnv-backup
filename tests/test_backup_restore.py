import dataclasses
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from direnv_backup.cli.backup import backup, main
from direnv_backup.config import Config
from direnv_backup.restore import restore_backup
from tests.helpers.config import write_config
from tests.helpers.direnv import assert_all_envrc_files_are_in_place
from tests.helpers.docker import inside_container
from tests.helpers.environment import AutoCleaningEnvironment
from tests.helpers.gpg import GPGKey


@pytest.mark.skipif(not inside_container(), reason="must run in container")
def test_backup_and_restore_with_encryption(config: Config) -> None:
    # ----------------------------------------------------------------------------------
    #  Backup
    # ----------------------------------------------------------------------------------

    assert config.encryption_recipient
    gpg_key = GPGKey(name="foo", email=config.encryption_recipient)

    with AutoCleaningEnvironment(
        root_dir=config.root_dir,
        set_envrcs=True,
        gpg_key=gpg_key,
        cleanup_gpg_keys_on_exit=False,
    ):
        # Act
        backup(config=config)

        # Assert
        assert len(list(config.backup_dir.glob("*.tar"))) == 0
        assert len(list(config.backup_dir.glob("*.gpg"))) == 1

    # ----------------------------------------------------------------------------------
    #  Restore
    # ----------------------------------------------------------------------------------

    # Setup: there must only be an encrypted file in the backup directory
    assert config.backup_dir.exists()
    files_in_backup_dir = [p for p in config.backup_dir.rglob("*") if p.is_file()]
    assert len(files_in_backup_dir) == 1
    assert files_in_backup_dir[0].suffixes == [".gpg"]

    with AutoCleaningEnvironment(
        root_dir=config.root_dir,
        set_envrcs=False,
        gpg_key=gpg_key,
    ):
        # Act
        restore_backup(config=config)

        # Assert
        assert_all_envrc_files_are_in_place(root_dir=config.root_dir)


@pytest.mark.skipif(not inside_container(), reason="must run in container")
def test_backup_and_restore_without_encryption(config: Config) -> None:
    # ----------------------------------------------------------------------------------
    #  Backup
    # ----------------------------------------------------------------------------------

    config = Config(
        root_dir=config.root_dir,
        exclude=config.exclude,
        backup_dir=config.backup_dir,
        encrypt_backup=False,
        encryption_recipient=None,
    )

    with AutoCleaningEnvironment(
        root_dir=config.root_dir,
        set_envrcs=True,
        gpg_key=None,
        cleanup_gpg_keys_on_exit=False,
    ):
        # Act
        backup(config=config)

        # Assert
        assert len(list(config.backup_dir.glob("*.tar"))) == 1
        assert len(list(config.backup_dir.glob("*.gpg"))) == 0

    # ----------------------------------------------------------------------------------
    #  Restore
    # ----------------------------------------------------------------------------------

    # Setup: there must only be an encrypted file in the backup directory
    assert config.backup_dir.exists()
    files_in_backup_dir = [p for p in config.backup_dir.rglob("*") if p.is_file()]
    assert len(files_in_backup_dir) == 1
    assert files_in_backup_dir[0].suffixes == [".tar"]

    with AutoCleaningEnvironment(
        root_dir=config.root_dir,
        set_envrcs=False,
        gpg_key=None,
        cleanup_gpg_keys_on_exit=False,
    ):
        # Act
        restore_backup(config=config)

        # Assert
        assert_all_envrc_files_are_in_place(root_dir=config.root_dir)


@patch("direnv_backup.encrypt.is_gpg_installed")
def test_delete_temporary_tar_if_gpg_not_installed(
    mocked_is_gpg_installed: MagicMock,
    config_file: Path,
    config: Config,
) -> None:
    mocked_is_gpg_installed.return_value = False

    write_config(path=config_file, config=config)

    exit_value = main(["--config", str(config_file)])
    assert exit_value == "gpg is not installed"

    tar_files_in_backup_dir = list(config.backup_dir.rglob("*.tar"))
    assert not tar_files_in_backup_dir


def test_delete_temporary_tar_if_no_key_found_for_provided_recipient(
    tmp_path: Path, config: Config
) -> None:
    config_path = tmp_path / "config.json"
    nonexistent_recipient = "john@doe.com"
    bad_config = dataclasses.replace(config, encryption_recipient=nonexistent_recipient)
    write_config(path=config_path, config=bad_config)

    exit_value = main(["--config", str(config_path)])
    assert exit_value == "No key found for recipient 'john@doe.com'"

    tar_files_in_backup_dir = list(config.backup_dir.rglob("*.tar"))
    assert not tar_files_in_backup_dir
