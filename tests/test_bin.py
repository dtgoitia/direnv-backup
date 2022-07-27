import shutil
from pathlib import Path

import pytest

from src.cli.backup import backup
from src.lib import Config, restore_backup


def create_envrc(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"This is an .envrc file\n{path.absolute()}")


def test_kk(tmp_path: Path):
    use_accessible_dir_for_test_files = False

    if use_accessible_dir_for_test_files:
        test_dir = Path("testing_dir")
        if test_dir.exists():
            shutil.rmtree(test_dir)
        test_dir.mkdir(parents=True, exist_ok=True)
    else:
        test_dir = tmp_path

    config = Config(
        root_dir=test_dir / "root_dir",
        exclude=[],
        backup_dir=test_dir / "backup_dir",
        encrypt_backup=True,
        encryption_recipient="david.torralba.goitia@gmail.com",
    )

    def assert_root_directory_is_healthy():
        assert (config.root_dir / ".envrc").exists()
        assert (config.root_dir / "foo" / ".envrc").exists()
        assert (config.root_dir / "bar" / ".envrc").exists()

    # ----------------------------------------------------------------------------------
    #
    #    Backup
    #
    # ----------------------------------------------------------------------------------

    # Setup: create mock files to be backed up
    create_envrc(config.root_dir / ".envrc")
    create_envrc(config.root_dir / "foo/.envrc")
    create_envrc(config.root_dir / "bar/.envrc")
    assert_root_directory_is_healthy()

    # Act
    backup(config=config)

    # Assert
    assert len(list(config.backup_dir.glob("*.tar"))) == 0
    assert len(list(config.backup_dir.glob("*.gpg"))) == 1

    # ----------------------------------------------------------------------------------
    #
    #    Restore
    #
    # ----------------------------------------------------------------------------------

    # Setup: clean up files to test restoration works as expected
    shutil.rmtree(config.root_dir)
    assert config.root_dir.exists() is False

    # Setup: there must only be an encrypted file in the backup directory
    assert config.backup_dir.exists()
    files_in_backup_dir = [p for p in config.backup_dir.rglob("*") if p.is_file()]
    assert len(files_in_backup_dir) == 1
    assert files_in_backup_dir[0].suffixes == [".gpg"]

    # TODO: try to use the wrong recipient
    # broken_config = replace(config, encryption_recipient="foo")

    # Act
    restore_backup(config=config)

    # Assert
    assert_root_directory_is_healthy()


@pytest.mark.skip(reason="TODO")
def test_exit_if_config_file_does_not_exist():
    ...


@pytest.mark.skip(reason="TODO")
def test_exit_if_config_file_is_empty():
    ...


@pytest.mark.skip(reason="TODO")
def test_exit_if_config_file_is_not_valid_json():
    ...


@pytest.mark.skip(reason="TODO")
def test_exit_if_config_is_not_valid():
    ...


@pytest.mark.skip(reason="TODO")
def test_delete_temporary_tar_if_gpg_not_installed():
    ...


@pytest.mark.skip(reason="TODO")
def test_delete_temporary_tar_if_no_key_found_for_provided_recipient():
    ...
