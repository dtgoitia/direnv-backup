from __future__ import annotations

import os
import subprocess
from pathlib import Path

from devex.pkgbuild import (
    LOCAL_AUR_REPO_DIR_ENVVAR_NAME,
    RawPkgbuild,
    find_pkgbuild_path,
)
from devex.pyproject import find_pyproject_path
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


class MockDevelopmentEnvironment:
    """
    Create a disposable development environment with PKGBUILD, pyproject.toml, etc. and
    mock git
    """

    def __init__(
        self,
        test_dir: Path,
        pkgbuild: RawPkgbuild = "",
        pyproject: str = "",
    ) -> None:
        self.test_dir = test_dir

        if not pkgbuild:
            pkgbuild = find_pkgbuild_path().read_text()

        if not pyproject:
            pyproject = find_pyproject_path().read_text()

        aur_dir = test_dir / "aur"
        aur_dir.mkdir(parents=True, exist_ok=True)
        self.aur_pkbuild_path = aur_dir / "PKGBUILD"
        self.aur_pkbuild_path.write_text(pkgbuild)

        self.repo_dir = test_dir / "repo"
        self.repo_dir.mkdir(parents=True, exist_ok=True)
        self.pkbuild_path = self.repo_dir / "PKGBUILD"
        self.pkbuild_path.write_text(pkgbuild)
        self.pyproject_path = self.repo_dir / "pyproject.toml"
        self.pyproject_path.write_text(pyproject)

    def __enter__(self) -> MockDevelopmentEnvironment:
        self.previous_working_dir = Path.cwd()
        change_working_directory(to=self.repo_dir)

        self.previous_environment = os.environ
        os.environ = self.previous_environment.copy()
        os.environ[LOCAL_AUR_REPO_DIR_ENVVAR_NAME] = str(
            self.aur_pkbuild_path.parent.absolute()
        )

        return self

    def __exit__(self, ext_type, exc_value, exc_tb) -> None:
        change_working_directory(to=self.previous_working_dir)

        os.environ = self.previous_environment

    @property
    def pkgbuild(self) -> RawPkgbuild:
        return self.pkbuild_path.read_text()


def change_working_directory(to: Path) -> None:
    os.chdir(path=to)
