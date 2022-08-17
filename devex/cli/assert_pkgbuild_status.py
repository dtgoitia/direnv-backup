#!/usr/bin/env python

"""
ensure pyproject.toml version, last tag, and PKGBUILD version is aligned
ensure pyproject.toml description, and PKGBUILD pkgdesc is aligned
"""

import argparse
import logging
import sys

from devex.git import InvalidVersionInGitTag, NoGitTagsFound
from devex.pkgbuild import (
    find_aur_pkgbuild_path,
    find_pkgbuild_path,
    git_tag_and_pyproject_version_match,
    pkgbuild_and_local_aur_pkgbuild_match,
    pyproject_and_pkgbuild_match,
)
from devex.pyproject import find_pyproject_path

logger = logging.getLogger(__name__)


def parse_arguments(args: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true", help="Show debug logs")
    arguments = parser.parse_args(args)
    return arguments


def _assert() -> str | None:
    pyproject_path = find_pyproject_path()
    pyproject = pyproject_path.read_text()

    if not git_tag_and_pyproject_version_match(pyproject=pyproject):
        return "last git tag in master and pyproject.toml version are not aligned"

    pkgbuild_path = find_pkgbuild_path()
    pkgbuild = pkgbuild_path.read_text()

    if not pyproject_and_pkgbuild_match(pkgbuild=pkgbuild, pyproject=pyproject):
        return "pyproject.toml and PKGBUILD are not aligned"

    aur_pkgbuild_path = find_aur_pkgbuild_path()
    aur_pkgbuild = aur_pkgbuild_path.read_text()

    if not pkgbuild_and_local_aur_pkgbuild_match(
        pkgbuild=pkgbuild, aur_pkgbuild=aur_pkgbuild
    ):
        return "PKGBUILD and local AUR repo PKGBUILD are not aligned"

    return None


def assert_pkgbuild_status_cmd(args: list[str] | None = None) -> str | None:
    arguments = parse_arguments(args=args)

    if arguments.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logging.basicConfig(level=log_level, format="%(message)s")

    try:
        mismatch_found = _assert()
        if not mismatch_found:
            logger.info("All files aligned :)")

        return mismatch_found

    except NoGitTagsFound:
        return "no git tags found"
    except (InvalidVersionInGitTag,) as error:
        return str(error)


if __name__ == "__main__":
    if exit_value := assert_pkgbuild_status_cmd():
        sys.exit(exit_value)
