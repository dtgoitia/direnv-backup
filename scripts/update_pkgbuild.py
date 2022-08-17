#!/usr/bin/env python

import argparse
import enum
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

logger = logging.getLogger(__name__)

LOCAL_AUR_REPO_DIR_ENVVAR_NAME = "LOCAL_AUR_REPO_DIR"


@dataclass(frozen=True)
class SemVer:
    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


RawPkgbuild = str
# @dataclass
# class RawPkgbuild:
#     pkgver: str
#     pkgrel: str


class SemVerBumpType(enum.Enum):
    major = 0
    minor = 1
    patch = 2


bump_type_options = ", ".join([x.name for x in SemVerBumpType])


def parse_arguments(args: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bump",
        type=str,
        help=f"Bump type: {bump_type_options}",
    )
    arguments = parser.parse_args(args)
    return arguments


class MissingEnvironmentVariable(Exception):
    ...


def find_pkgbuild_path() -> Path:
    envvar_name = LOCAL_AUR_REPO_DIR_ENVVAR_NAME
    if envvar_name not in os.environ:
        raise MissingEnvironmentVariable(f"Please set {envvar_name}")

    raw = os.environ[envvar_name]
    local_aur_repo_dir = Path(raw).expanduser()

    if not local_aur_repo_dir.exists():
        raise ValueError(
            f"The {envvar_name} environment variable points to a path that does not"
            f" exist: {local_aur_repo_dir}"
        )

    if not local_aur_repo_dir.is_dir():
        raise ValueError(
            f"The {envvar_name} environment variable points to a path that is not a"
            f" directory: {local_aur_repo_dir}"
        )

    pkgbuild_path = local_aur_repo_dir / "PKGBUILD"

    return pkgbuild_path


def read_current_version(raw: str) -> SemVer:
    pkgver_line = next(line for line in raw.split("\n") if "pkgver" in line)
    _, raw_version = pkgver_line.split("=")
    raw_mayor, raw_minor, raw_patch = raw_version.split(".")
    semver = SemVer(
        major=int(raw_mayor),
        minor=int(raw_minor),
        patch=int(raw_patch),
    )
    return semver


def calculate_new_version(current: SemVer, bump_type: SemVerBumpType) -> SemVer:
    if bump_type == SemVerBumpType.major:
        return SemVer(
            major=current.major + 1,
            minor=0,
            patch=0,
        )

    if bump_type == SemVerBumpType.minor:
        return SemVer(
            major=current.major,
            minor=current.minor + 1,
            patch=0,
        )

    if bump_type == SemVerBumpType.patch:
        return SemVer(
            major=current.major,
            minor=current.minor,
            patch=current.patch + 1,
        )

    raise Exception("Unexpected")


def _replace_line(
    *,
    pkgbuild: RawPkgbuild,
    starting_with: str,
    new_value: str,
) -> RawPkgbuild:
    new_lines: list[str] = []

    for line in pkgbuild.split("\n"):
        if line.startswith(starting_with):
            line = f"{starting_with}={new_value}"
        new_lines.append(line)

    updated_pkgbuild = "\n".join(new_lines)
    return updated_pkgbuild


def replace_version(old: RawPkgbuild, version: SemVer) -> RawPkgbuild:
    return _replace_line(pkgbuild=old, starting_with="pkgver", new_value=str(version))


def bump_version(pkgbuild: RawPkgbuild, bump_type: SemVerBumpType) -> RawPkgbuild:
    current_version = read_current_version(raw=pkgbuild)
    new_version = calculate_new_version(current=current_version, bump_type=bump_type)

    updated_pkgbuild = replace_version(old=pkgbuild, version=new_version)
    return updated_pkgbuild


class UnexpectedScenario(Exception):
    ...


def read_current_pkgrel(pkgbuild: RawPkgbuild) -> int:
    for line in pkgbuild.splitlines():
        if not line.startswith("pkgrel"):
            continue
        _, raw_pkgrel = line.strip().split("=")
        pkgrel = int(raw_pkgrel)
        return pkgrel

    raise UnexpectedScenario("You should have never reached this point in code")


def replace_pkgrel(old: RawPkgbuild, pkgrel: int) -> RawPkgbuild:
    return _replace_line(pkgbuild=old, starting_with="pkgrel", new_value=str(pkgrel))


def _update_pkgrel(pkgbuild: RawPkgbuild, func: Callable[[int], int]) -> RawPkgbuild:
    current_pkgrel = read_current_pkgrel(pkgbuild=pkgbuild)
    new_pkgrel = func(current_pkgrel)

    updated_pkgbuild = replace_pkgrel(old=pkgbuild, pkgrel=new_pkgrel)
    return updated_pkgbuild


def reset_pkgrel(pkgbuild: RawPkgbuild) -> RawPkgbuild:
    def _set_to_one(_: int) -> int:
        return 1

    return _update_pkgrel(pkgbuild=pkgbuild, func=_set_to_one)


def bump_pkgrel(pkgbuild: RawPkgbuild) -> RawPkgbuild:
    def _increment_by_one(current: int) -> int:
        return current + 1

    return _update_pkgrel(pkgbuild=pkgbuild, func=_increment_by_one)


def update_pkgbuild_cmd(args: list[str] | None = None) -> str | None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    arguments = parse_arguments(args=args)

    pkgbuild_path = find_pkgbuild_path()

    pkgbuild = pkgbuild_path.read_text()

    if arguments.bump:

        try:
            bump_type = SemVerBumpType[arguments.bump]
            updated_pkgbuild = bump_version(pkgbuild=pkgbuild, bump_type=bump_type)

            # Ensure that the pkgrel goes back to `1` after changing `pkgver`
            updated_pkgbuild = reset_pkgrel(pkgbuild=updated_pkgbuild)
        except KeyError:
            return (
                f"{arguments.bump!r} is not a valid bump type. Supported values:"
                f" {bump_type_options}"
            )
        except MissingEnvironmentVariable as error:
            return str(error)

    else:
        # The PKGBUILD has changed, but the `pkgver` remains the same. According to AUR
        # best practices, `pkgrel` should be incremented then.
        updated_pkgbuild = bump_pkgrel(pkgbuild=pkgbuild)
        ...

    pkgbuild_path.write_text(updated_pkgbuild)

    return None


if __name__ == "__main__":
    if exit_value := update_pkgbuild_cmd():
        sys.exit(exit_value)
