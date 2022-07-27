import logging
import subprocess
from pathlib import Path

from src.types import Email

logger = logging.getLogger(__name__)


def encrypt(path_to_encrypt: Path, encrypted_path: Path, recipient: Email) -> Path:
    # TODO: if GPG key to be used is not specified in config, raise clear exception

    cmd = [
        "gpg",
        "--output",
        encrypted_path,
        "--encrypt",
        "--recipient",
        recipient,
        path_to_encrypt,
    ]
    proc = subprocess.run(cmd, capture_output=True)
    stdout = proc.stdout.decode("utf-8")
    stderr = proc.stderr.decode("utf-8")

    something_went_wrong = stdout or stderr

    if something_went_wrong:
        # TODO: handle this with the corresponding exceptions - if key missing, etc.
        print(f"{stdout=}")
        print(f"{stderr=}")

    logger.debug(f"Encryption output: {encrypted_path}")


def decrypt(encrypted_path: Path) -> Path:
    decrypted_path = encrypted_path.with_suffix(".tar")

    cmd = [
        "gpg",
        "--output",
        decrypted_path,
        "--decrypt",
        encrypted_path,
    ]
    proc = subprocess.run(cmd, capture_output=True)
    stdout = proc.stdout.decode("utf-8")
    stderr = proc.stderr.decode("utf-8")

    something_went_wrong = stdout or stderr

    if something_went_wrong:
        # TODO: handle this with the corresponding exceptions - if key missing, etc.
        print(f"{stdout=}")
        print(f"{stderr=}")

    logger.debug(f"Encryption output: {decrypted_path}")
    return decrypted_path
