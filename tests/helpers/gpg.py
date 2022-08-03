import subprocess
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent


@dataclass
class GPGKey:
    name: str
    email: str


def gpg_key_exists(key: GPGKey) -> bool:
    process = subprocess.run(["gpg", "--list-keys"], capture_output=True)
    stdout = process.stdout.decode("utf-8")

    for line in stdout.split("\n"):
        if key.name in line and key.email in line:
            return True

    return False


def generate_gpg_key(key: GPGKey) -> None:
    tmp_dir = Path("/tmp")
    assert tmp_dir.exists()

    key_spec_path = tmp_dir / "key_spec_path"

    key_spec_path.write_text(
        dedent(
            f"""
            %echo Generating a default key
            # Do not ask for a passphrase
            %no-protection
            Key-Type: default
            Subkey-Type: default
            Name-Real: {key.name}
            Name-Comment: with stupid passphrase
            Name-Email: {key.email}
            Expire-Date: 0
            # Do a commit here, so that we can later print "done" :-)
            %commit
            %echo done
            """
        )
    )
    cmd = ["gpg", "--batch", "--gen-key", str(key_spec_path)]
    subprocess.run(cmd, capture_output=True)


def delete_all_gpg_keys() -> None:
    pubring_path = Path("~/.gnupg/pubring.kbx").expanduser()
    if pubring_path.exists():
        pubring_path.unlink()
    subprocess.run(["gpg", "--list-keys"], capture_output=True)
