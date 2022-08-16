import subprocess
from pathlib import Path

from tests.helpers.direnv import (
    assert_all_envrc_files_are_in_place,
    create_sample_envrc_files,
    delete_envrc_files,
    get_direnv_files,
)
from tests.helpers.gpg import (
    GPGKey,
    delete_all_gpg_keys,
    generate_gpg_key,
    gpg_key_exists,
)


class AutoCleaningEnvironment:
    """
    Cleanup/recreate required direnv files, GPG keys to mimic real usage scenarios.
    """

    def __init__(
        self,
        *,
        root_dir: Path,
        set_envrcs: bool = False,
        gpg_key: GPGKey | None = None,
        cleanup_gpg_keys_on_exit: bool = True,
    ):
        self.root_dir = root_dir
        self.create_envrc_files = set_envrcs
        self.gpg_key = gpg_key
        self.cleanup_gpg_keys_on_exit = cleanup_gpg_keys_on_exit

    def __enter__(self):
        delete_envrc_files(root_dir=self.root_dir)

        if self.create_envrc_files:
            create_sample_envrc_files(root_dir=self.root_dir)
            assert_all_envrc_files_are_in_place(root_dir=self.root_dir)

        if self.gpg_key:
            if not gpg_key_exists(key=self.gpg_key):
                generate_gpg_key(key=self.gpg_key)
                assert gpg_key_exists(key=self.gpg_key)

    def __exit__(self, ext_type, exc_value, exc_tb):
        # TODO handle: ext_type, exc_value, exc_tb

        if get_direnv_files(lookup_dir=self.root_dir):
            delete_envrc_files(root_dir=self.root_dir)
            assert get_direnv_files(lookup_dir=self.root_dir) == set()

        if self.cleanup_gpg_keys_on_exit:
            delete_all_gpg_keys()


def command_exists(command: str) -> bool:
    process = subprocess.run(["which", command], capture_output=True)
    stdout = process.stdout.decode("utf-8")
    stderr = process.stderr.decode("utf-8")

    if process.returncode == 1:
        assert not stdout
        assert f"which: no {command} in " in stderr
        return False

    assert stdout
    assert not stderr
    return True
