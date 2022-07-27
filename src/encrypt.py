import logging
import subprocess
from pathlib import Path

from src.types import Email

logger = logging.getLogger(__name__)


class EncryptionError(Exception):
    ...


def is_gpg_installed() -> bool:
    cmd = ["which", "gpg"]
    proc = subprocess.run(cmd, capture_output=True)
    stdout = proc.stdout.decode("utf-8")

    fmt_command = " ".join(cmd)
    logger.debug(f"{fmt_command!r} returned this stdout: {stdout!r}")

    gpg_command_found = stdout != ""
    if gpg_command_found:
        logger.debug("gpg command is installed")
    else:
        logger.debug("gpg command is not installed")

    return gpg_command_found


def email_has_gpg_key_associated(email: Email) -> bool:
    cmd = ["gpg", "--list-keys"]
    logger.debug(f'Executing {" ".join([str(x) for x in cmd])!r} ...')
    proc = subprocess.run(cmd, capture_output=True)
    stdout = proc.stdout.decode("utf-8")
    stderr = proc.stderr.decode("utf-8")

    logger.debug(f"{stdout=}")
    logger.debug(f"{stderr=}")

    email_found_in_keys = f"<{email}>" in stdout

    if email_found_in_keys:
        logger.debug(f"Email {email!r} is associated to a GPG key")
    else:
        logger.debug(f"Email {email!r} is not associated to any GPG key")

    return email_found_in_keys


def encrypt(path_to_encrypt: Path, encrypted_path: Path, recipient: Email) -> Path:
    if not is_gpg_installed():
        error_message = "gpg is not installed"
        logger.debug(error_message)
        raise EncryptionError(error_message)

    if not email_has_gpg_key_associated(email=recipient):
        error_message = f"No key found for recipient {recipient!r}"
        logger.debug(error_message)
        raise EncryptionError(error_message)

    cmd = [
        "gpg",
        "--output",
        encrypted_path,
        "--encrypt",
        "--recipient",
        recipient,
        path_to_encrypt,
    ]
    logger.debug(f'Executing {" ".join([str(x) for x in cmd])!r} ...')
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
    if not is_gpg_installed():
        raise EncryptionError("gpg is not installed")

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
