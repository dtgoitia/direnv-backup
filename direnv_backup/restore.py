import logging
import shutil
from pathlib import Path

from direnv_backup.archive import extract
from direnv_backup.config import Config
from direnv_backup.encrypt import decrypt
from direnv_backup.io import copy_file

logger = logging.getLogger(__name__)


# TODO: add support for dry run printing to console
def restore_file(backup: Path, config: Config) -> None:
    # Taxonomy of a backup file path:
    #
    #   my_backup_dir/.tmp/projects/foo/.envrc   <-- a backup file once extracted
    #   ------▲------ --▲- ---▲---- ----▲-----
    #         │         │     │         └─ relative path
    #         │         │     │
    #         │         │     └─ top parent
    #         │         │
    #         │         └─ where backup is extracted temporarily before restoration
    #         │
    #         └─ backups folder - specified in config.backup_dir
    #
    #
    #    variable name          variable value
    #  -------------------------------------------------------------------
    #    backup:                my_backup_dir/.tmp/projects/foo/.envrc
    #    config.tmp_dir:        my_backup_dir/.tmp
    #    relative_to_tmp_dir:                     projects/foo/.envrc
    #    top_parent:                              projects
    #    relative_path:                                    foo/.envrc
    #
    relative_to_tmp_dir = backup.relative_to(config.tmp_dir)
    top_parent = relative_to_tmp_dir.parts[0]

    # Assumption: the top parent directory name of the backup file must match the name
    # of the `root_dir` specified in the config
    assert top_parent == config.root_dir.name

    # Stripe anything path parts above the top parent, including the top parent itself
    relative_path = relative_to_tmp_dir.relative_to(top_parent)
    final_path = config.root_dir / relative_path
    logger.debug(f"Restoring {backup} to {final_path}")
    copy_file(src=backup, dst=final_path)


def find_all_backups(dir: Path, encrypted: bool) -> list[Path]:
    if encrypted:
        extension = ".gpg"
    else:
        extension = ".tar"

    backups = list(dir.glob(f"*{extension}"))
    return backups


def find_latest_backup(dir: Path, encrypted: bool) -> Path:
    backups = find_all_backups(dir=dir, encrypted=encrypted)

    # backups include a timestamp at the begining of the file
    sorted_backups = sorted(backups)
    logger.info(f"{len(sorted_backups)} backups found")

    most_recent_backup = sorted_backups.pop()
    logger.info(f"Most recent backup: {most_recent_backup.absolute()}")

    return most_recent_backup


def restore_backup(config: Config) -> None:
    """
    The restore backup will restore the files taking the config.root_dir as the root
    directory to calculate where to put each file inside the backup.

    Restoration uses global config to:
      1. Find backup path
      3. Determine where to restore the files in the backup

    GPG knows which private key to use to decrypt the file because its specified in the
    encrypted file itself: https://security.stackexchange.com/a/183202
    """
    # TODO assert keys exists for selected recipient, if not raise meaningful error

    if config.encrypt_backup:
        encrypted_path = find_latest_backup(dir=config.backup_dir, encrypted=True)
        # encrypted_path = next(config.backup_dir.glob("*.gpg"))
        archive_path = decrypt(encrypted_path=encrypted_path)
        assert archive_path.suffixes == [".tar"]
    else:
        archive_path = find_latest_backup(dir=config.backup_dir, encrypted=False)
        # archive_path = next(config.backup_dir.glob("*.tar"))

    # To make clean-up easier, extract the backup into a temporary directory
    #
    #   backup_dir/
    #       20220727_181651.gpg
    #       20220727_181651.tar
    #       .tmp/    <---- temporary dir to extract tar file
    #           projects/.envrc
    #           projects/foo/.envrc
    #
    tmp_dir = config.tmp_dir
    tmp_dir.mkdir(parents=True, exist_ok=True)
    extract(path=archive_path, extract_to_dir=tmp_dir)

    file_paths = (path for path in tmp_dir.rglob("*") if path.is_file())

    try:
        for backup in file_paths:
            restore_file(backup=backup, config=config)
    except Exception:
        raise
    finally:
        logger.debug("Cleaning temporary files...")
        shutil.rmtree(tmp_dir)

        if config.encrypt_backup:
            archive_path.unlink()
        else:
            # If the backup was not encrypted, the archive is the backup itself so do
            # not delete it during the clean-up of you will loose your backup!
            ...

    logger.debug("Restore process finished")
