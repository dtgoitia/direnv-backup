#!/usr/bin/env python

"""
Copy the PKGBUILD from the current repo to the (local clone of the) AUR repo, and do
nothing else

Version bumps, updating checksums, etc. is handled by other scripts.
"""

import argparse
import logging
import os
import shutil
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def parse_arguments(args: list[str] | None = None) -> argparse.Namespace:
    current_module_docstring = sys.modules[__name__].__doc__
    parser = argparse.ArgumentParser(
        description=current_module_docstring,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    arguments = parser.parse_args(args)
    return arguments


class ConfigError(Exception):
    ...


def find_local_pkgbuild() -> Path:
    pkgbuild_dir = Path("PKGBUILD")
    if not pkgbuild_dir.exists() or pkgbuild_dir.is_file():
        raise ConfigError(
            "Error while looking for copy of PKGBUILD files. Expected to find them in"
            f" the {pkgbuild_dir.absolute()} directory, but it does not exit"
        )

    pkgbuild_path = next(pkgbuild_dir.glob("PKGBUILD"))

    return pkgbuild_path


def get_local_aur_repo_dir() -> Path:
    envvar_name = "LOCAL_AUR_REPO_DIR"
    try:
        dir_as_str = os.environ[envvar_name]
    except KeyError:
        raise ConfigError(f"Please set the {envvar_name!r} environment variable")

    dir = Path(dir_as_str).expanduser()

    if not dir.exists():
        raise ConfigError(
            f"The dir {dir_as_str} does not exit - Please set/update the"
            f" {envvar_name!r} environment variable"
        )

    return dir


def push_pkgbuild_to_local_aur_repo() -> None:
    aur_repo_dir = get_local_aur_repo_dir()
    pkgbuild_path = find_local_pkgbuild()

    pkgbuild_dst_path = aur_repo_dir / pkgbuild_path.name
    shutil.copy(src=pkgbuild_path, dst=pkgbuild_dst_path)


def main(args: list[str] | None = None) -> None | str:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    _ = parse_arguments(args=args)

    try:
        push_pkgbuild_to_local_aur_repo()
    except ConfigError as error:
        return str(error)

    return None


if __name__ == "__main__":
    if exit_value := main():
        sys.exit(exit_value)
