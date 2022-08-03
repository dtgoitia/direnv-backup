import datetime
import json
import logging
import shutil
from dataclasses import dataclass
from pathlib import Path

from direnv_backup.archive import archive_dir
from direnv_backup.config import Config
from direnv_backup.encrypt import EncryptionError, encrypt
from direnv_backup.io import copy_file

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


def build_backup_filename() -> str:
    now = datetime.datetime.now()
    microseconds = datetime.timedelta(microseconds=now.microsecond)
    t = (now - microseconds).isoformat()
    filename = t.replace("-", "").replace(":", "").replace("T", "-")
    return filename


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
    if not config.encryption_recipient:
        raise EncryptionError("Config must specify a recipient to run encryption")

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
