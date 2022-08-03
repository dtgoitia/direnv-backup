#!/usr/bin/env python

import argparse
import enum
import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SemVer:
    mayor: int
    minor: int
    patch: int


@dataclass
class Pkgbuild:
    pkgver: str
    pkgrel: str


class SemVerBumpType(enum.Enum):
    mayor = 0
    minor = 1
    patch = 2


bump_type_options = "/".join([x.name for x in SemVerBumpType])


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "bump_type",
        type=str,
        help=f"Bump type: {bump_type_options}",
    )
    args = parser.parse_args()
    return args


def find_pkgbuild_path() -> Path:
    ...


def read_current_version(raw: str) -> SemVer:
    pkgver_line = next(line for line in raw.split("\n") if "pkgname" in line)
    _, raw_version = pkgver_line.split("=")
    raw_mayor, raw_minor, raw_patch = raw_version.split(".")
    semver = SemVer(
        mayor=int(raw_mayor),
        minor=int(raw_minor),
        patch=int(raw_patch),
    )
    return semver


def calculate_new_version(current: SemVer, bump_type: SemVerBumpType) -> SemVer:
    if bump_type == SemVerBumpType.mayor:
        return SemVer(
            mayor=current.mayor + 1,
            minor=0,
            patch=0,
        )

    if bump_type == SemVerBumpType.minor:
        return SemVer(
            mayor=current.mayor,
            minor=current.minor + 1,
            patch=0,
        )

    if bump_type == SemVerBumpType.patch:
        return SemVer(
            mayor=current.mayor,
            minor=current.minor,
            patch=current.patch + 1,
        )

    raise Exception("Unexpected")


def bump_version(bump_type: SemVerBumpType) -> None:
    pkgbuild_path = find_pkgbuild_path()

    raw_pkgbuild = pkgbuild_path.read_text()

    current_version = read_current_version(raw=raw_pkgbuild)
    new_version = calculate_new_version(current=current_version, bump_type=bump_type)
    raise NotImplementedError("TODO")
    print(new_version)

    # TODO: update PKGBUILD file

    # TODO: add tag in master


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    arguments = parse_arguments()

    bump_type = SemVerBumpType[arguments.bump_type]

    bump_version(bump_type=bump_type)
