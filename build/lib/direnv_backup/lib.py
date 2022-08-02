import datetime
import json
import logging
import shutil
from dataclasses import dataclass
from pathlib import Path

from direnv_backup.archive import archive_dir, extract
from direnv_backup.config import Config
from direnv_backup.encrypt import EncryptionError, decrypt, encrypt

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Snapshot:
    files: list[Path]
    timestamp: datetime.datetime


def scan_direnv_files(config: Config) -> Snapshot:
    start_path = config.root_dir
    logger.debug(f"Scanning direnv files in {start_path}")

    direnv_files: set[Path] = set()

    stack: list[Path] = [start_path]
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

    logger.debug(f"Found {len(direnv_files)} direnv files")

    snapshot = Snapshot(
        files=sorted(list(direnv_files)),
        timestamp=datetime.datetime.now(),
    )

    return snapshot


def read_snapshot(path: Path) -> Snapshot:
    with path.open("r") as f:
        data = json.load(f)

        return Snapshot(
            files=[Path(file) for file in data["files"]],
            timestamp=datetime.datetime.fromisoformat(data["timestamp"]),
        )


def build_backup_filename() -> Path:
    now = datetime.datetime.now()
    microseconds = datetime.timedelta(microseconds=now.microsecond)
    t = (now - microseconds).isoformat()
    filename = t.replace("-", "").replace(":", "").replace("T", "-")
    return filename


def copy_file(*, src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(src=src, dst=dst)


def copy_snapshot_files(*, snapshot: Snapshot, config: Config) -> None:
    config.tmp_dir.mkdir(parents=True, exist_ok=True)

    # When mirroring the original file structure, you want to include the `root_dir` dir
    # name in the file structure
    base_path = config.root_dir.parent

    total = len(snapshot.files)
    for i, path in enumerate(snapshot.files):
        partial = path.relative_to(base_path)
        backup_path = config.tmp_dir / partial
        copy_file(src=path, dst=backup_path)
        logger.info(f"{i+1}/{total}  {partial} backed up")


def archive_snapshot(config: Config) -> Path:
    archive_filename = build_backup_filename()
    archive_path = config.backup_dir / f"{archive_filename}.tar"

    archive_dir(dir=config.tmp_dir, base=config.tmp_dir, output=archive_path)

    shutil.rmtree(path=config.tmp_dir)

    return archive_path


def encrypt_archive(archive_path: Path, config: Config) -> None:
    encrypted_path = archive_path.with_suffix(".gpg")

    logger.debug(f"Attempting to encrypt {archive_path}")
    encrypt(
        path_to_encrypt=archive_path,
        encrypted_path=encrypted_path,
        recipient=config.encryption_recipient,
    )


def backup(config: Config) -> None:
    snapshot = scan_direnv_files(config=config)

    copy_snapshot_files(snapshot=snapshot, config=config)

    archive_path = archive_snapshot(config=config)

    if config.encrypt_backup:
        try:
            encrypt_archive(archive_path=archive_path, config=config)
        except EncryptionError:
            raise
        finally:
            logger.debug(f"Cleaning up temporary archive: {archive_path}")
            archive_path.unlink()


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
    # TODO assert image exists for selected recipient, if not raise meaningful error

    if config.encrypt_backup:
        encrypted_path = next(config.backup_dir.glob("*.gpg"))
        archive_path = decrypt(encrypted_path=encrypted_path)
        assert archive_path.suffixes == [".tar"]
    else:
        archive_path = next(config.backup_dir.glob("*.tar"))

    if not encrypted_path.exists():
        raise NotImplementedError("TODO: add meaningful error")

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
