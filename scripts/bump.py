#!/usr/bin/env python

import argparse
import enum
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

LOCAL_AUR_REPO_DIR_ENVVAR_NAME = "LOCAL_AUR_REPO_DIR"


@dataclass(frozen=True)
class SemVer:
    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


@dataclass
class Pkgbuild:
    pkgver: str
    pkgrel: str


class SemVerBumpType(enum.Enum):
    major = 0
    minor = 1
    patch = 2


bump_type_options = ", ".join([x.name for x in SemVerBumpType])


def parse_arguments(args: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "bump_type",
        type=str,
        help=f"Bump type: {bump_type_options}",
    )
    args = parser.parse_args(args)
    return args


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


PkgbuildContent = str


def replace_version(old: PkgbuildContent, version: SemVer) -> PkgbuildContent:
    new: list[str] = []

    for line in old.split("\n"):
        if line.startswith("pkgver"):
            line = f"pkgver={version}"
        new.append(line)

    return "\n".join(new)


def bump_version(bump_type: SemVerBumpType) -> None:
    pkgbuild_path = find_pkgbuild_path()

    original_pkgbuild = pkgbuild_path.read_text()

    current_version = read_current_version(raw=original_pkgbuild)
    new_version = calculate_new_version(current=current_version, bump_type=bump_type)

    updated_pkgbuild = replace_version(old=original_pkgbuild, version=new_version)

    pkgbuild_path.write_text(updated_pkgbuild)

    # TODO: add tag in master


def main(args: list[str] | None = None) -> str | None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    arguments = parse_arguments(args=args)

    try:
        bump_type = SemVerBumpType[arguments.bump_type]
    except KeyError:
        return (
            f"{arguments.bump_type!r} is not a valid bump type. Supported values:"
            f" {bump_type_options}"
        )

    try:
        bump_version(bump_type=bump_type)
    except MissingEnvironmentVariable as error:
        return error


if __name__ == "__main__":
    if exit_value := main():
        sys.exit(exit_value)
