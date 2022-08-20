#!/usr/bin/env python

"""
Conceptually:
PKGBUILD version must follow repo version
repo version = pyproject.toml
git tags follow pyproject.toml

sources of truth:
    - version: pyproject.toml --> git tags
               pyproject.toml --> PKGBUILD
    - pkgrel: PKGBUILD (agnostic to repo)
    - pkgdesc: pyproject.toml --> PKGBUILD
    - checksum: PKGBUILD (agnostic to repo)
    - source: version --> pyproject.toml --> gittags
                          pyproject.toml --> PKGBUILD
"""
import argparse
import logging
import shutil
import sys

from devex.exceptions import MissingEnvironmentVariable
from devex.pkgbuild import (
    find_aur_pkgbuild_path,
    find_pkgbuild_path,
    generate_srcinfo,
    sync_pkg_metadata,
)
from devex.pyproject import find_pyproject_path
from devex.semver import SemVerBumpType

logger = logging.getLogger(__name__)


bump_type_options = ", ".join([x.name for x in SemVerBumpType])


def parse_arguments(args: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bump",
        type=str,
        help=f"Bump type: {bump_type_options}",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Show debug logs")
    arguments = parser.parse_args(args)
    return arguments


def update_pkgbuild_cmd(args: list[str] | None = None) -> str | None:
    arguments = parse_arguments(args=args)

    if arguments.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logging.basicConfig(level=log_level, format="%(message)s")

    pkgbuild_path = find_pkgbuild_path()
    pyproject_path = find_pyproject_path()

    action: None | SemVerBumpType = None
    if arguments.bump:
        try:
            bump_type = SemVerBumpType[arguments.bump]
            action = bump_type
        except KeyError:
            return (
                f"{arguments.bump!r} is not a valid bump type. Supported values:"
                f" {bump_type_options}"
            )
        except MissingEnvironmentVariable as error:
            return str(error)

    sync_pkg_metadata(
        pkgbuild_path=pkgbuild_path,
        pyproject_path=pyproject_path,
        action=action,
    )

    aur_pkgbuild_path = find_aur_pkgbuild_path()
    shutil.copy(src=pkgbuild_path, dst=aur_pkgbuild_path)

    logger.info("Generating .SRCINFO in aur local repo...")
    generate_srcinfo(aur_dir=aur_pkgbuild_path.parent)

    return None


if __name__ == "__main__":
    if exit_value := update_pkgbuild_cmd():
        sys.exit(exit_value)
